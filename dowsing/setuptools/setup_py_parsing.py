"""
This is mostly compatible with pkginfo's metadata classes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import libcst as cst
from libcst.metadata import (
    ParentNodeProvider,
    PositionProvider,
    QualifiedNameProvider,
    ScopeProvider,
)

from ..types import Distribution
from .setup_and_metadata import SETUP_ARGS

LOG = logging.getLogger(__name__)


def from_setup_py(path: Path, markers: Dict[str, Any]) -> Distribution:
    """
    Reads setup.py (and possibly some imports).

    Will not actually "run" the code but will evaluate some conditions based on
    the markers you provide, since much real-world setup.py checks things like
    version, platform, or even `sys.argv` to come up with what it passes to
    `setup()`.

    There should be some other class to read pyproject.toml.

    This needs a path because one day it may need to read other files alongside
    it.
    """

    # TODO: This does not take care of encodings or py2 syntax.
    module = cst.parse_module((path / "setup.py").read_text())

    # TODO: This is not a good example of LibCST integration.  The right way to
    # do this is with a scope provider and transformer, and perhaps multiple
    # passes.

    d = Distribution()
    d.metadata_version = "2.1"

    analyzer = SetupCallAnalyzer()
    wrapper = cst.MetadataWrapper(module)
    wrapper.visit(analyzer)
    if not analyzer.found_setup:
        raise SyntaxError("No simple setup call found")

    for field in SETUP_ARGS:
        name = field.get_distribution_key()
        if not hasattr(d, name):
            continue

        if field.keyword in analyzer.saved_args:
            v = analyzer.saved_args[field.keyword]
            if isinstance(v, Literal):
                setattr(d, name, v.value)
            else:
                LOG.warning(f"Want to save {field.keyword} but is {type(v)}")

    return d


@dataclass
class TooComplicated:
    reason: str


@dataclass
class Sometimes:
    # TODO list of 'when' and 'else'
    pass


@dataclass
class Literal:
    value: Any
    cst_node: Optional[cst.CSTNode]


@dataclass
class FindPackages:
    where: Any = None
    exclude: Any = None
    include: Any = None


class FileReference:
    def __init__(self, filename: str) -> None:
        self.filename = filename


class SetupCallTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (ScopeProvider, ParentNodeProvider, QualifiedNameProvider)

    def __init__(
        self,
        call_node: cst.CSTNode,
        keywords_to_change: Dict[str, Optional[cst.CSTNode]],
    ) -> None:
        self.call_node = call_node
        self.keywords_to_change = keywords_to_change

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        if original_node == self.call_node:
            new_args = []
            for arg in updated_node.args:
                if isinstance(arg.keyword, cst.Name):
                    if arg.keyword.value in self.keywords_to_change:
                        value = self.keywords_to_change[arg.keyword.value]
                        if value is not None:
                            new_args.append(arg.with_changes(value=value))
                        # else don't append
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            return updated_node.with_changes(args=new_args)

        return updated_node


class SetupCallAnalyzer(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (
        ScopeProvider,
        ParentNodeProvider,
        QualifiedNameProvider,
        PositionProvider,
    )

    # TODO names resulting from other than 'from setuptools import setup'
    # TODO wrapper funcs that modify args
    # TODO **args
    def __init__(self) -> None:
        super().__init__()
        # TODO Union[TooComplicated, Sometimes, Literal, FileReference]
        self.saved_args: Dict[str, Any] = {}
        self.found_setup = False
        self.setup_node: Optional[cst.CSTNode] = None

    def visit_Call(self, node: cst.Call) -> Optional[bool]:
        names = self.get_metadata(QualifiedNameProvider, node)
        # TODO sometimes there is more than one setup call, we might
        # prioritize/merge...
        if any(
            q.name
            in (
                "setuptools.setup",
                "distutils.core.setup",
                "setup3lib",
                "skbuild.setup",
            )
            for q in names
        ):
            self.found_setup = True
            self.setup_node = node
            scope = self.get_metadata(ScopeProvider, node)
            for arg in node.args:
                # TODO **kwargs
                if isinstance(arg.keyword, cst.Name):
                    key = arg.keyword.value
                    value = self.evaluate_in_scope(arg.value, scope)
                    self.saved_args[key] = Literal(value, arg)
                elif arg.star == "**":
                    # kwargs
                    d = self.evaluate_in_scope(arg.value, scope)
                    if isinstance(d, dict):
                        for k, v in d.items():
                            self.saved_args[k] = Literal(v, None)
                    else:
                        # GRR
                        pass
                else:
                    raise ValueError(repr(arg))

            return False

        return None

    BOOL_NAMES = {"True": True, "False": False, "None": None}
    PRETEND_ARGV = ["setup.py", "bdist_wheel"]

    def evaluate_in_scope(
        self, item: cst.CSTNode, scope: Any, target_line: int = 0
    ) -> Any:
        qnames = self.get_metadata(QualifiedNameProvider, item)

        if isinstance(item, cst.SimpleString):
            return item.evaluated_value
        elif isinstance(item, (cst.Integer, cst.Float)):
            return int(item.value)
        elif isinstance(item, cst.Name) and item.value in self.BOOL_NAMES:
            return self.BOOL_NAMES[item.value]
        elif isinstance(item, cst.Name):
            name = item.value
            assignments = scope[name]
            assignment_nodes = sorted(
                (
                    (self.get_metadata(PositionProvider, a.node).start.line, a.node)
                    for a in assignments
                    if a.node
                ),
                reverse=True,
            )
            # Walk assignments from bottom to top, evaluating them recursively.
            for lineno, node in assignment_nodes:

                # When recursing, only look at assignments above the "target line".
                if target_line and lineno >= target_line:
                    continue

                # Assign(
                #   targets=[AssignTarget(target=Name(value="v"))],
                #   value=SimpleString(value="'x'"),
                # )
                #
                # AugAssign(
                #   target=Name(value="v"),
                #   operator=AddAssign(...),
                #   value=SimpleString(value="'x'"),
                # )
                #
                # TODO or an import...
                # TODO builtins have BuiltinAssignment

                try:
                    if node:
                        parent = self.get_metadata(ParentNodeProvider, node)
                        if parent:
                            gp = self.get_metadata(ParentNodeProvider, parent)
                        else:
                            raise KeyError
                    else:
                        raise KeyError
                except (KeyError, AttributeError):
                    continue

                try:
                    scope = self.get_metadata(ScopeProvider, gp)
                except KeyError:
                    # module scope isn't in the dict
                    continue

                # This presumes a single assignment
                if isinstance(gp, cst.Assign) and len(gp.targets) == 1:
                    result = self.evaluate_in_scope(gp.value, scope, lineno)
                elif isinstance(parent, cst.AugAssign):
                    result = self.evaluate_in_scope(parent, scope, lineno)
                else:
                    # too complicated?
                    continue

                # keep trying assignments until we get something other than ??
                if result != "??":
                    return result

            # give up
            return "??"
        elif isinstance(item, (cst.Tuple, cst.List)):
            lst = []
            for el in item.elements:
                lst.append(
                    self.evaluate_in_scope(
                        el.value,
                        self.get_metadata(ScopeProvider, el),
                        target_line,
                    )
                )
            if isinstance(item, cst.Tuple):
                return tuple(lst)
            else:
                return lst
        elif isinstance(item, cst.Call) and any(
            q.name == "setuptools.find_packages" for q in qnames
        ):
            default_args = [".", (), ("*",)]
            args = default_args.copy()

            names = ("where", "exclude", "include")
            i = 0
            for arg in item.args:
                if isinstance(arg.keyword, cst.Name):
                    args[names.index(arg.keyword.value)] = self.evaluate_in_scope(
                        arg.value, scope, target_line
                    )
                else:
                    args[i] = self.evaluate_in_scope(arg.value, scope, target_line)
                    i += 1

            # TODO clear ones that are still default
            return FindPackages(*args)
        elif (
            isinstance(item, cst.Call)
            and isinstance(item.func, cst.Name)
            and item.func.value == "dict"
        ):
            d = {}
            for arg in item.args:
                if isinstance(arg.keyword, cst.Name):
                    d[arg.keyword.value] = self.evaluate_in_scope(
                        arg.value, scope, target_line
                    )
                # TODO something with **kwargs
            return d
        elif isinstance(item, cst.Dict):
            d = {}
            for el2 in item.elements:
                if isinstance(el2, cst.DictElement):
                    d[self.evaluate_in_scope(el2.key, scope)] = self.evaluate_in_scope(
                        el2.value, scope, target_line
                    )
            return d
        elif isinstance(item, cst.Subscript):
            lhs = self.evaluate_in_scope(item.value, scope, target_line)
            if isinstance(lhs, str):
                # A "??" entry, propagate
                return "??"

            # TODO: Figure out why this is Sequence
            if isinstance(item.slice[0].slice, cst.Index):
                rhs = self.evaluate_in_scope(
                    item.slice[0].slice.value, scope, target_line
                )
                try:
                    if isinstance(lhs, dict):
                        return lhs.get(rhs, "??")
                    else:
                        return lhs[rhs]
                except Exception:
                    return "??"

            else:
                # LOG.warning(f"Omit2 {type(item.slice[0].slice)!r}")
                return "??"
        elif isinstance(item, cst.BinaryOperation):
            lhs = self.evaluate_in_scope(item.left, scope, target_line)
            rhs = self.evaluate_in_scope(item.right, scope, target_line)
            if lhs == "??" or rhs == "??":
                return "??"
            if isinstance(item.operator, cst.Add):
                try:
                    return lhs + rhs
                except Exception:
                    return "??"
            else:
                return "??"
        elif isinstance(item, cst.AugAssign):
            lhs = self.evaluate_in_scope(item.target, scope, target_line)
            rhs = self.evaluate_in_scope(item.value, scope, target_line)
            if lhs == "??" or rhs == "??":
                return "??"
            if isinstance(item.operator, cst.AddAssign):
                try:
                    return lhs + rhs
                except Exception:
                    return "??"
            else:
                return "??"
        else:
            # LOG.warning(f"Omit1 {type(item)!r}")
            return "??"

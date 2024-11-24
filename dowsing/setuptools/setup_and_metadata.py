from .types import (
    BoolWriter,
    ConfigField,
    DictWriter,
    ListCommaWriter,
    ListCommaWriterCompat,
    ListSemiWriter,
    Metadata,
    SectionWriter,
    SetupCfg,
)

# Not all of these are in the resulting metadata, but if defined for use in
# setup.py or setup.cfg, I include them here to be able to translate between
# them.
# For a dry description of the current state, including version added, see
# https://packaging.python.org/specifications/core-metadata/
#
# Some of these are not yet implemented, mainly because they're uncommon and of
# limited use for what I need.  Pull requests welcome.
#
# The examples are intended to be used with some kind of validation testing, but
# it's very slow (perhaps 300mS) and many of the fields are validated.  I wanted
# unique data in each to tell them apart, but random wouldn't work (especially
# for versions).
SETUP_ARGS = [
    # Metadata 1.0; This ordering is the same as _METHOD_BASENAMES in
    # distutils/dist.py which handles an older version of the metadata.
    # https://docs.python.org/3/distutils/setupscript.html#additional-meta-data
    #
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#metadata
    # does a good job telling you whether it's metadata/options in setup.cfg,
    # but doesn't really tell you what they do or what the metadata keys are or
    # what metadata version they correspond to.
    ConfigField("name", SetupCfg("metadata", "name"), Metadata("Name")),
    ConfigField(
        "version",
        SetupCfg("metadata", "version"),
        Metadata("Version"),
        sample_value="1.5.1",
    ),
    ConfigField("author", SetupCfg("metadata", "author"), Metadata("Author")),
    ConfigField(
        "author_email",
        SetupCfg("metadata", "author_email"),
        Metadata("Author-email"),
    ),
    ConfigField(
        "license",
        SetupCfg("metadata", "license"),
        Metadata("License"),
    ),
    # TODO licence (alternate spelling)
    # TODO license_file, license_files (setuptools-specific)
    ConfigField("url", SetupCfg("metadata", "url"), Metadata("Home-page")),
    ConfigField(
        "description",
        SetupCfg("metadata", "description"),
        Metadata("Summary"),
    ),
    ConfigField(
        "long_description",
        SetupCfg("metadata", "long_description"),
        Metadata("Description"),
    ),  # but special because it can exist as the body
    ConfigField(
        "keywords",
        SetupCfg("metadata", "keywords", writer_cls=ListCommaWriterCompat),
        Metadata("Keywords"),
        sample_value=["abc", "def"],
    ),  # but not repeated
    # platforms
    # fullname
    # contact
    # contact_email
    # Metadata 1.1, supported by distutils
    # provides
    # requires
    # obsoletes
    ConfigField(
        "classifiers",
        SetupCfg("metadata", "classifiers", writer_cls=ListSemiWriter),
        Metadata("Classifier", repeated=True),
        sample_value=[
            "License :: OSI Approved :: MIT License",
            "Intended Audience :: Developers",
        ],
        distribution_key="classifiers",
    ),
    # download_url
    # Metadata 1.1
    # supported-platform (binary only?)
    # Metadata 1.2, half-supported by distutils but not written in PKG-INFO
    ConfigField(
        "maintainer", SetupCfg("metadata", "maintainer"), Metadata("Maintainer")
    ),
    ConfigField(
        "maintainer_email",
        SetupCfg("metadata", "maintainer_email"),
        Metadata("Maintainer-email"),
    ),
    # Metadata 1.2, not at all supported by distutils
    ConfigField(
        "python_requires",
        SetupCfg("options", "python_requires"),  # also requires_python :/
        Metadata("Requires-Python"),
        sample_value="<4.0",
    ),
    # requires_external
    # project_url -> dict
    ConfigField(
        "project_urls",
        SetupCfg("metadata", "project_urls", writer_cls=DictWriter),
        Metadata("Project-URL"),
        sample_value={"Bugtracker": "http://example.com"},
        distribution_key="project_urls",
    ),
    # provides_dist (rarely used)
    # obsoletes_dist (rarely used)
    # Metadata 2.1
    # text/plain, text/x-rst, text/markdown
    # This allows charset and variant (for markdown, GFM or CommonMark)
    ConfigField(
        "long_description_content_type",
        SetupCfg("metadata", "long_description_content_type"),
        Metadata("Description-Content-Type"),
    ),
    # provides_extra
    # Not written to PKG-INFO
    # [options]
    ConfigField(
        "zip_safe",
        SetupCfg("options", "zip_safe", writer_cls=BoolWriter),
        sample_value=True,
    ),
    ConfigField(
        "setup_requires",
        SetupCfg("options", "setup_requires", writer_cls=ListSemiWriter),
        sample_value=["setuptools"],
    ),
    ConfigField(
        "install_requires",
        SetupCfg("options", "install_requires", writer_cls=ListCommaWriter),
        Metadata("Requires-Dist", repeated=True),
        sample_value=["a", "b ; python_version < '3'"],
        distribution_key="requires_dist",
    ),
    ConfigField(
        "tests_require",
        SetupCfg("options", "tests_require", writer_cls=ListSemiWriter),
        sample_value=["pytest"],
    ),
    ConfigField(
        "include_package_data",
        SetupCfg("options", "include_package_data", writer_cls=BoolWriter),
        sample_value=True,
    ),
    #
    ConfigField(
        "extras_require",
        SetupCfg("options.extras_require", "UNUSED", writer_cls=SectionWriter),
        sample_value=None,
    ),
    # use_2to3
    # use_2to3_fixers list-comma
    # use_2to3_exclude_fixers list-comma
    # convert_2to3_doctests list-comma
    ConfigField(
        "scripts",
        SetupCfg("options", "scripts", writer_cls=ListCommaWriter),
        sample_value=None,
    ),
    # eager_resources list-comma
    # dependency_links list-comma
    ConfigField(
        "packages",
        SetupCfg("options", "packages", writer_cls=ListCommaWriter),
        sample_value=["a"],
    ),
    ConfigField(
        "package_dir",
        SetupCfg("options", "package_dir", writer_cls=DictWriter),
        sample_value=None,
    ),
    ConfigField(
        "package_data",
        SetupCfg("options.package_data", "UNUSED", writer_cls=SectionWriter),
        sample_value=None,  # {"foo": ["py.typed"]},
    ),
    # package_data (section)
    # exclude_package_data (section)
    ConfigField(
        "namespace_packages",
        SetupCfg("options", "namespace_packages", writer_cls=ListCommaWriter),
        sample_value=None,  # ["foo", "bar"],
    ),
    ConfigField(
        "py_modules",
        SetupCfg("options", "py_modules", writer_cls=ListCommaWriter),
        sample_value=None,
    ),
    ConfigField(
        "data_files",
        SetupCfg("options.data_files", "UNUSED", writer_cls=SectionWriter),
        sample_value=None,
    ),
    ConfigField(
        "entry_points",
        SetupCfg("options.entry_points", "UNUSED", writer_cls=SectionWriter),
        sample_value=None,
    ),
    #
    # Documented, but not in the table...
    ConfigField("test_suite", SetupCfg("options", "test_suite")),
    ConfigField("test_loader", SetupCfg("options", "test_loader")),
    #
    # FindPackages
    ConfigField(
        "find_packages_where",
        SetupCfg("options.packages.find", "where"),
        sample_value=None,
    ),
    ConfigField(
        "find_packages_exclude",
        SetupCfg("options.packages.find", "exclude", writer_cls=ListCommaWriter),
        sample_value=None,
    ),
    ConfigField(
        "find_packages_include",
        SetupCfg("options.packages.find", "include", writer_cls=ListCommaWriter),
        sample_value=None,
    ),
    ConfigField(
        "pbr",
        SetupCfg("--unused--", "--unused--"),
        sample_value=None,
    ),
    ConfigField(
        "pbr__files__packages_root",
        SetupCfg("files", "packages_root"),
        sample_value=None,
    ),
    ConfigField(
        "pbr__files__packages",
        SetupCfg("files", "packages", writer_cls=ListCommaWriter),
        sample_value=None,
    ),
]

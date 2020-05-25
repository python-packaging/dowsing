from .flit import FlitReaderTest
from .setuptools import SetuptoolsReaderTest

__all__ = [
    "FlitReaderTest",
    "SetuptoolsReaderTest",
]

if __name__ == "__main__":
    import unittest

    unittest.main()

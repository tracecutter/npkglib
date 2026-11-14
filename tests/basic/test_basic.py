"""
npkglib.tests.basic.test_basic

INTERNAL

:copyright: Copyright (c) 2025 John Fogelin.
:license: MIT, see LICENSE for details.
"""


def test_version():
    import npkglib

    assert hasattr(npkglib, "__version__")

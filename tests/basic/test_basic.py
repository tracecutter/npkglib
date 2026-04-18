"""
pbox.tests.basic.test_basic

INTERNAL

:copyright: Copyright (c) 2025 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""


def test_version():
    import pbox

    assert hasattr(pbox, "__version__")

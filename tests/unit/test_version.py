import treqna
from treqna._version import __version__


def test_version_defined() -> None:
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_package_exports_version() -> None:
    assert treqna.__version__ == __version__


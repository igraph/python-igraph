from igraph.drawing.utils import FakeModule
from typing import Any

__all__ = ("find_cairo",)
__docformat__ = "restructuredtext en"


def find_cairo() -> Any:
    """Tries to import the ``cairo`` Python module if it is installed,
    also trying ``cairocffi`` (a drop-in replacement of ``cairo``).
    Returns a fake module if everything fails.
    """
    module_names = ["cairo", "cairocffi"]
    module = FakeModule("Plotting not available; please install pycairo or cairocffi")
    for module_name in module_names:
        try:
            module = __import__(module_name)
            break
        except ImportError:
            pass
    return module

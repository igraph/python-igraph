from igraph.drawing.utils import FakeModule
from typing import Any

__all__ = ("find_plotly", )


def find_plotly() -> Any:
    """Tries to import the ``plotly`` Python module if it is installed.
    Returns a fake module if everything fails.
    """
    try:
        import plotly

    except ImportError:
        plotly = FakeModule("You need to install plotly to use this functionality")

    return plotly

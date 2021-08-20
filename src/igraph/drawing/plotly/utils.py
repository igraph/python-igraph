from igraph.drawing.utils import FakeModule, Point
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


def format_path_step(code, point_or_points):
    """Format step in SVG path for plotly"""
    if isinstance(point_or_points, Point):
        points = [point_or_points]
    else:
        points = point_or_points

    step = f" {code}"
    for (x, y) in points:
        step += f" {x},{y}"
    return step


# Adapted from https://community.plotly.com/t/arc-shape-with-path/7205/3
def format_arc(center, radius_x, radius_y, theta1, theta2, N=100, closed=False):
    """Approximation of an SVG-style arc

    NOTE: plotly does not currently support the native SVG "A/a" commands"""
    import math

    xc, yc = center
    dt = 1.0 * (theta2 - theta1)
    t = [theta1 + dt * i / (N-1) for i in range(N)]
    x = [xc + radius_x * math.cos(i) for i in t]
    y = [yc + radius_y * math.sin(i) for i in t]
    path = f'M {x[0]}, {y[0]}'
    for k in range(1, len(t)):
        path += f'L{x[k]}, {y[k]}'
    if closed:
        path += ' Z'
    return path


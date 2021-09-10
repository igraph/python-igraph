# Functions adapted from matplotlib.testing. Credit for the original functions
# goes to the amazing folks over at matplotlib.
from pathlib import Path
import sys
import inspect
import functools

try:
    import matplotlib
    from matplotlib.testing.decorators import _ImageComparisonBase
    from matplotlib.testing.compare import comparable_formats
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib = None

__all__ = ("find_image_comparison",)


def find_image_comparison():
    def dummy_comparison(*args, **kwargs):
        return lambda *args, **kwargs: None

    if matplotlib is None:
        return dummy_comparison
    return image_comparison


# NOTE: Parametrizing this requires pytest (see matplotlib's test suite)
_default_extension = "pdf"


def _unittest_image_comparison(
    baseline_images, tol, remove_text, savefig_kwargs, style
):
    """
    Decorate function with image comparison for unittest.
    This function creates a decorator that wraps a figure-generating function
    with image comparison code.
    """
    import unittest

    def decorator(func):
        old_sig = inspect.signature(func)

        @functools.wraps(func)
        @matplotlib.style.context(style)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True

            img = _ImageComparisonBase(
                func, tol=tol, remove_text=remove_text, savefig_kwargs=savefig_kwargs
            )
            matplotlib.testing.set_font_settings_for_testing()

            func(*args, **kwargs)

            assert len(plt.get_fignums()) == len(
                baseline_images
            ), "Test generated {} images but there are {} baseline images".format(
                len(plt.get_fignums()), len(baseline_images)
            )
            for idx, baseline in enumerate(baseline_images):
                img.compare(idx, baseline, _default_extension, _lock=False)

        parameters = list(old_sig.parameters.values())
        new_sig = old_sig.replace(parameters=parameters)
        wrapper.__signature__ = new_sig

        return wrapper

    return decorator


def image_comparison(
    baseline_images,
    tol=0,
    remove_text=False,
    savefig_kwarg=None,
    # Default of mpl_test_settings fixture and cleanup too.
    style=("classic", "_classic_test_patch"),
):
    """
    Compare images generated by the test with those specified in
    *baseline_images*, which must correspond, else an `ImageComparisonFailure`
    exception will be raised.
    Parameters
    ----------
    baseline_images : list or None
        A list of strings specifying the names of the images generated by
        calls to `.Figure.savefig`.
        If *None*, the test function must use the ``baseline_images`` fixture,
        either as a parameter or with `pytest.mark.usefixtures`. This value is
        only allowed when using pytest.
    tol : float, default: 0
        The RMS threshold above which the test is considered failed.
        Due to expected small differences in floating-point calculations, on
        32-bit systems an additional 0.06 is added to this threshold.
    remove_text : bool
        Remove the title and tick text from the figure before comparison.  This
        is useful to make the baseline images independent of variations in text
        rendering between different versions of FreeType.
        This does not remove other, more deliberate, text, such as legends and
        annotations.
    savefig_kwarg : dict
        Optional arguments that are passed to the savefig method.
    style : str, dict, or list
        The optional style(s) to apply to the image test. The test itself
        can also apply additional styles if desired. Defaults to ``["classic",
        "_classic_test_patch"]``.
    """
    if savefig_kwarg is None:
        savefig_kwarg = dict()  # default no kwargs to savefig
    if sys.maxsize <= 2 ** 32:
        tol += 0.06
    return _unittest_image_comparison(
        baseline_images=baseline_images,
        tol=tol,
        remove_text=remove_text,
        savefig_kwargs=savefig_kwarg,
        style=style,
    )

# Functions adapted from matplotlib.testing. Credit for the original functions
# goes to the amazing folks over at matplotlib.
from pathlib import Path
import os
import sys
import inspect
import functools

try:
    import plotly
except ImportError:
    plotly = None

__all__ = ("find_image_comparison",)


def find_image_comparison():
    def dummy_comparison(*args, **kwargs):
        return lambda *args, **kwargs: None

    if plotly is None:
        return dummy_comparison
    return image_comparison


# NOTE: Parametrizing this requires pytest (see matplotlib's test suite)
_default_extension = "svg"


def _load_baseline_image(filename, fmt):
    import json

    if fmt == "json":
        with open(filename, "rt") as handle:
            image = json.load(handle)
        return image

    raise NotImplementedError(f"Image format {fmt} not implemented yet")


def _load_baseline_images(filenames, fmt="json"):
    baseline_folder = Path(__file__).parent / "baseline_images"

    images = []
    for fn in filenames:
        fn_abs = baseline_folder / f"{fn}.{fmt}"
        image = _load_baseline_image(fn_abs, fmt)
        images.append(image)
    return images


def _store_result_image_json(fig, result_fn):
    import os
    import json

    os.makedirs(result_fn.parent, exist_ok=True)

    # This produces a Python dict that's JSON compatible. We print it to a
    # file in a way that is easy to diff and lists properties in a predictable
    # order
    fig_json = fig.to_dict()
    with open(result_fn, "wt") as handle:
        json.dump(fig_json, handle, indent=2, sort_keys=True)


def _store_result_image(image, filename, fmt="json"):
    result_folder = Path("result_images") / 'plotly'
    result_fn = result_folder / (filename + f".{fmt}")

    if fmt == "json":
        return _store_result_image_json(image, result_fn)

    raise NotImplementedError(f"Image format {fmt} not implemented yet")


def _compare_image_json(baseline, fig):
    return baseline == fig.to_dict()


def compare_image(baseline, fig, tol=0, fmt="json"):
    if fmt == "json":
        return _compare_image_json(baseline, fig)

    raise NotImplementedError(f"Image format {fmt} not implemented yet")


def _unittest_image_comparison(
    baseline_images,
    tol,
    remove_text,
):
    """
    Decorate function with image comparison for unittest.
    This function creates a decorator that wraps a figure-generating function
    with image comparison code.
    """
    import unittest

    def decorator(func):
        old_sig = inspect.signature(func)

        # This saves us to lift name, docstring, etc.
        # NOTE: not super sure why we need this additional layer of wrapping
        # seems to have to do with stripping arguments from the test function
        # probably redundant in this adaptation
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # Three steps:
            # 1. run the function and store the results
            figs = func(*args, **kwargs)
            if isinstance(figs, plotly.graph_objects.Figure):
                figs = [figs]

            # Store images (used to bootstrap new tests)
            for fig, image_file in zip(figs, baseline_images):
                _store_result_image(fig, image_file)

            assert len(baseline_images) == len(
                figs
            ), "Test generated {} images but there are {} baseline images".format(
                len(figs), len(baseline_images)
            )

            # 2. load the control images
            baselines = _load_baseline_images(baseline_images)

            # 3. compare them one by one
            for i, (baseline, fig) in enumerate(zip(baselines, figs)):
                if remove_text:
                    # TODO
                    pass

                # FIXME: what does tolerance mean for json?
                res = compare_image(baseline, fig, tol)
                assert res, f"Image {i} does not match the corresponding baseline"

            return figs

        parameters = list(old_sig.parameters.values())
        new_sig = old_sig.replace(parameters=parameters)
        wrapper.__signature__ = new_sig

        return wrapper

    return decorator


def image_comparison(
    baseline_images,
    tol=0,
    remove_text=False,
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
    if sys.maxsize <= 2 ** 32:
        tol += 0.06
    return _unittest_image_comparison(
        baseline_images=baseline_images,
        tol=tol,
        remove_text=remove_text,
    )

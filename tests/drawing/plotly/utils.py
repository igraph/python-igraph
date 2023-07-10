# Functions adapted from matplotlib.testing. Credit for the original functions
# goes to the amazing folks over at matplotlib.
from pathlib import Path

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


def _compare_image_json(baseline, fig, tol=0.001):
    '''This function compares the two JSON dictionaries within some tolerance'''
    def is_coords(path_element):
        if ',' not in path_element:
            return False
        coords = path_element.split(',')
        for coord in coords:
            try:
                float(coord)
            except ValueError:
                return False
        return True

    def same_coords(path_elem1, path_elem2, tol):
        coords1 = [float(x) for x in path_elem1.split(',')]
        coords2 = [float(x) for x in path_elem2.split(',')]
        for coord1, coord2 in zip(coords1, coords2):
            if abs(coord1 - coord2) > tol:
                return False
        return True

    # Fig has two keys, 'data' and 'layout'
    figd = fig.to_dict()
    # 'data' has a list of dots and lines. The order is required to match
    if len(baseline['data']) != len(figd['data']):
        return False
    for stroke1, stroke2 in zip(baseline['data'], figd['data']):
        # Some properties are strings, no tolerance
        for prop in ['fillcolor', 'mode', 'type']:
            if (prop in stroke1) != (prop in stroke2):
                return False
            if prop not in stroke1:
                continue
            if stroke1[prop] != stroke2[prop]:
                return False

        # Other properties are numeric, recast as float and use tolerance
        for prop in ['x', 'y']:
            if (prop in stroke1) != (prop in stroke2):
                return False
            if prop not in stroke1:
                continue
            if len(stroke1[prop]) != len(stroke2[prop]):
                return False
            for prop_elem1, prop_elem2 in zip(stroke1[prop], stroke2[prop]):
                if abs(float(prop_elem1) - float(prop_elem2)) > tol:
                    return False

    # 'layout' has a dict of various things, some of which should be identical
    if sorted(baseline['layout'].keys()) != sorted(figd['layout'].keys()):
        return False
    if baseline['layout']['xaxis'] != baseline['layout']['xaxis']:
        return False
    if baseline['layout']['yaxis'] != baseline['layout']['yaxis']:
        return False
    # 'shapes' is a list of shape, should be the same up to tolerance
    if len(baseline['layout']['shapes']) != len(figd['layout']['shapes']):
        return False
    for shape1, shape2 in zip(baseline['layout']['shapes'], figd['layout']['shapes']):
        if sorted(shape1.keys()) != sorted(shape2.keys()):
            return False
        if shape1['type'] != shape2['type']:
            return False
        if 'line' in shape1:
            if shape1['line']['color'] != shape2['line']['color']:
                return False
            if ('width' in shape1['line']) != ('width' in shape2['line']):
                return False
            if 'width' in shape1['line']:
                w1 = float(shape1['line']['width'])
                w2 = float(shape2['line']['width'])
                if abs(w1 - w2) > tol:
                    return False

        if 'path' in shape1:
            # SVG path
            path1, path2 = shape1['path'].split(), shape2['path'].split()
            if len(path1) != len(path2):
                return False
            for path_elem1, path_elem2 in zip(path1, path2):
                is_coords1 = is_coords(path_elem1)
                is_coords2 = is_coords(path_elem2)
                if is_coords1 != is_coords2:
                    return False
                if is_coords1:
                    if not same_coords(path_elem1, path_elem2, tol):
                        return False

    # 'layout': skipping that for now, seems mostly plotly internals

    return True


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

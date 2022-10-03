import gc
import sys

from pytest import fixture


@fixture(autouse=True)
def check_refcounts():
    objs = [True, False]
    gc.collect()
    refs = {}
    for obj in objs:
        refs[obj] = sys.getrefcount(obj)
    gc.collect()

    yield

    gc.collect()
    for obj in objs:
        current = sys.getrefcount(obj)
        if refs[obj] - current > 7:
            raise RuntimeError(f"reference count of {obj} decreased from {refs[obj]} to {current}")

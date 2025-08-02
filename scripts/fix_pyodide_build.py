#!/usr/bin/env python3
import pyodide_build

from pathlib import Path
from urllib.request import urlretrieve

target_dir = (
    Path(pyodide_build.__file__).parent / "tools" / "cmake" / "Modules" / "Platform"
)
target_dir.mkdir(exist_ok=True, parents=True)

target_file = target_dir / "Emscripten.cmake"
if not target_file.is_file():
    url = "https://raw.githubusercontent.com/pyodide/pyodide-build/main/pyodide_build/tools/cmake/Modules/Platform/Emscripten.cmake"
    urlretrieve(url, str(target_file))

FROM python:3.10.6-bullseye

SHELL ["/bin/bash", "-c"]

COPY setup.py.diff.txt /setup.py.diff

RUN set -ex \
	&& echo "Installing flex and bison" \	
	&& apt-get update \
	&& apt-get -y install flex bison \
	&& echo "Installing Emscripten" \
	&& git clone https://github.com/emscripten-core/emsdk.git \
	&& cd emsdk \
	&& ./emsdk install latest \
	&& ./emsdk activate latest \
	&& source "/emsdk/emsdk_env.sh" \
	&& cd .. \
	&& echo "Cloning igraph repositories" \
	&& git clone https://github.com/igraph/python-igraph.git \
	&& cd python-igraph/vendor/source \
	&& git clone https://github.com/igraph/igraph.git \
	&& cd ../.. \
	&& echo "Applying patch to setup.py" \
	&& git apply < /setup.py.diff \
	&& echo "Installing pyodide-build" \
	&& pip install pyodide-build \
	&& echo "Building igraph wheel" \
	&& pyodide build

TAG = igraph/manylinux

build-wheel:
	docker build -f docker/manylinux.docker -t $(TAG) .

copy-wheel:
	# copies the built wheels from the docker image to a local directory
	rm -rf docker/wheelhouse
	mkdir docker/wheelhouse
	docker run --user `id -u` -v `pwd`/docker/wheelhouse:/output $(TAG) sh -c "cp /wheelhouse/python_igraph*.*manylinux*.whl /output"

test-ubuntu: copy-wheel
	echo 'testing ubuntu'
	docker run -v `pwd`/docker/wheelhouse:/wheelhouse python:2 sh -c " \
		pip install python-igraph --no-index --find-links /wheelhouse; \
		python -c \"import igraph; print 'ok', igraph\"; \
	"

test-centos: copy-wheel
	echo 'testing centos'
	docker run -v `pwd`/docker/wheelhouse:/wheelhouse centos sh -c " \
		yum -y install epel-release; \
		yum -y install python-pip; \
		pip install -U pip; \
		pip install python-igraph --no-index --find-links /wheelhouse; \
		python -c \"import igraph; print igraph\"; \
	"

test-alpine: copy-wheel
	echo 'testing alpine'
	# todo: this is failing because it requires libm linked into the wheel
	docker run -v `pwd`/docker/wheelhouse:/wheelhouse python:2-alpine sh -c " \
		apk update; \
		apk add libxml2 libstdc++; \
		pip install python-igraph --no-index --find-links /wheelhouse; \
		python -c \"import igraph; print igraph\"; \
	"

# note: test-alpine not included because there's no libm available
test-wheel: test-ubuntu test-centos

.PHONY: build-wheel copy-wheel test-wheel

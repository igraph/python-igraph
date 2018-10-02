TAG = igraph/manylinux

build-wheel:
	docker build -f docker/manylinux.docker -t $(TAG) .

copy-wheel:
	rm -rf docker/wheelhouse
	mkdir docker/wheelhouse
	docker run --user `id -u` -v `pwd`/docker/wheelhouse:/output $(TAG) sh -c "cp /wheelhouse/*manylinux* /output"

.PHONY: build-wheel copy-wheel

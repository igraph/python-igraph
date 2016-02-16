Docker container for igraph in a Jupyter notebook
=================================================

This folder contains a ``Dockerfile`` to build igraph in Python and make it
accessible in a Jupyter notebook.

Use the following command line to start the container with Docker::

    $ docker run --rm -it -p 8888:8888 -v "$(pwd):/notebooks" ntamas/python-igraph-notebook
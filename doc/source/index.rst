.. igraph documentation master file, created by sphinx-quickstart on Thu Dec 11 16:02:35 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: include/global.rst

.. currentmodule:: igraph

python-igraph: the Python interface to igraph
=============================================
|igraph| is a fast open source tool to manipulate, analyze, and plot graphs or networks written in C, and `python-igraph` is |igraph|'s interface for the Python programming language.


Installation
============

.. container:: twocol

    .. container::

        Install using `pip <https://pypi.org/project/igraph>`__:

        .. code-block:: bash

            pip install igraph

    .. container::

        Install using `conda <https://docs.continuum.io/anaconda/>`__:

        .. code-block:: bash

            conda install -c conda-forge python-igraph

Further details are available in the :doc:`Installation Guide <install>`.

Documentation
=============

.. container:: twocol

    .. container::


       **Tutorials**

       - :doc:`tutorials/quickstart/quickstart`
       - :doc:`Gallery <gallery>`
       - :doc:`tutorial`


    .. container::

       **Reference**

       - :doc:`generation`
       - :doc:`analysis`
       - :doc:`visualisation`
       - :doc:`configuration`
       - :doc:`api/index`

.. toctree::
   :maxdepth: 1
   :hidden:

   install
   gallery
   tutorial
   api/index
   generation
   analysis
   visualisation
   misc
   configuration


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`


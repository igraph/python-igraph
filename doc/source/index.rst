.. igraph documentation master file, created by sphinx-quickstart on Thu Dec 11 16:02:35 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: include/global.rst

.. currentmodule:: igraph

.. raw:: html

    <style type="text/css">
    div.twocol {
        padding-left: 0;
        padding-right: 0;
        display: flex;
    }
    
    div.twocol > div {
        flex-grow: 1;
        padding: 0;
        margin-right: 20px;
    }
    </style>


python-igraph |release|
=======================
|igraph| is a fast open source tool to manipulate and analyze graphs or networks. It is primarily written in C. `python-igraph` is |igraph|'s interface for the Python programming language.

`python-graph` includes functionality for graph plotting and conversion from/to `networkx`_.


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

       **Detailed docs**

       - :doc:`Generation <generation>`
       - :doc:`Analysis <analysis>`
       - :doc:`Visualization <visualisation>`
       - :doc:`configuration`

.. container:: twocol

    .. container::

       **Reference**
 
       - :doc:`api/index`
       - `Source code <https://github.com/igraph/python-igraph>`_

    .. container::

       **Support**

       - :doc:`FAQs <faq>`
       - `Forum <https://igraph.discourse.group/>`_


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
   configuration
   faq


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`


.. _networkx: https://networkx.org/documentation/stable/

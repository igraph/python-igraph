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
Python interface of `igraph`_, a fast and open source C library to manipulate and analyze graphs (aka networks). It can be used to:

 - Create, manipulate, and analyze networks.
 - Convert graphs from/to `networkx`_, `graph-tool`_ and many file formats.
 - Plot networks using `Cairo`_, `matplotlib`_, and `plotly`_.


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

       - :doc:`Quick Start <tutorials/quickstart/quickstart>`
       - :doc:`Example Gallery <gallery>`
       - :doc:`Extended tutorial <tutorial>`

    .. container::

       **Detailed docs**

       - :doc:`Generation <generation>`
       - :doc:`Analysis <analysis>`
       - :doc:`Visualization <visualisation>`
       - :doc:`Configuration <configuration>`

.. container:: twocol

    .. container::

       **Reference**
 
       - :doc:`api/index`
       - `Source code <https://github.com/igraph/python-igraph>`_

    .. container::

       **Support**

       - :doc:`FAQs <faq>`
       - `Forum <https://igraph.discourse.group/>`_

Documentation for `python-igraph <= 0.10.1` is available on our `old website <https://igraph.org/python/versions/0.10.1>`_.

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


.. _igraph: https://igraph.org
.. _networkx: https://networkx.org/documentation/stable/
.. _graph-tool: https://graph-tool.skewed.de/
.. _Cairo: https://www.cairographics.org
.. _matplotlib: https://matplotlib.org
.. _plotly: https://plotly.com/python/

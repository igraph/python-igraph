.. include:: include/global.rst

.. currentmodule:: igraph

==========================
Frequently asked questions
==========================

I tried to install |igraph| but got an error! What do I do?
-----------------------------------------------------------
First, look at our :doc:`installation instructions <install>` including the
troubleshooting section. If that does not solve your problem, reach out via
the `igraph forum <https://igraph.discourse.group/>`_. We'll try our best to
help you!


I've just installed |igraph|. What do I do now?
-----------------------------------------------
Take a peek at the :doc:`tutorials/quickstart`! You can then go through a few
more examples in our :ref:`gallery <gallery-of-examples>`, read detailed instructions on graph :doc:`generation <generation>`, :doc:`analysis <analysis>` and :doc:`visualisation <visualisation>`, and check out the full :doc:`API documentation <api/index>`.


I thought |igraph| was an R package, is this the same package?
--------------------------------------------------------------
|igraph| is a software library written in C with interfaces in various programming
languages such as R, Python, and Mathematica. Many functions will have similar names
and functionality across languages, but the matching is not perfect, so you will
occasionally find functions that are supported in one language but not another.
See the FAQ below for instructions about how to request a feature.


I would like to use |igraph| but don't know Python, what to do?
---------------------------------------------------------------
|igraph| can be used from multiple programming languages such as C, R, Python,
and Mathematica. While the exact function names differ a bit, most functionality
is shared, so if you can code any of them you can use |igraph|: just refer to
the installation instructions for the appropriate language on our
`homepage <https://igraph.org>`_.

If you are not familiar with programming at all, or if you don't know any Python
but would still like to use the Python interface for |igraph|, you should start by
learning Python first. There are many resources online including online classes,
videos, tutorials, etc. |igraph| does not use a lot of advanced Python-specific
tricks, so once you can use a standard module such as :mod:`pandas` or
:mod:`matplotlib`, |igraph| should be easy to pick up.


I would like to have a function for operation/algorithm X, can you add it?
--------------------------------------------------------------------------
We are continuously extending |igraph| to include new functionality, and
requests from our community are the best way to guide those efforts. Of
course, we are just a few folks so we cannot guarantee that each and every
obscure community detection algorithm will be included in the package.
Please open a new thread on our `forum <https://igraph.discourse.group/>`_
describing your request. If your request is to adapt an existing function
or specific piece of code, you can directly open a
`GitHub issue <https://github.com/igraph/python-igraph/issues>`_
(make sure a similar issue does not exist yet! - If it does, comment there
instead.)


What's the difference between |igraph| and similar packages (networkx, graph-tool)?
-----------------------------------------------------------------------------------
All those packages focus on graph/network analysis.

.. warning::
   The following differences and similarities are considered correct as of the time of writing (Jan 2022). If you identify incorrect or outdated information, please open a `Github issue <https://github.com/igraph/python-igraph/issues>`_ and we'll update it.

**Differences:**

 - |igraph| supports **multiple programming languages** (e.g. C, Python, R, Mathematica). `networkx`_ and `graph-tool`_ are Python only.
 - |igraph|'s core library is written in C, which makes it often faster than `networkx`_. `graph-tool`_ is written in heavily templated C++, so it can be as fast as |igraph| but supports fewer architectures. Compiling `graph-tool` can take much longer than |igraph| (hours versus around a minute).
 - |igraph| vertices are *ordered with contiguous numerical IDs, from 0 upwards*, and an *optional* "vertex name". `networkx`_ nodes are *defined* by their name and not ordered.
 - Same holds for edges, ordered with integer IDs in |igraph|, not so in `networkx`_.
 - |igraph| can plot graphs using :mod:`matplotlib` and has experimental support for `plotly`_, so it can produce animations, notebook widgets, and interactive plots (e.g. zoom, panning). `networkx`_ has excellent :mod:`matplotlib` support but no `plotly`_ support. `graph-tool`_ only supports static images via Cairo and GTK+.
 - In terms of design, |igraph| really shines when you have a relatively static network that you want to analyse, while it can struggle with very dynamic networks that gain and lose vertices and edges all the time. This might change in the near future as we improve |igraph|'s core C library. At the moment, `networkx`_ is probably better suited for simulating such highly dynamic graphs.

**Similarities:**

 - Many tasks can be achieved equally well with |igraph|, `graph-tool`_, and `networkx`_.
 - All can read and write a number of graph file formats.
 - All can visualize graphs, with different strengths and weaknesses.

.. note::
  |igraph| includes conversion functions from/to `networkx`_, so you can create and manipulate a network with |igraph| and later on convert it to `networkx`_ or `graph-tool`_ if you need. Vice versa, you can load a graph in `networkx`_ or `graph-tool`_ and convert the graph into an |igraph| object if you need more speed, a specific algorithm, matplotlib animations, etc. You can even use |igraph| to convert graphs from `networkx`_ to `graph-tool`_ and vice versa!



I would like to contribute to |igraph|, where do I start?
---------------------------------------------------------
Thank you for your enthusiasm! |igraph| is a great opportunity to give back
to the open source community or just learn about graphs. Depending on your
skills in software engineering, programming, communication, or data science
some tasks might be better suited than others.

If you want to code straight away, take a look at the
`GitHub issues <https://github.com/igraph/python-igraph/issues>`_ and see if
you find one that sounds easy enough and sparks your interest, and write a
message saying you're interested in taking it on. We'll reply ASAP and guide
you as of your next steps.

The C core library also has various `"theory issues" <https://github.com/igraph/igraph/labels/theory>`_. You can contribute to these issues without any programming
knowledge by researching graph literature or finding the solution to a graph
problem. Once the theory obstacle has been overcome, others can move on to the
coding part: a real team effort!

If none of those look feasible, or if you have a specific idea, or still if
you would like to contribute in other ways than pure programming, reach out
on our `forum <https://igraph.discourse.group/>`_ and we'll come up with
some ideas.


.. _networkx: https://networkx.org/documentation/stable/
.. _graph-tool: https://graph-tool.skewed.de/
.. _plotly: https://plotly.com/python/

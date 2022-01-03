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
Take a peek at the :doc:`tutorials/quickstart/quickstart`! You can then go through a few
more examples in our :doc:`gallery <gallery>`, read detailed instructions on graph :doc:`generation <generation>`, :doc:`analysis <analysis>` and :doc:`visualisation <visualisation>`, and check out the full :doc:`API documentation <api/index>`.


I thought |igraph| was an R package, is this the same package?
--------------------------------------------------------------
|igraph| is a software library written in C with extensions in R, Python, and
Mathematica. Many functions will have similar names and functionality across
languages, but the matching is not perfect, so you will occasionally find
functions that are supported in one language but not another. See the above FAQ
for instructions about how to request a feature.


I would like to use |igraph| but don't know Python, what to do?
---------------------------------------------------------------
|igraph| can be used via four programming languages: C, R, Python, and Mathematica.
While the exact function names differ a bit, most functionality is shared, so if
you can code any of them you can use |igraph|: just refer to the installation
instructions for the appropriate language on our `homepage <https://igraph.org>`_.

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

If none of those look feasible, or if you have a specific idea, or still if
you would like to contribute in other ways than pure programming, reach out
on our `forum <https://igraph.discourse.group/>`_ and we'll come up with
some ideas!



.. include:: ../../include/global.rst

.. _tutorials-configuration:

======================
Configuration Instance
======================

This example shows how to use |igraph|'s `configuration instance <https://igraph.org/python/doc/api/igraph.configuration.Configuration.html>`_ to set default |igraph| settings. This is useful for setting global settings so that they don't need to be explicitly stated at the beginning of every |igraph| project you work on.

First we define the default plotting backend, layout, and color palette, and save them. By default, ``config.save()`` will save files to ``~/.igraphrc`` on Linux and Max OS X systems, or in ``C:\Documents and Settings\username\.igraphrc`` for Windows systems.

.. code-block:: python

    import igraph as ig

    # Get the configuration instance
    config = ig.Configuration().instance()

    # Set configuration variables
    config["general.verbose"] = True
    config["plotting.backend"] = "matplotlib"
    config["plotting.layout"] = "fruchterman_reingold"
    config["plotting.palette"] = "rainbow"

    # Save configuration to ~/.igraphrc
    config.save()

This script only needs to be run once, and can then be deleted. Afterwards any time you use |igraph|, it will read the config from the saved file and use them as the defaults. For example:

.. code-block:: python

    import igraph as ig
    import matplotlib.pyplot as plt
    import random

    # Generate a graph
    random.seed(1)
    g = ig.Graph.Barabasi(n=100, m=1)

    # Calculate a color value between 0-200 for all nodes
    betweenness = g.betweenness()
    colors = [int(i * 200 / max(betweenness)) for i in betweenness]

    # Plot the graph
    ig.plot(g, vertex_color=colors, vertex_size=1, edge_width=0.3)
    plt.show()

Note that we do not never explicitly state the backend, layout or palette, yet the final plots look like this:

.. figure:: ./figures/configuration.png
   :alt: A 100 node graph colored to show betweenness
   :align: center

   Graph colored based on each node's betweenness centrality measure.

The full list of config settings can be found `here <https://igraph.org/python/doc/api/igraph.configuration.Configuration.html>`_. 

.. note::
    
    - Note that you  can specify your own location by passing in a filepath to ``config.save``, e.g. ``config.save("./path/to/config/file")``. You can then load it later using ``ig.Configuration().instance().load("./path/to/config/file")``
    - If you want an efficient way to set the visual style between individual graphs (such as vertex sizes, colors, layout etc.) check out :ref:`tutorials-visual-style`. 

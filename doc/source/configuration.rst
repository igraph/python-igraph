.. include:: include/global.rst

.. currentmodule:: igraph

=============
Configuration
=============
|igraph| includes customization options that can be set via the :class:`configuration.Configuration` object and can be preserved via a configuration file. This file is stored at ``~/.igraphrc`` by default on Linux and Mac OS X systems, and at ``C:\Documents and Settings\username\.igraphrc`` on Windows systems.

To modify config options and store the result to file for future reuse:

.. code-block:: python

    import igraph as ig

    # Set configuration variables
    ig.config["plotting.backend"] = "matplotlib"
    ig.config["plotting.palette"] = "rainbow"

    # Save configuration to default file location
    ig.config.save()

Once your configuration file exists, |igraph| will load its contents automatically upon import.

It is possible to keep multiple configuration files in nonstandard locations by passing an argument to ``config.save``, e.g. ``ig.config.save("/path/to/config/file")``. To load a specific config the next time you import igraph, use:

.. code-block:: python

   import igraph as ig
   ig.config.load("/path/to/config/file")

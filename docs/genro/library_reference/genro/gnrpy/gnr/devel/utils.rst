===========================================================
:mod:`gnr.devel.utils` -- Tools to build command-line tools
===========================================================
    
    *Last page update*: |today|
    
    .. automodule:: gnr.devel.utils

Autodiscovery
=============

It is a tool to gather information about projects, instances, sites,
packages and commands available in a given GenroPy installation.

It tries to guess the current project, instance, site and package
based on the current working directory.

.. autoclass:: AutoDiscovery
    :members:

Utilities
=========

.. autofunction:: expandpath

.. autoclass:: ProgressBar
    :members:
    
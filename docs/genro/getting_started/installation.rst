.. _installation:

====================
GenroPy Installation
====================

    *Last page update*: |today|
    
    * :ref:`requirements`
    * :ref:`obtaining`
    * :ref:`installing`
    * :ref:`configuring`
    * :ref:`inst_tutorials`

.. _requirements:

Requirements
============

    To use GenroPy, you'll need at least:
    
    * Mac OS or Linux [#]_
    * Python 2.6
    * Postgres 8
    * git
    
    Install **easy_install**::
    
        curl -O http://peak.telecommunity.com/dist/ez_setup.py
        sudo python ez_setup.py
        # for Ubuntu
        sudo apt-get install python-setuptools
        
    Install **psycopg2** and **paver**, with *easy_install*::
    
        sudo easy_install -U -Z psycopg2
        # for Ubuntu
        sudo apt-get install python-psycopg2
    
    To install *paver*::
    
        sudo easy_install -U -Z paver
    
    (``-U`` = upgrade, ``-Z`` = always unzip)

.. _obtaining:

How to obtain GenroPy
=====================

    Genropy is in a git repository. To obtain genropy, type::
    
        add???
        
.. _installing:

Installing GenroPy
==================

    The bulk of the work is done thanks to *paver*::
    
        cd genro
        cd gnrpy
        sudo paver develop
        
.. _configuring:

Configuring GenroPy
===================

    GenroPy uses the :ref:`gnr_index` folder for configuration::
    
        cd ../example_configuration/
        cp -a moveto.gnr $HOME/.gnr
    
    Edit the :ref:`gnr_environment`, the "siteconfig\/:ref:`gnr_siteconfig_default`\"
    and the "instanceconfig\/:ref:`gnr_instanceconfig_default`\" as needed.
    More information on relative links.

.. _inst_tutorials:

Tutorials
=========

    Now you can put your hands in dough:
    
    * learning how to create a Genro project: check the :ref:`tutorial <tutorial_index>`
      section
    * checking some project examples in the :ref:`tts_index` section
      
**Footnotes**

.. [#] Windows is supported but it is not preferred and (until now) it is not yet documented

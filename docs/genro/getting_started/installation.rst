.. _genro_installation:

====================
GenroPy Installation
====================

    *Last page update*: |today|
    
    * :ref:`installationRequirements`
    * :ref:`obtainingGenropy`
    * :ref:`installingGenropy`
    * :ref:`configuringGenropy`
    * :ref:`projectsExamples`

.. _installationRequirements:

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

.. _obtainingGenropy:

How to obtain GenroPy
=====================

    Genropy is in a git repository. To obtain genropy, type::
    
        add???
        
    .. _installingGenropy:

Installing GenroPy
==================

    The bulk of the work is done thanks to *paver*::
    
        cd genro
        cd gnrpy
        sudo paver develop
        
.. _configuringGenropy:

Configuring GenroPy
===================

    GenroPy uses the :ref:`genro_gnr_index` folder for configuration::
    
        cd ../example_configuration/
        cp -a moveto.gnr $HOME/.gnr
    
    Edit the :ref:`gnr_environment`, the "siteconfig\/:ref:`gnr_siteconfig_default`\"
    and the "instanceconfig\/:ref:`gnr_instanceconfig_default`\" as needed.
    More information on relative links.

.. _projectsExamples:

Project Examples
================

    GenroPy includes some tutorial projects:
    
    * **agenda**: an application to manage phone calls
      (package, application and site: **agenda**)
      
    * **fatture1**: add???change to invoice! - it is a simple invoice application
      (package: **invoices**, application and site: **fatture1**)
      
    * **showcase**: it is an incomplete but useful collection of examples.
      (package, application and site: **showcase**)
      
    To create the database in postgres type::
    
        gnrdbsetup instanceName
        
    where ``instanceName`` is the name of the instance of your :ref:`genro_project`.
    
    To start the paste :ref:`genro_wsgi` development webserver, type::
    
        gnrwsgiserve siteName
        
    where ``siteName`` is the name of the site folder of your :ref:`genro_project`.
    
   .. note:: We suggest you to begin with the **showcase** tutorial: follow the instructions
             of the :ref:`genro_showcase_index` documentation section to start with it.
             
**Footnotes**

.. [#] Windows is supported but it is not preferred and (until now) it is not yet documented

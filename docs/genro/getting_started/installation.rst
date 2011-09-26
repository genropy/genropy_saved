.. _installation:

====================
GenroPy Installation
====================

    *Last page update*: |today|
    
    * :ref:`requirements`
    * :ref:`obtaining`
    * :ref:`installing`
    
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

    Genropy is in a Git repository. To obtain genropy, type::
    
        add???
        
.. _installing:

Installing GenroPy
==================

    The bulk of the work is done thanks to *paver*::
    
        cd genro
        cd gnrpy
        sudo paver develop
        
**Footnotes**

.. [#] Windows is supported but it is not preferred and (until now) it is not yet documented

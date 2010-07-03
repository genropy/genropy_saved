***************
 Install
***************

Requirements
============

To use GenroPy, you'll need at least:

- Mac OS or Linux (Windows is possible but not preferred or covered here)
- Python 2.6
- Postgres 8
- subversion
- git (optional)

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

How to obtain GenroPy
=====================

Genropy is in a subversion repository.  If you use git then you can track local changes.  To obtain genropy, type::

    svn co http://svn.genropy.org/genro/trunk genro

If you have the time here is the git alternative::

    git svn clone http://robertolupi@svn.genropy.org/genro/trunk genro

Installing GenroPy
==================

The bulk of the work is done thanks to *paver*::

    cd genro
    cd gnrpy
    sudo paver develop

Configuring GenroPy
===================

GenroPy using the ``.gnr`` configuration::

    cd ../example_configuration/
    cp -a moveto.gnr $HOME/.gnr

Edit ``environment.xml``, ``siteconfig/default.xml`` and ``instanceconfig/default.xml`` as needed.

Installation Examples
=======================

GenroPy includes some test projects:

Showcase - is an incomplete but useful collection of examples.
(package: **showcase**, application:**showcase**, site **testgarden**)


Fatture1 - is a simple invoice application
(package: **invoices**, application and site: **fatture1**)

To create the database in postgres and start the paste wsgi development webserver::

    gnrdbsetup -i fatture1
    gnrwsgiserve -s fatture1

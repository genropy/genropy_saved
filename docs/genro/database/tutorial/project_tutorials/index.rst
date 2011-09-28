.. _tts_index:

=================
project tutorials
=================

    .. warning:: chapter to be written completely!
    
    *Last page update*: |today|
    
.. _tts_intro:

introduction
============

    add???
    
    GenroPy includes some tutorial projects:
    
    * :ref:`tts_agenda`: an application to manage phone calls
    * :ref:`tts_invoices`: it is a simple invoice application
    * :ref:`tts_showcase`: it is an incomplete but useful collection of examples
    
.. _tts_initiate_project:

initiate a project
==================
    
    add???
    
    Create the database: add??? (Navicat...)
    
    To create a **schema**... add???
    
    To fill the database structure in postgres use the :ref:`gnrdbsetup` script typing::
    
        gnrdbsetup instanceName
        
    where ``instanceName`` is the name of the instance of your :ref:`project`.
    
    To start the paste :ref:`wsgi` development webserver use the :ref:`gnrwsgiserve` script typing::
    
        gnrwsgiserve siteName
        
    where ``siteName`` is the name of the site folder of your :ref:`project`
    
   .. note:: We suggest you to begin with the **add???** tutorial: follow the instructions
             of the add??? section to start with it.
    
.. _tts_section_index:

section index
=============

.. toctree::
    :maxdepth: 2
    
    agenda
    invoices
    showcase
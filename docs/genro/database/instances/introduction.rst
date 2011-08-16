.. _instances_introduction:

============
Introduction
============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/instances/project_instances.png
    
    * :ref:`instances_map`
    * :ref:`instances_autofill`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``instances`` folder:
    
    * contains customizations for the particular customer
    * usually contains parameters for database access
    * has a :ref:`instances_data` subfolder that you can use to store data in filesystems
    
.. _instances_map:

``instances`` folder content list
=================================

    If you follow the steps of the :ref:`project_autocreation` section, inside your
    ``instances`` folder you will find an ``instance`` folder including a ``custom`` folder,
    a ``data`` folder and the ``instanceconfig`` file.
    
    .. image:: ../../_images/projects/instances/instances1.png
    
    where ``projectName`` is the name of your instance (we suggest you to call your instance
    with the name you gave to your project).
    
    Click on the following links for more information on them:
    
    * :ref:`instances_custom`
    * :ref:`instances_data`
    * :ref:`instances_instanceconfig`
    
.. _instances_autofill:

autocreation of the ``instances`` folder
========================================

    To create a new istance folder you can type in your terminal::
    
        gnrmkinstance instanceName
        
    where ``instanceName`` is the name of your instance (we suggest you to call your instance
    with the name you gave to your :ref:`project`).
    
    Your ``instances`` folder will look like this one:
    
    .. image:: ../../_images/projects/instances/instances2.png
    
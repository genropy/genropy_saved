.. _genro_instances_introduction:

============
Introduction
============

    .. image:: ../../images/projects/project_instances.png
    
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

    If you follow the steps of the :ref:`genro_project_autocreation` section, inside your
    ``instances`` folder you will find an ``instance`` folder including a ``custom`` folder,
    a ``data`` folder and the ``instanceconfig`` file.
    
    .. image:: ../../images/projects/instances.png
    
    where ``instancename`` is the name of your instance (we suggest you to call your instance
    with the name you gave to your :ref:`genro_project`).
    
    Click on the following links for more information on them:
    
    * :ref:`instances_custom`
    * :ref:`instances_data`
    * :ref:`instances_instanceconfig`
    
.. _instances_autofill:

autocreation of the ``instances`` folder
========================================

    To create a new istance folder you can type in your terminal::
    
        gnrmkinstance instancename
        
    where ``instancename`` is the name of your instance (we suggest you to call your instance
    with the name you gave to your :ref:`genro_project`).
    
    Your ``instances`` folder will look like this one:
    
    .. image:: ../../images/projects/instances.png
    
    where ``myproject`` is the name of your instance.
    
    .. note:: The autocreation of this folder is handled by the :class:`InstanceMaker` class.
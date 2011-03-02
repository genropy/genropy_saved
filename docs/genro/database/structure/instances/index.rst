.. _genro_instances_index:

=========
instances
=========

    * :ref:`instances_features`
    * :ref:`instances_autofill`
    * :ref:`instances_map`
    
    .. module:: gnr.app.gnrdeploy
    
.. _instances_features:

features
========

    The ``instances`` folder:
    
    * contains customizations for the particular customer
    * Usually contains parameters for database access
    * has a :ref:`instances_data` subfolder that you can use to store data in filesystems
    
.. _instances_autofill:

autocreation of the ``instances`` folder
========================================

    You can create an ``instances`` folder typing::
    
        gnrmkinstance instancename
        
    where ``instancename`` is the name of your instance (we suggest you to call your instance with the name you gave to your :ref:`genro_structure_mainproject`).
    
    Your ``instances`` folder will look like this one:
    
    .. image:: ../../../images/structure/structure-instances.png
    
    where ``myproject`` is the name of your instance.
    
    .. note:: The autocreation of this folder is handled by the :class:`InstanceMaker` class.
    
.. _instances_map:

``instances`` folder content list
=================================

    If you follow the steps of the previous section, inside your ``instances`` folder you will find an ``instance`` folder including a ``custom`` folder, a ``data`` folder and the ``instanceconfig`` file.
    
    Click on the following links for more information on them:
    
.. toctree::
    :maxdepth: 1
    
    instance_name
    custom
    data
    instanceconfig
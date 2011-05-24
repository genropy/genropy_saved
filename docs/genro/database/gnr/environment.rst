.. _gnr_environment:

===================
``environment.xml``
===================

    .. warning:: to be completed!
    
    .. image:: ../../images/projects/gnr/environment.png
    
    * :ref:`environment_introduction`
    * The :ref:`environment_instances` tag
    * The :ref:`environment_packages` tag
    * The :ref:`environment_resources` tag
    * The :ref:`environment_sites` tag
    
.. _environment_introduction:
    
Introduction
============

    The ``environment.xml`` allow to define the root paths for your
    :ref:`genro_project` folders.
    
    We remind you that every project folder includes the following four subfolders:
    
    * the :ref:`genro_instances_index` folder
    * the :ref:`genro_packages_index` folder
    * the :ref:`private_resources` folder
    * the :ref:`genro_sites_index` folder
    
    You have to define the path of the genro project's folders and the path for the
    dojo's contents. Optionally, you can specify the path of your projects (and theirs
    relative subfolders).
    
.. _environment_instances:

<instances>
===========

    add???
    
.. _environment_packages:

<packages>
==========

    add???
    
.. _environment_resources:

<resources>
===========

    To configure correctly the ``environment.xml`` file for the usage of :ref:`genro_component`\s,
    you have to add the following tag::
    
       <genro path="$GNRHOME/resources/"/>
       
    So the ``<resources>`` tag will be::
    
       <resources>
           <genro path="$GNRHOME/resources/"/>
       </resources>
       
    .. _environment_sites:

<sites>
=======

    add???
    
    .. _environment_example:
    
example
=======
    
    We report here the structure of the ``environment.xml``::
    
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <environment>
                <gnrhome value='~/development/genro' /> <!--"development" is our rootpath folder for Genro-->
            </environment>
            <projects>
                <genro path="$GNRHOME/projects" />
                <softwell path='~/development/softwell/projects' /> <!--Here lies a repository of Genro Team project-->
                <my_project path="~/development/my_project"/> <!--Add here the path of your projects-->
            </projects>
            <packages>
                <genro path="$GNRHOME/packages"/>
                <my path='~/my_packages' />  <!--Add here the path of your packages folder -->
            </packages>
            <static>'
                <js>
                    <dojo_11 path="$GNRHOME/dojo_libs/dojo_11" cdn=""/> <!--Put here the version of Dojo and
                                                                         Genro js libs you use-->
                    <gnr_11 path="$GNRHOME/gnrjs/gnr_d11"/>
                </js>
            </static>
            <resources >
                <genro path="$GNRHOME/resources/"/>
            </resources>
        </GenRoBag>
                
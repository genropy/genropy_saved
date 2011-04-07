.. _gnr_environment:

===================
``environment.xml``
===================

    The ``environment.xml`` allow to define the root for your :ref:`genro_project` folders.
    
    We remind you that every project folder includes the following four subfolders:
    
    * the :ref:`genro_instances_index` folder
    * the :ref:`genro_packages_index` folder
    * the :ref:`genro_resources_index` folder
    * the :ref:`genro_sites_index` folder
    
    You have to define the path of the genro project's folders and the path for the dojo's contents.
    Optionally, you can specify the path of your projects (and theirs relative subfolders).
    
    We report here the structure of the ``environment.xml``::

        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <environment>
                <gnrhome value='~/development/genro' /> <!--"development" is our rootpath folder for Genro-->
            </environment>
            <projects>
                <genro path="$GNRHOME/projects" />
                <softwell path='~/development/softwell/projects' /> <!--here lies a repository of Genro Team project-->
                <my_project path="~/development/my_project"/> <!--here you put your projects' folders-->
            </projects>
            <packages>
                <genro path="$GNRHOME/packages"/>
                <my paths='~/yourFolderPathOfYourProject' />
            </packages>
            <static>'
                <js>
                    <dojo_11 path="$GNRHOME/dojo_libs/dojo_11" cdn=""/>
                    <dojo_13 path="$GNRHOME/dojo_libs/dojo_13" cdn=""/>
                    <gnr_11 path="$GNRHOME/gnrjs/gnr_d11"/>
                    <gnr_13 path="$GNRHOME/gnrjs/gnr_d13"/>
                </js>
            </static>
            <resources >
                <genro path="$GNRHOME/resources/"/>
            </resources>
        </GenRoBag>
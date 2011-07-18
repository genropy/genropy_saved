.. _genro_gnr_instanceconfig:

==================
``instanceconfig``
==================
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/gnr/instanceconfig.png
    
    * :ref:`gnr_instanceconfig_default`:
    
        * :ref:`instanceconfig_auto`
        * :ref:`instanceconfig_tags`:
        
            * :ref:`instanceconfig_packages`
            * :ref:`instanceconfig_db`
            * :ref:`instanceconfig_authentication`: :ref:`instanceconfig_xml_auth`,
              :ref:`instanceconfig_py_auth`
              
    The ``instanceconfig`` folder includes a single file: ``default.xml``
    
.. _gnr_instanceconfig_default:
    
``default.xml``
===============

    .. image:: ../../_images/projects/gnr/instance_default.png
    
    The ``default.xml`` file is an XML file that allows to:
    
    * define the packages you want to use in your :ref:`genro_project`
    * define the name of your database
    * handle the permits of your :ref:`genro_project`
    
    .. note:: the ``default.xml`` file of the ``.gnr/instanceconfig`` folder set the
              default values for the :ref:`instances_instanceconfig` file of all your
              :ref:`genro_project`.
              
              You can obviously redefine the values of the ``instanceconfig.xml`` file
              for every project you make, setting the features directly in the
              :ref:`instances_instanceconfig` file of the project.
    
.. _instanceconfig_auto:

autocreation
------------
    
    With the :ref:`instances_autofill` the ``instanceconfig`` will look like this one::
    
        <?xml version='1.0' encoding='UTF-8'?>
        <GenRoBag>
            <packages _T="NN">
            </packages>
            <db _T="NN">
            </db>
            <authentication pkg="adm">
                <py_auth _T="NN" defaultTags="user" pkg="adm" method="authenticate"></py_auth>
            </authentication>
        </GenRoBag>

.. _instanceconfig_tags:

Tags
----

    Let's see its content:
    
    * The ``<packages>`` tag allows to include any other package from other projects; Genro will
      search it through its mixin tecnique. For more information, check the
      :ref:`instanceconfig_packages` paragraph.
    * The ``<db>`` tag includes the name of your database. For more information, check the
      :ref:`instanceconfig_db` paragraph.
    * The ``<authentication>`` tag allow to handle all the access authorization to your project.
      Check the :ref:`instanceconfig_authentication` paragraph for more information.
    * The ``_T="NN"`` is a special attribute that allow to keep track of datatypes (for more
      information, check the :ref:`bag_from_to_XML` section).
    
.. _instanceconfig_packages:

``<packages>``
^^^^^^^^^^^^^^
    
    The ``<packages>`` tag allow to include any other package from other projects: this allow
    you to use every file (:ref:`genro_table`\s, :ref:`webpages_webpages`\s,
    :ref:`genro_intro_resources`) of the packages you've imported. If you want to import one
    package, you have to:
    
    #. include its path into the :ref:`environment_packages` tag of your ``environment.xml`` file
       
    #. include the package name into the ``<packages>`` tag of the ``instanceconfig.xml`` file.
       The syntax is::
       
         <projectName:packageName />
         
       where ``projectName`` is the name of the folder of the project, while ``packageName``
       is the name of the package you need to import. You can obviously import many packages
       from a single project.
       
       **Example:** if you need the ``invoice`` package and the ``taxes`` package from the
       ``money`` project, you will write in your ``instanceconfig.xml`` file::
       
         <packages>
             <money:invoice />
             <money:taxes />
         </packages>
         
       while in the :ref:`gnr_environment` file::
       
         <packages>
             <my paths='~/yourRootPathForGenro/.../theFolderPathOfTheMoneyProject' />
         </packages>
         
    .. note:: Remember that in the ``<packages>`` tag you have at least put your main package::
              
                <mypackage />
              
              With main package we mean the package where you put your :ref:`packages_model`
              and :ref:`packages_webpages` folders.
              
    .. note:: Remeber also to import the ``sys`` package::
              
                <gnrcore:sys />
                
              So you will have [#]_::
              
                <packages>
                    <mypackage />
                    <gnrcore:sys />
                </packages>
                
.. _instanceconfig_db:

``<db>``
^^^^^^^^

    In the ``<db>`` tag you have to specify at least the database name::
    
        <db dbname='myDatabaseName' />
        
    There are many options you can add:
    
    * ``dbname``: specify the name of the database
    * ``implementation``: you can choose the SQL database engine. For the best performance,
      use postgreSQL (implementation="postgres")
    * ``host``: specify the host.
    * ``password``: the password of the SQL database engine.
    * ``user``: the user of the SQL database engine.
    
    .. note:: We suggest you to keep the usage of postgreSQL, but, if you prefer, you can use
              MySQL or SQLite.
              
    This is an example of ``<db>``::
    
        <db dbname="mypersonaldatabase" implementation="postgres"
            host="localhost" password="superSecurePwd" user="postgres"  />
        
.. _instanceconfig_authentication:

``<authentication>``
^^^^^^^^^^^^^^^^^^^^

    The ``<authentication>`` tag allow to manage the authentications to your project's webpages.
    
    You have to specify the ``adm`` package inside the ``<authentication>`` tag::
    
        <authentication pkg="adm"></authentication>
        
    .. note:: remember to import the ``adm`` package following the istructions of the
              :ref:`instanceconfig_packages` section.
        
    The ``adm`` package allow to manage the authentications. For more information on it, check
    the :ref:`genro_library_adm` documentation page.
    
    Inside the ``<authentication>`` tag we have to define two different tags: the ``<py_auth>``
    and the ``<xml_auth>``.
    
.. _instanceconfig_xml_auth:

``<xml_auth>``
^^^^^^^^^^^^^^

    .. warning:: DEPRECATED!!! The adm/manage_users is not used anymore! add???
    
    .. note:: the ``<xml_auth>`` tag uses the :meth:`auth_xml` method of the ``GnrApp`` class.
    
    The ``<xml_auth>`` tag is a support tag that comes in handy to the :ref:`instanceconfig_py_auth`
    tag; it allows to you (i.e. the programmer) to enter the first time into the webpage called
    *adm/manage_users* you can give to your customers (and to you!) a user and a password
    to access to your project.
    
    The ``<xml_auth>`` attributes are:
    
    * The first attribute is the name of your temporary user (in the example below, ``nameUser``)
    * `pwd`: the password of your temporary user
    * `tags`: the level of authorization of your user; you can use every tag you want, there is no
      keyword for any user. For example, you may want to use these four level authorizations:
    
        * `_DEV_`: developer
        * `admin`: administrator
        * `user`: user
        * `staff`: staff
        
    And your ``<xml_auth>`` will be something like::
    
        <xml_auth defaultTags="users,xml">
            <myName pwd="superSecurePwd" tags="_DEV_,admin,user,staff"/>
        </xml_auth>
        
    where ``myName`` is the name, ``superSecurePwd`` is the password.
    
.. _instanceconfig_py_auth:

``<py_auth>``
^^^^^^^^^^^^^

    .. warning:: DEPRECATED!!! The adm/manage_users is not used anymore! add???
    
    .. note:: the ``<py_auth>`` tag uses the :meth:`auth_py` method of the ``GnrApp`` class.
    
    Once you have your temporary user [#]_, you can create the users for your customers.
    
    For doing this, you have to go the following webpage::
    
        http://127.0.0.1:yourPort/adm/manage_users
        
    where in place of ``yourPort`` you have to put your port (e.g. 8090) that you have set in your
    :ref:`sites_siteconfig`::
    
        http://127.0.0.1:8090/adm/manage_users
    
    Once you're there you will find a standardTable; open the padlock (you can do it because you
    entered with xml authorization) and set all the users you need (your one, the customers one...).
    
    So, your ``<authentication>`` tag will look like this one::
    
        <authentication pkg="adm">
            <py_auth defaultTags="user" pkg="adm" method="authenticate"></py_auth>
            <xml_auth defaultTags="users,xml">
                <myName pwd="superSecurePwd" tags="_DEV_,admin,user,staff"/>
            </xml_auth>
        </authentication>
        
**Footnotes**:

.. [#] Notice that for the package included in your project you may omit the name of the project in the syntax.
.. [#] If you don't have a temporary user, please create it following the instructions of the :ref:`instanceconfig_xml_auth` paragraph
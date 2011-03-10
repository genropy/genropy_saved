.. _webpages_webpages:

=======
webpage
=======

    * :ref:`webpages_introduction`
    * :ref:`webpages_GnrCustomWebPage`
    * :ref:`webpages_variables`:
    
        * Components variables: :ref:`webpages_py_requires`
        * CSS variables: :ref:`webpages_css_requires`, :ref:`webpages_css_theme`
        * Dojo variables: :ref:`webpages_dojo_source`, :ref:`webpages_dojo_theme`, :ref:`webpages_dojo_version`
        * Javascript variables: :ref:`webpages_js_requires`
        * Page options: :ref:`webpages_pageOptions`
        * Polling variables: :ref:`webpages_auto_polling`, :ref:`webpages_user_polling`
        * Other variables: :ref:`webpages_auth_tags`, :ref:`webpages_eagers`, :ref:`webpages_gnrjsversion`,
          :ref:`webpages_maintable`, :ref:`webpages_recordlock`
        
.. _webpages_introduction:

Introduction on a GnrCustomWebPage
==================================

    Genro provides the application GUI using webpages. GnrCustomWebPage. The standard usage of Genro GnrCustomWebPages is to use them in a combo with some :ref:`model_table`\s to create a DBMS :ref:`genro_structure_mainproject`.
    
    You can act on a Genro webpage through many elements: please check every relative section if you need to learn more about them.
    
    * **Widgets elements** - Used to create the webpage's layout and to introduce the input elements (button, checkbox, etc).
    
        * Check the :ref:`genro_widgets_introduction`;
        * description and list of all the :ref:`genro_widgets_index`.
    
    * **HTML elements** - standard HTML elements.
    
        * Check the :ref:`genro_html_introduction`.
    
    * **CSS elements** - standard CSS elements.
    
        * Check the :ref:`genro_css`.
    
    * **data elements** - Used to define variables from server to client.
    
        * Check the :ref:`genro_data` page.
        
    * **dataRemote elements** - Synchronous rpc.
        
        * Check the :ref:`genro_dataremote` page.
    
    * **controller elements** - They receive input and initiate a response by making calls on model objects.
        
        * Check the :ref:`genro_controllers_intro`;
        * list of :ref:`genro_datacontroller_index`.
        
    We are going now to introduce the :ref:`webpages_GnrCustomWebPage`, the standard class used to build the webpages.

.. _webpages_GnrCustomWebPage:

GnrCustomWebPage
================

    The GnrCustomWebPage (Genro Custom Webpage) is add???(a mixin class?) through which you can build your webpages.
    
    #. A webpage file has to begin with a line code that specify the location to the python executable in your machine::
    
        #!/usr/bin/env python
        
    #. Then you have to (optionally) specify the encoding you are using::
        
        # encoding: utf-8
    
    #. After that you have to introduce the GnrCustomWebPage class with the following declaration line::
    
        class GnrCustomWebPage(object):
        
    #. You may insert some optional :ref:`webpages_variables`. Here we introduce the most commonly used:
    
        * :ref:`webpages_maintable`: allow to create shortcuts for users query
        * :ref:`webpages_py_requires`: allow to include some Genro :ref:`genro_components_index` to your webpage
        * :ref:`webpages_js_requires`: allow to include some javascipt functionality to your webpage
        * :ref:`webpages_css_requires`: allow to include some :ref:`genro_css` to your webpage
    
    #. You have to define the main method (unless you're using an active component [#]_)
        
    Let's see now an example of a complete heading of a webpage::
    
        #!/usr/bin/env python
        # encoding: utf-8
        
        class GnrCustomWebPage(object):
            maintable = 'agenda.contact'
            py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'
            css_requires = 'public'
            
            def main(self,root,**kwargs):
                root.div('Hello world!')
                # Here goes the rest of your code...
                
    In the following section we describe the :ref:`webpages_variables`.
    
    .. _webpages_variables:

webpages variables
==================
    
    With the term ``webpages variables`` we mean that Genro provides some defined variables that you can use to customize your webpages.
    
    .. note:: The webpages variables act only on the single webpage you insert it.
    
    .. _webpages_dojo_theme:

dojo_theme
----------

    * Description: a string that allows to change the Dojo theme of your webpage
    * Default value: *tundra*
    * Compatible themes:
    
        * Dojo 1.1: *nihilo*, *soria*, *tundra*
        * Dojo 1.5: *claro*, *nihilo*, *soria*, *tundra*
        
    * Example::
        
        dojo_theme = 'nihilo'
    
    .. _webpages_dojo_version:

dojo_version
------------
    
    * Description: a number that allows to specify the Dojo version of your :ref:`genro_structure_mainproject`.
      You have to write the version supported without the dot (e.g: write '11' for Dojo '1.1')
    * Default value: the value you specify in the :ref:`siteconfig_dojo` tag of your :ref:`sites_siteconfig`.
      If you didn't specify it, the default value is '11'
    * Example::
    
        dojo_version = '11'
    
    .. _webpages_css_theme:

css_theme
---------

    * Description: a string that allows to change the Genro's page theme. A Genro theme add some CSS features
      to the Dojo theme you are using in your project (to change the Dojo theme, you can only change it
      through the :ref:`webpages_dojo_theme` webpage variable)
    * Default value: the value you specify in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`.
      If you didn't specify it, the default value is ``add???``.
    * Example::
    
        css_theme = 'aqua'
    
    .. note:: if you want to define a Genro theme in all of your webpages, define it in the
              :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`
    
    .. _webpages_gnrjsversion:

gnrjsversion
------------

    * Description: Genro Javascript libraries compatible with the relative Dojo version (type: number).
    * Default value: the value you specify in the :ref:`siteconfig_jslib` tag of your :ref:`sites_siteconfig`.
      If you didn't specify it, the default value is '11' (i.e: Genro JS libraries compatible with Dojo 1.1)
    * Example::
    
        gnrjsversion = '11'
    
    .. _webpages_maintable:

maintable
---------
    
    * Description: a string that allows to create shortcuts for user queries through some Genro
      :ref:`genro_form_index` (like :ref:`genro_field` or :ref:`genro_fieldcell`)
    * Syntax: ``maintable = 'packageName.tableName'``, where:
    
        * ``packageName`` is the name of your package (for more information, check the :ref:`genro_packages_index` page)
        * ``tableName`` is the name of the :ref:`model_table`   
    
    * Default value: ``None``
    * Example::
    
        maintable = 'agenda.call'
    
    .. _webpages_recordlock:

recordLock
----------

    * Description: add???
    * Default value: add???
    * Example: add???
    
    .. _webpages_user_polling:

user_polling
------------
    
    * Description: set a number for user-polling frequency (units: seconds)
    * Default value: ``3``
    * Example::
    
        user_polling = 3
        
    .. _webpages_auto_polling:

auto_polling
------------

    * Description: set a number for auto-polling frequency (units: seconds)
    * Default value: ``30``
    * Example::
    
        auto_polling = 30
    
    .. _webpages_eagers:

eagers
------

    * Description: a dict that allows to give a hierarchy to the :ref:`bag_resolver` calls of a :ref:`sql_relation`:
      the relations you put in the eagers are resolved before the other ones.
    * Syntax: 
        
        * *key*: ``packageName.tableName``, where:
        
            * ``packageName`` is the name of your package (for more information check the :ref:`genro_packages_index` page)
            * ``tableName`` is the name of the :ref:`model_table`
            
        * *value*: includes a :ref:`sql_relation`
    * Default value: ``{}`` (an empty dict)
    * Example::
    
        eagers = {'writers.contracts':'@sy_publisherid'}
    
    .. _webpages_py_requires:

py_requires
-----------

    * Description: a string that allows to include some components to your project.
    * Syntax: ``py_requires = 'fileName:componentClassName'``
    
        Where:
        
        * ``fileName`` is the name of the file including the component (write it without its ``.py`` extension)
        * ``componentClassName`` is the name of the component class
        
    * Default value: ``None``
    * Example::
    
        py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'
    
    In this example you are calling the ``Public`` and the ``IncludedView`` classes of the ``public.py`` file
    and the ``TableHandler`` class of the ``standard_tables.py`` file.
    
    .. note:: The components you want to use must be placed into a folder named "``resources``" (or "``_resources``")
              
              * For more information about components check the :ref:`genro_components_index` documentation page
              * For more information about their location in a Genro :ref:`genro_structure_mainproject`,
                please check the :ref:`genro_webpage_resources` documentation page.
    
    .. _webpages_js_requires:

js_requires
-----------

    * Description: allow to import some javascript files
    * Default value: ``None``
    * Example::
    
        js_requires = 'wizard'
        
    This line implies that you have created a js file called ``wizard.js``
        
    .. note:: The js files you want to use must be placed into a folder named "``resources``" (or "``_resources``")
              
              * For more information about Genro js and their location in Genro, please check the
                :ref:`genro_webpage_resources` documentation page.
    
    .. _webpages_pageOptions:

pageOptions
-----------

    * Description: a dict with page options. add??? --> pageOptions = {'enableZoom':False,'openMenu':False}
    * Default value: ``add???``
    * Example::
    
        add???
    
    .. _webpages_css_requires:

css_requires
------------

    * Description: allow to import some css files.
    * Default value: ``None``
    * Example:
    
        css_requires = 'my_css'
        
    This line implies that you have created a CSS file called ``my_css.js``
        
    .. note:: The CSS files you want to use must be placed into a folder named "``resources``" (or "``_resources``")
              
              * For more information about Genro CSS, please check the :ref:`genro_css` documentation page.
              * For more information about their location in a Genro :ref:`genro_structure_mainproject`, please check the
                :ref:`genro_webpage_resources` documentation page.
    
    .. _webpages_auth_tags:

auth_tags
---------

    * Description: add???
    * Default value: ``add???``
    * Example:
    
        add???
    
    .. _webpages_dojo_source:

dojo_source
-----------

    add???
    
    * Description: add???
    * Default value: boolean. Default value is add???(``True``?)
    * Example:
    
        add???

**Footnotes**:

.. [#] For more information on active and passive components, please check the :ref:`components_active_passive` documentation section.
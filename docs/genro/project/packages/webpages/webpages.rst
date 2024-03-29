.. _webpage:

=======
webpage
=======

    *Last page update*: |today|
    
    .. image:: ../../../_images/projects/packages/webpage.png
    
    * :ref:`The GnrCustomWebPage class <gnrcustomwebpage>`
    * :ref:`The main method <webpages_main>`
    * :ref:`webpages_methods`
    * :ref:`webpages_variables`
    
.. _gnrcustomwebpage:

GnrCustomWebPage
================
    
    .. module:: gnr.web.gnrwebpage
    
    Genro provides the application GUI using webpages. A webpage is built through an istance
    of the GnrCustomWebPage class, that is a custom class of the :class:`GnrWebPage`.
    
    You can act on a Genro webpage through many webpage elements: please check the
    :ref:`introduction to webpage elements <we_intro>` if you need
    to learn more about them.
    
    The GnrCustomWebPage (Genro Custom Webpage) is TODO(a mixin class?) through which you can
    build your webpages.
    
    #. A webpage file has to begin with a line code that specify the location to the python
       executable in your machine::
    
        #!/usr/bin/env python
        
    #. Then you have to specify the encoding. For example::
        
        # encoding: utf-8
        
    #. After that you have to introduce the GnrCustomWebPage class with the following declaration line::
    
        class GnrCustomWebPage(object):
        
    #. You may insert some optional :ref:`webpages_variables`. Here we introduce
       the most commonly used:
       
        * :ref:`maintable`: allow to link your webpage to a :ref:`table`
        * :ref:`webpages_py_requires`: allow to include some Genro
          :ref:`components` to your webpage (or, more generally, Python modules)
        * :ref:`webpages_js_requires`: allow to include some javascript functionality
          to your webpage
        * :ref:`css_requires`: allow to include some :ref:`css`
          to your webpage
    
    #. You have to define the :ref:`webpages_main` method (unless you're using an active
       component [#]_)
        
    Let's see now an example of a complete heading of a webpage::
    
        #!/usr/bin/env python
        # encoding: utf-8
        
        class GnrCustomWebPage(object):
            maintable = 'agenda.contact'
            py_requires = 'public:Public,standard_tables:TableHandler'
            css_requires = 'public'
            
            def main(self,root,**kwargs):
                root.div('Hello world!')
                # Here goes the rest of your code...
                
.. _webpages_main:
    
main
====
    
    The main method of a webpage::
    
        def main(self, root, **kwargs):
    
    where:
    
    * the ``root`` is a :ref:`bag` that passes a :ref:`contentpane`. To this contentPane
      you can append every :ref:`webpage element <we>` you need, like
      a div, a :ref:`button` or a more complex object like a :ref:`form` and so on.
      
      If you import the ``public.py`` :ref:`webpages_py_requires` in your GnrCustomWebPage::
      
        py_requires = 'public:Public'
        
      then the ``root`` passes a :ref:`bordercontainer`, not a contentPane.
      
    * in the ``**kwargs`` you will find all the values passed to the client through
      the :ref:`xmlhttprequest`.
      
    .. note:: Usually the ``main`` method is MANDATORY. But, if you use an :ref:`components_active`,
              you may avoid to define it because the ``main`` method is defined within the
              component itself. For more information check the :ref:`introduction to components
              <components_intro>` page
              
.. _webpages_methods:
              
GnrCustomWebPage methods
========================

    TODO
    
.. _onloading_method:
    
onLoading
---------
    
    .. method:: onLoading(self, record, newrecord, loadingParameters, recInfo)
    
    TODO
    
    **Parameters:**
                    * **record** - the value of the saved record contained into a :ref:`bag`.
                      This Bag can be manipulated to alter the data being supplied to the client.
                        
                        Example::
                        
                            0 - (str) id: aBcDeFgHiJkLmNoPrStUvZ  <dtype='A'>
                            1 - (unicode) name: my date <dtype='A' oldValue='None'>
                            2 - (date) data: 2011-06-29  <dtype='D' oldValue='None'>
                            3 - (date) data_to: 2011-07-02  <dtype='D' oldValue='None'>
                            4 - (bool) year: True  <dtype='B' oldValue='None'>
                            5 - (unicode) day: 10  <dtype='L' oldValue='None'>
                            6 - (unicode) month: 5  <dtype='L' oldValue='None'>
                            
                    * **newrecord** - boolean.
                    * **loadingParameters** - :ref:`bag` or dict
                    * **recInfo** - dict. It contains metadata that are used by the framework to determine
                      which behavior is determined in various situations. ``RecInfo`` may contain the
                      following values:
                      
                      ``_alwaysSaveRecord`` -- boolean. Control the behavior during the rescue:
                      
                      * ``False`` (default) -- When a user inserts a new record and immediately saves
                        (without change), then there is no record saved or stored in the database.
                      * ``True`` -- if the user inserts a new record then save without making changes,
                        always created a new record.
                    
.. _onsaving_method:
    
onSaving
--------
    
    .. method:: onSaving(self,recordCluster,recordClusterAttr,resultAttr)
    
    TODO
    
    **Parameters:**
                    * **recordCluster** - 
                    * **recordClusterAttr** - 
                    * **resultAttr** - 
                    
.. _onsaved_method:
    
onSaved
-------
    
    .. method:: onSaved(self,record,resultAttr)
    
    TODO
    
    **Parameters:**
                    * **record** - 
                    * **resultAttr** - 
                    
    .. _webpages_variables:

webpage variables
=================
    
    A webpage variable is a variable with preset features that you need to define
    inside your :ref:`gnrcustomwebpage`
    
    .. note:: The webpages variables act only on the single webpage in which you insert them
    
    Let's see a list of webpages variables divided by their features:
    
    * Components variables: :ref:`webpages_py_requires`
    * CSS variables: :ref:`css_requires`, :ref:`webpages_css_theme`, :ref:`webpages_css_icons`
    * Dojo variables: :ref:`webpages_dojo_source`, :ref:`webpages_dojo_theme`,
      :ref:`webpages_dojo_version`
    * javascript variables: :ref:`webpages_js_requires`
    * Page options: :ref:`webpages_pageOptions`
    * Polling variables: :ref:`webpages_auto_polling`, :ref:`webpages_user_polling`
    * Other variables: :ref:`webpages_auth_tags`, :ref:`webpages_eagers`,
      :ref:`webpages_gnrjsversion`,
      :ref:`maintable`, :ref:`webpages_recordlock`
      
.. _webpages_css_icons:

css_icons
---------

    * Description: a string that allows to change the Genro's page icons theme.
      
    For more information check the :ref:`relative section on CSS page <css_icons>`
    
    .. _css_requires:

css_requires
------------

    * Description: allow to import css files
    * Example::
    
        css_requires = 'my_style'
        
    This line implies that you have created a CSS file called ``my_style.css``
        
    .. note:: The CSS files you want to use must be placed into your "``resources``" folder
              
              * For more information about Genro CSS, please check the :ref:`css` page.
              * For more information about their location in a Genro :ref:`project`,
                please check the :ref:`intro_resources` page.
                
    .. _webpages_css_theme:

css_theme
---------

    * Description: a string that allows to change the Genro's page theme. A Genro theme add some
      CSS features to the Dojo theme you are using in your project (to change the Dojo theme, you
      can only change it through the :ref:`webpages_dojo_theme` webpage variable)
    * Default value: the value you specify in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`.
    * Example::
    
        css_theme = 'aqua'
    
    .. note:: if you want to define a Genro theme in all of your webpages, define it in the
              :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`
              
    .. _webpages_dojo_source:

dojo_source
-----------

    * Description: boolean. Webpage variable for Dojo developers. If ``True``, you can read the
      javascript code decompressed [#]_.
    * Default value: ``False`` (compressed javascript)
    * Example::
    
        dojo_source = True
    
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
    
    * Description: a number that allows to specify the Dojo version of your :ref:`project`.
      You have to write the version supported without the dot (e.g: write '11' for Dojo '1.1')
    * Default value: the value you specify in the :ref:`siteconfig_dojo` tag of your
      :ref:`sites_siteconfig`. If you didn't specify it, the default value is '11'
    * Example::
    
        dojo_version = '11'
        
    .. _webpages_js_requires:

js_requires
-----------

    * Description: allow to import some javascript files
    * Example::
    
        js_requires = 'wizard'
        
    This line implies that you have created a js file called ``wizard.js``
        
    .. note:: The js files you want to use must be placed into your "``resources``" folder
              
              * For more information about Genro js and their location in Genro, please check
                the :ref:`intro_resources` page
                
    .. _webpages_pageOptions:

pageOptions
-----------

    * Description: a dict with page options:
    
        * *openMenu*: if ``True``, the project menu (included in the :ref:`packages_menu` file)
          of the webpage is opened when the page is loaded. Default value is ``True``
        
        * *enableZoom*: if ``True``, TODO
        
    * Example::
    
        pageOptions = {'enableZoom':False,'openMenu':False}
        
    .. _webpages_auto_polling:

auto_polling
------------

    * Description: set a number for auto-polling frequency (units: seconds)
    * Default value: ``30``
    * Example::
    
        auto_polling = 30
        
    .. _webpages_user_polling:

user_polling
------------

    * Description: set a number for user-polling frequency (units: seconds)
    * Default value: ``3``
    * Example::
    
        user_polling = 3
    
    .. _webpages_auth_tags:

auth_tags
---------

    * Description: TODO. Link it to the
      :meth:`~gnr.web._gnrbasewebpage.GnrBaseWebPage.pageAuthTags` method...
    * Example::
    
        TODO
    
    .. _webpages_eagers:

eagers
------

    * Description: a dict that allows to give a hierarchy to the :ref:`bag_resolver` calls of
      a :ref:`relation <relations>`: the relations you put in the eagers are resolved before
      the other ones.
    * Syntax: 
        
        * *key*: ``packageName.tableName``, where:
        
            * ``packageName`` is the name of your package (for more information check the
              :ref:`packages` page)
            * ``tableName`` is the name of the :ref:`table`
            
        * *value*: includes a :ref:`relation <relations>`
        
    * Example::
    
        eagers = {'writers.contracts':'@sy_publisherid'}
    
    .. _webpages_gnrjsversion:

gnrjsversion
------------

    * Description: Genro javascript libraries compatible with the relative Dojo version (type: number).
    * Default value: the value you specify in the :ref:`siteconfig_jslib` tag of your :ref:`sites_siteconfig`.
      If you didn't specify it, the default value is '11' (i.e: Genro JS libraries compatible with Dojo 1.1)
    * Example::
    
        gnrjsversion = '11'
        
    .. _maintable:

maintable
---------
    
    * Description: it allows to specify a :ref:`database table <table>` from which user selects records.
      It becomes the :ref:`dbtable` default value of all the elements of your webpage that support the
      :ref:`dbtable` attribute, that are the :ref:`dbselect`, the :ref:`dbcombobox`, the :ref:`field`
      and the :ref:`formbuilder`
    * Syntax: ``maintable = 'packageName.tableName'``, where:
    
        * ``packageName`` is the name of your package (for more information, check the
          :ref:`packages` page)
        * ``tableName`` is the name of the :ref:`table`
        
    * Example::
    
        maintable = 'agenda.call'
        
    For more information, check the :ref:`dbtable` page.
    
    .. _webpages_recordlock:

recordLock
----------

    * Description: TODO
    * Example: TODO
    
**Footnotes**:

.. [#] For more information on active and passive components, please check the :ref:`components_active_passive` section.
.. [#] Dojo is usually sent compressed to the client. But if you want to debug it, it is better to read it uncompressed.
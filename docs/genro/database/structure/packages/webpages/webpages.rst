.. _webpages_webpages:

=======
webpage
=======

    * :ref:`webpages_GnrCustomWebPage`
    * webpage variables: :ref:`webpages_py_requires`, :ref:`webpages_js_requires`, :ref:`webpages_pageOptions`, :ref:`webpages_css_requires`
    
.. _webpages_GnrCustomWebPage:

Genro Custom Webpage
====================

    The Genro Custom Webpage is add???(a mixin class?) through which you can build your webpages.
    
    A webpage file has to begin with the following declaration line::
    
        class GnrCustomWebPage(object):
        
    After that, you may insert some optional webpage variables. We'll explain them in details later (or, if you prefer, click on their title to go to their documentation section):
        
    * :ref:`webpages_maintable`: allow to create shortcuts for users query
    * :ref:`webpages_py_requires`: allow to include some Genro :ref:`genro_components_index` to your webpage
    * :ref:`webpages_js_requires`: allow to include some javascipt functionality to your webpage
    * :ref:`webpages_pageOptions`: add???
    * :ref:`webpages_css_requires`: allow to include some CSS elements to your webpage
    
    After that, you have to define the main method (unless you're using an active component!! [#]_)
        
    Let's see now an example of a complete heading::
    
        #!/usr/bin/env python
        # encoding: utf-8
        # Created by me on 2011-01-25.
        # Copyright (c) 2011 Softwell. All rights reserved.
        
        class GnrCustomWebPage(object):
            maintable = 'agenda.contact'
            py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'
            css_requires = 'public'
            
            def main(self,root,**kwargs):
                bc = root.borderContainer()
                bc.div('Hello!')
                # Here goes the rest of your code...
                
    In the following sections we describe the webpages variables.
    
.. _webpages_maintable:

maintable
=========

    add???
    
.. _webpages_py_requires:

py_requires
===========

    add???
    
.. _webpages_js_requires:

js_requires
===========

    add???
    
.. _webpages_pageOptions:

pageOptions
===========

    add???
    
.. _webpages_css_requires:

css_requires
============

    With the *css_requires* you can specify the path of your CSS files ...add???

.. _webpages_dojo_version:

dojo_version
============

    add???

**Footnotes**:

.. [#] For more information on active and passive components, please check the :ref:`components_active_passive` documentation section.
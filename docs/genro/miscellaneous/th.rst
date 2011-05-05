.. _genro_th:

====
 th
====

    Welcome!
    
    This is a temporary page to explain the new ``th`` methods. It will change
    progressively with time until the method will stabilize.
    
    If you need a specific help on a particular issue, please click on one of
    the following links; otherwise, read the complete page.
    
    * :ref:`th_tables`
    * :ref:`th_page`:
    
        * :ref:`page_py_requires`
        
    * :ref:`th_tablehandlers`:
    
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_palette`
        * :ref:`th_stack`
        
    * :ref:`th_old_new`:
    
        * :ref:`old_new_index`
        * :ref:`old_new_resources`
    
.. _th_tables:

tables
======

    add???

.. _th_page:

webpages
========

    add???

.. _page_py_requires:

``py_requires``
---------------
    
    In order to use the ``th`` component in your :ref:`webpages_webpages`, please add
    the following ``py_requires``::
    
        py_requires = "public:TableHandlerMain"
        
    For more informations on ``py_requires``, please check the :ref:`webpages_py_requires`
    documentation section.
    
.. _th_tablehandlers:

tablehandlers
=============

    In this section we explain all the tablehandler that you can use.
    
.. _th_border:

th_borderTableHandler
---------------------

    .. method:: pane.simpleTextarea([**kwargs])
    
.. _th_dialog:

th_dialogTableHandler
---------------------

    .. method:: th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,[**kwargs])
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``None``
    * *dialog_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_palette:

th_paletteTableHandler
----------------------

    .. method:: th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *palette_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_stack:

th_stackTableHandler
--------------------

    add???
    
.. _th_old_new:

convert your project into the new mode
======================================

    .. warning:: completely to do!! (add???)
    
    This section wants to explain what modifies you have to do to pass from the old mode
    to the new one.
    
.. _old_new_index:

index
-----

    add???

.. _old_new_resources:
    
resources
---------

    if you have some ``_resources`` folders in your webpages, please move them into add???
    
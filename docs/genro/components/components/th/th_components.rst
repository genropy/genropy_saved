.. _th_types:

===================
TableHandler: types
===================

    *Last page update*: |today|
    
    * :ref:`th_types_intro`:
    
        :ref:`th_common_attributes`
        
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_page`
        * :ref:`th_palette`
        * :ref:`th_plain`
        * :ref:`th_stack`
        
    * :ref:`th_formhandler`
    
    * :ref:`th_iframe_types`:
    
        :ref:`th_iframe_common_attributes`
    
        * :ref:`th_thiframe`
        * :ref:`th_iframedialog`
        * :ref:`th_iframedispatcher`
        * :ref:`th_iframepalette`
    
    * :ref:`th_linker_type`:
    
        :ref:`th_linker_common_attributes`
    
        * :ref:`th_linker_base`
        * :ref:`th_linkerbar`
        * :ref:`th_linkerbox`
        
    * :ref:`th_ig`
    
.. _th_types_intro:

TableHandler types - introduction
=================================

    In this section we explain all the TableHandler types. A TableHandler type is a
    different way to show the :ref:`view_data` and the :ref:`data_entry`.
    
    In particular:
    
    * :ref:`th_border`: show the ``view-data window`` and the ``data-entry window``
      in a single page
    * :ref:`th_dialog`: show the ``data-entry window`` in a dialog that appears over the
      ``view-data window``
    * :ref:`th_palette`: show the ``data-entry window`` in a :ref:`palette <palette>`
      that appears over the ``view-data window``
    * :ref:`th_plain`: show only the ``view-data window``. User can't modify records
    * :ref:`th_stack`: show the ``data-entry window`` and the ``view-data window``
      in two different stack
      
.. _th_common_attributes:

TableHandler common attributes
------------------------------
    
    Some attributes are common to every of these types and we describe those
    attributes here:
    
    * *pane*: MANDATORY - the :ref:`contentpane` to which the TableHandler
      is linked
      
      .. note:: we suggest you to link a TableHandler to a :ref:`contentpane`;
                avoid a :ref:`bordercontainer`, a :ref:`tabcontainer` or
                other :ref:`layout elements <layout>` (if you use them, pay
                attention to use the correct attributes of the layout elements)
      
    * *nodeId*: the TableHandler :ref:`nodeid`. It is not a mandatory attribute: if you
      don't need a specific name for the nodeId, then it is handled automatically
      
      .. warning:: if you have more than a TableHandler in the same page related to the
                   same :ref:`table` you must MANDATORY define a different nodeId for
                   every TableHandler of that page
                   
    * *table*: the path of the :ref:`table` linked to your TableHandler. It is MANDATORY
      unless you use the relation attribute. For more information, check the
      :ref:`th_relation_condition` example. The syntax is::
      
        table = 'packageName.tableName'
        
    * *th_pkey*: add???
    * *datapath*: the path of your data. If you don't need a specific datapath
      it is handled automatically
      
      .. warning:: if you have more than a TableHandler in the same page related to the
                   same :ref:`table` AND they have the same path level, then you must
                   define MANDATORY a different datapath for every TableHandler of that
                   page that comes into conflict
                   
      For more information:
      
        * on "datapath" attribute, check the :ref:`datapath` page
        * on TableHandler path levels, check the :ref:`th_map` page
      
    * *formResource*: allow to change the default :ref:`th_form_class`.
      Check the :ref:`th_formresource` section for more information
    * *viewResource*: allow to change the default :ref:`th_view_class`.
      Check the :ref:`th_viewresource` section for more information.
    * *formInIframe*: add???
    * *readOnly*: boolean. If ``True``, the TableHandler is in read-only mode,
      so user can visualize records and open the :ref:`th_form_class`, but
      he can't add/delete/modify records. Default value is ``True`` or ``False``
      depending on the widget (check it in their method definition).
    * *default_kwargs*: you can add different kwargs:
        
        * *virtualStore*: boolean. If it is set to ``True``, it introduces two features:
            
            #. Add the :ref:`th_query_bar` (if it is not yet visualized)
            #. Optimize the time to give the result of a user query: if the user query
               returns a huge set of records as result, the virtualStore load on the client
               only the set of records that user sees in his window, and load more records
               when user scrolls through the result list.
               
        * *relation*: an alternative to the *table* and the *condition* attributes. For more
          information, check the :ref:`th_relation_condition` sections
        * *condition*: MANDATORY unless you specify the relation attribute. Check the
          :ref:`th_relation_condition` section for more information.
        * *condition_kwargs*: the parameters of the condition. Check the
          :ref:`th_relation_condition` section for more information.
        * *grid_kwargs*: add???.
        * *hiderMessage*: add???.
        * *pageName*: add???.
        * *pbl_classes*: if ``True``, modify the CSS attributes of the top bar of a :ref:`grid`.
          For more information, check the :ref:`pbl_classes` page
                              
.. _th_border:

borderTableHandler
------------------

    **Definition:**
    
    .. method:: TableHandler.th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`bordercontainer`, the borderTableHandler shows the
    :ref:`view_data` and the :ref:`data_entry` in a single page.
    
    .. image:: ../../../_images/components/th/border_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.borderTableHandler(...) #not th_borderTableHandler !
    
    **Attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the borderTableHandler are listed here:
    
    * *widget_kwargs*: add???
    * *loadEvent*: add???
    * *viewRegion*: add?
    * *formRegion*: add?
    * *vpane_kwargs*: allow to set the attributes of the :ref:`view_data`
      
      In particular, you have the following options:
      
      * *vpane_region*: specify the region occupied by the View class. As for the
        :ref:`bordercontainer`, you may choose between these values: top, left,
        right, bottom, center. By default, the View class has ``vpane_region='top'``
      * *vpane_width* (OR *vpane_height*): specify the width (or the height) occupied
        by the View class (tip: we suggest you to use a percentage, like '30%')
        By default, the View class has ``vpane_height='50%'``
        
      Example::
      
        vpane_region='left',vpane_width='36%'
        
    * *fpane_kwargs*: allow to set the attributes of the :ref:`data_entry`
      
      In particular, you have the following options:
      
      * *fpane_region*: specify the region occupied by the Form class. As for the
        :ref:`bordercontainer`, you may choose between these values: top, left,
        right, bottom, center. By default, the Form class has ``fpane_region='bottom'``
      * *fpane_width*: specify the width occupied by the Form class (tip: we
        suggest you to use a percentage, like '30%') By default, the Form class has
        ``fpane_height='50%'``
      
      Example::
    
          vpane_region='right',vpane_width='70%'
      
.. _th_dialog:

dialogTableHandler
------------------

    **Definition:**
    
    .. method:: TableHandler.th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    The dialogTableHandler shows the :ref:`data_entry` in a dialog over
    the :ref:`view_data`.
    
    .. image:: ../../../_images/components/th/dialog_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.dialogTableHandler(...) #not th_dialogTableHandler !
    
    **Attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the dialogTableHandler are listed here:
    
    * *dialog_kwargs*: there are many options:
    
        * *dialog_height*: MANDATORY - define the dialog height
        * *dialog_width*: MANDATORY - define the dialog width
        * *dialog_title*: define the dialog title
        
      Example::
      
        dialog_height='100px',dialog_width='300px',dialog_title='Customer'
        
.. _th_page:

pageTableHandler
----------------
    
    **Definition:**
    
    .. method:: TableHandler.th_pageTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,formUrl=None,viewResource=None,default_kwargs=None,dbname=None,**kwargs)
    
    **Description:**
    
    The pageTableHandler add???
    
    add??? add image!
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.pageTableHandler(...) #not th_pageTableHandler !
    
    **Attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the pageTableHandler are listed here:
    
    * *dbname=None*: add???
    * *formUrl=None*: add???
    
    Example::
    
        add???
    
.. _th_palette:

paletteTableHandler
-------------------
    
    **Definition:**
    
    .. method:: TableHandler.th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    The paletteTableHandler shows the :ref:`data_entry` in a palette
    over the :ref:`view_data`.
    
    .. image:: ../../../_images/components/th/palette_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.paletteTableHandler(...) #not th_paletteTableHandler !
    
    **Attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the paletteTableHandler are listed here:
    
    * *palette_kwargs*: MANDATORY - define the height and the width of the palette.
      
      Example::
      
        palette_height='100px'; palette_width='300px'
        
.. _th_plain:

plainTableHandler
-----------------
    
    **Definition:**
    
    .. method:: TableHandler.th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,viewResource=None,readOnly=True,**kwargs)
    
    **Description:**
    
    With the plainTableHandler you have only the :ref:`view_data`. Also, by default
    user can't modify, add and delete records (infact, the *readOnly* attribute is set
    to ``True``). Set it to ``False`` to change this default behavior.
    
    .. image:: ../../../_images/components/th/plain_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.plainTableHandler(...) #not th_plainTableHandler !
    
    **Attributes**:
    
    The attributes that belong to every TableHandler are described in the :ref:`th_common_attributes`
    section. There are not attributes belonging only to the plainTableHandler
    
.. _th_stack:

stackTableHandler
-----------------
    
    **Definition:**
    
    .. method:: TableHandler.th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`stackcontainer`, the stackTableHandler shows the
    :ref:`view_data` and the :ref:`data_entry` in two different pages.
    
    Remembering the Dojo StackContainer definition: *<<A container that has multiple children,*
    *but shows only one child at a time (like looking at the pages in a book one by one).>>*
    
    .. image:: ../../../_images/components/th/stack_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.stackTableHandler(...) #not th_stackTableHandler !
    
    **Attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the stackTableHandler are listed here:
    
    * *widget_kwargs*: add???.
    
.. _th_formhandler:

thFormHandler
=============

    **Definition:**
    
    .. method:: TableHandler.th_thFormHandler(self,pane,formId=None,table=None,formResource=None,startKey=None,formCb=None,store_kwargs=None,default_kwargs=None,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    add???
    
.. _th_iframe_types:

iframe types
============

    add???
    
    They are:
    
    * :ref:`th_thiframe`
    * :ref:`th_iframedialog`
    * :ref:`th_iframedispatcher`
    * :ref:`th_iframepalette`
    
.. _th_iframe_common_attributes:

iframe common attributes
------------------------

    Some attributes are common to every of these types and we describe those
    attributes here... add???
    
.. _th_thiframe:

thIframe
--------
    
    **Definition:**
    
    .. method:: TableHandler.th_thIframe(self,pane,method=None,src=None,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    * *pane*: add???.
    * *method*: add???.
    * *src*: add???.
    
.. _th_iframedialog:

IframeDialog
------------
    
    **Definition:**
    
    .. method:: ThLinker.th_thIframeDialog(self,pane,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    add???
    
.. _th_iframedispatcher:

iframedispatcher
----------------
    
    **Definition:**
    
    .. method:: TableHandler.rpc_th_iframedispatcher(self,root,methodname=None,pkey=None,table=None,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    * *root*: add???
    * *methodname*: add???
    * *pkey*: add???
    * *table*: add???
    
.. _th_iframepalette:

IframePalette
-------------
    
    **Definition:**
    
    .. method:: ThLinker.th_thIframePalette(self,pane,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    add???
    
.. _th_linker_type:

linker types
============
    
    add??? (introduction)
    
    They are:
    
    * :ref:`th_linker_base`
    * :ref:`th_linkerbar`
    * :ref:`th_linkerbox`
    
.. _th_linker_common_attributes:

linker common attributes
------------------------
    
    Some attributes are common to every of these types and we describe those
    attributes here:
    
    * *pane*: MANDATORY - the :ref:`contentpane` to which the TableHandler
      is linked.
    * *field*: a :ref:`field`; through this object the linker becomes related to the
      :ref:`table` to which the field belongs to.
    * *newRecordOnly*: add???
    * *dialog_kwargs*: there are many options:
    
        * *dialog_height*: MANDATORY - define the dialog height
        * *dialog_width*: MANDATORY - define the dialog width
        * *dialog_title*: define the dialog title
        
      Example::
      
        dialog_height='100px',dialog_width='300px',dialog_title='Customer'
        
.. _th_linker_base:

linker
------
    
    **Definition:**
    
    .. method:: ThLinker.th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,openIfEmpty=None,embedded=True,dialog_kwargs=None,default_kwargs=None,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linker are listed here:
    
    * *formResource*: allow to change the default :ref:`th_form_class`. Check the
      :ref:`th_formresource` section for more information.
    * *formUrl*: add???
    * *table*: the database :ref:`table` to which the th_linker refers to
    * *openIfEmpty*: add???
    * *embedded*: add???
    
.. _th_linkerbar:

linkerBar
---------
    
    **Definition:**
    
    .. method:: ThLinker.th_linkerBar(self,pane,field=None,label=None,table=None,_class='pbl_roundedGroupLabel',newRecordOnly=True,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linkerBar are listed here:
    
    * *label*: the label of the linkerBar
    * *table*: the database :ref:`table` to which the th_linkerBar refers to
    * *_class*: the CSS style
    
.. _th_linkerbox:

linkerBox
---------
    
    **Definition:**
    
    .. method:: ThLinker.th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,newRecordOnly=None,openIfEmpty=None,_class='pbl_roundedGroup',label=None,**kwargs)
    
    **Description:**
    
    add???
    
    **Attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linkerBox are listed here:
    
    * *template*: add???
    * *frameCode*: add???
    * *formResource*: allow to change the default :ref:`th_form_class`. Check the
      :ref:`th_formresource` section for more information.
    * *openIfEmpty*: add???
    * *_class*: the CSS style
    * *label*: the th_linkerBox label
    
        **Example**
        
        add??? example explanation
        
        add??? Explain of the tpl folder --> resources/tables/*TableName*/tpl/default.html
        
        ::
        
            linkerBox('customer_id',
                       dialog_width='300px',dialog_height='260px',dialog_title='Customer',
                       validate_notnull=True,validate_notnull_error='!!Required',
                       newRecordOnly=True,formResource=':MyForm')
                       
.. _th_ig:

includedGrid
============

    The includedGrid is a :ref:`grid` that allows the inline editing. So, the insertion
    or the modify of records is handled inside the grid
    
    .. note:: for a complete explanation of the includedGrid, check the :ref:`includedgrid` section
        
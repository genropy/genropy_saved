.. _selectionbrowser:

================
selectionBrowser
================

    *Last page update*: |today|
    
    .. warning:: deprecated since version 0.7
    
    .. note:: summary of the component requirements:
              
              * It is a :ref:`components_standard`.
              * It is a :ref:`components_passive`. Its :ref:`webpages_py_requires` is::

                    py_requires='public:Public'
                    
    .. method:: selectionBrowser(self, pane, rowcount, indexPath=None)
    
    The selectionBrowser is a preset tool to navigate through records
    
        **Parameters**: 
        
                        * **pane** - the :ref:`contentpane` to which to which you have to append
                          the selectionBrowser
                        * **row_count** - the row number
                        
    **image**:
    
    .. image:: ../../_images/components/macrowidgets/selectionbrowser.png
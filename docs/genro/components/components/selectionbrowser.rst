.. _selectionbrowser:

================
selectionBrowser
================

    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is a :ref:`components_standard`.
              * It is a :ref:`components_passive`. Its :ref:`webpages_py_requires` are::

                    py_requires='public:Public'
                    
    * :ref:`sb_def`
    * :ref:`sb_descr`
    * :ref:`sb_examples`: :ref:`sb_examples_simple`
    
.. _sb_def:

definition
==========

    .. method:: selectionBrowser(self, pane, rowcount, indexPath=None)
    
    The selectionBrowser is a preset tool to navigate through records
    
        **Parameters**: 
        
                        * **pane** - the :ref:`contentpane` to which to which you have to append
                          the selectionBrowser
                        * **row_count** - add???
                        * **indexPath** - add???
                        
.. _sb_descr:

description
===========

    .. image:: ../../_images/components/macrowidgets/selectionbrowser.png
    
    add???
    
.. _sb_examples:

Examples
========

.. _sb_examples_simple:

simple example
--------------
    
    Here is a simple example::
    
        # -*- coding: UTF-8 -*-
        
        class GnrCustomWebPage(object):
            py_requires = """public:Public"""

            def main(self, root, **kwargs):
                """selectionBrowser"""
                pane = root.contentPane(height='200px',datapath='root_example')
                self.selectionBrowser(pane,rowcount=0,indexPath=0)
                
                #add??? add a grid with columns and rows...
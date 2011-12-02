.. _iv:

============
includedView
============

    *Last page update*: |today|
    
    .. note:: includedView features:
              
              * **Type**: :ref:`Genro widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`iv_def`
    * :ref:`iv_examples`:
    
        * :ref:`iv_examples_simple`
        
.. _iv_def:

definition
==========

    .. method:: pane.includedView([**kwargs])
    
    It is the widget version of the :ref:`includedview` component. Pay attention that
    the includedView component is deprecated, while this widget is the actual way to
    create a :ref:`grid`
    
.. _iv_examples:

examples
========

.. _iv_examples_simple:

simple example
--------------

    * `includedView [basic] <http://localhost:8080/webpage_elements/grids/includedview/1>`_
      
      .. note:: example elements' list:

                * **classes**: :ref:`bag`, :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`datarpc`
                * **methods**: :meth:`~gnr.core.gnrbag.Bag.setItem`, :meth:`~gnr.web.gnrwebstruct.struct_method`
                * **webpage variables**: :ref:`webpages_py_requires`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """includedview"""

        from gnr.core.gnrbag import Bag
        from gnr.core.gnrdecorator import public_method

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerBase"

            def test_1_simple(self, pane):
                """includedview - js widget"""
                pane = pane.contentPane(height='80px')
                pane.includedView(storepath='.grid.data', struct=self.gridStruct(), splitter=True)
                pane.dataRpc('.grid.data', self.gridData, _onStart=True)

            @public_method
            def gridData(self):
                data = Bag()
                data.setItem('r1', None, name='Mark Smith', sex='M', birthday='1980-06-04::D', height=170)
                data.setItem('r2', None, name='Ann Brown', sex='F', birthday='1960-09-21::D', height=1730.45)
                return data

            def gridStruct(self):
                struct = Bag()
                r = struct.child('view').child('rows')
                r.child('cell', field='name', width='100%', name='Name')
                r.child('cell', field='sex', width='4em', name='Sex')
                r.child('cell', field='height', width='10em', name='Height', text_align='right')
                r.child('cell', field='birthday', width='10em', name='Birthday', format_date='short')
                return struct
        
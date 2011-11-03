.. _periodcombo:

===========
periodCombo
===========

    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is a :ref:`components_standard`.
              * It is a :ref:`components_passive`. Its :ref:`webpages_py_requires` is::

                    py_requires='public:Public'
                    
    * :ref:`pc_def`
    * :ref:`pc_descr`
    * :ref:`pc_examples`: :ref:`pc_examples_simple`
    
.. _pc_def:

definition
==========

    .. method:: periodCombo(self, fb, period_store=None, value=None, lbl=None, **kwargs)
    
    The periodCombo is a :ref:`filteringselect` that allows to choose a time interval
    
        **Parameters**: 
        
                        * **fb** - MANDATORY. The :ref:`formbuilder` to which you have to append
                          the periodCombo
                        * **period_store** - the store path. Default value is ``.period``
                        * **value** - the path of the value (more information in the :ref:`datapath`
                          section). Default value is ``^.period_input``
                        * **lbl** - the periodCombo :ref:`label <lbl_formbuilder>`. Default value is ``Period``
                        
.. _pc_descr:

description
===========

    As you can see in the following image, there are many preset period (taken from the
    :meth:`decodeDatePeriod <gnr.core.gnrdate.decodeDatePeriod>` method):
    
    .. image:: ../../_images/components/macrowidgets/periodcombo.png
    
    where:
    
    * 2011 is the actual year showed in a numerical string
    * 2010 is the last year showed in a numerical string
    
.. _pc_examples:

Examples
========

.. _pc_examples_simple:

simple example
--------------
    
    Here is a simple example::
    
        # -*- coding: UTF-8 -*-
        
        class GnrCustomWebPage(object):
            py_requires = """public:Public"""

            def main(self, root, **kwargs):
                pane = root.contentPane(height='200px',datapath='root_example') # remember to put a datapath!
                fb = pane.formbuilder(cols=2)
                self.periodCombo(fb,lbl='!!Period',period_store='.period')
                fb.div(value='^.period.period_string', _class='period',font_size='.9em',font_style='italic')
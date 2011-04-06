.. _genro_dataformula:

===========
dataFormula
===========

    The ``dataFormula`` belongs to :ref:`controllers_client` family.

    * :ref:`dataformula_def`
    * :ref:`dataformula_examples`

.. _dataformula_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dataFormula
        :noindex:
    
    **commons attributes**:
    
        For commons attributes (*_init*, *_onStart*, *_timing*) see controllers' :ref:`controllers_attributes`
        
.. _dataformula_examples:

Examples
========

    Example::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2)
                fb.horizontalSlider(lbl='Base',value='^base',width='200px',minimum=1,maximum=100)
                fb.numberTextBox(value='^base',places=2)
                fb.horizontalSlider(lbl='Height',value='^height',width='200px',minimum=1,maximum=100)
                fb.numberTextBox(value='^height',places=2)
                fb.dataFormula('area','base * height', base='^base', height='^height')
                fb.numberTextBox(lbl='Area',value='^area',places=2,border='2px solid grey',padding='2px')
    
    .. note:: dataFormula does not have to be necessarily a mathematical formula!

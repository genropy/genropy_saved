.. _label:

=====
label
=====
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *label* attribute is supported by:
              
              * :ref:`button`
              * :ref:`dropdownbutton`
              * :ref:`togglebutton`
              
              When you have a widget that doesn't support the *label* attribute, you
              can however give a label to it by inserting the widget into a :ref:`formbuilder`.
              For more information, check the :ref:`lbl_formbuilder` section
              
    * :ref:`label_def`
    * :ref:`lbl_formbuilder`
    
.. _label_def:

description
===========

    The *label* attribute allows to add a label to your widget
    
.. _lbl_formbuilder:

label through formbuilder
=========================

    If your widget doesn't support the *label* attribute but you want to give to it a label, you have to:
    
        #. create a :ref:`formbuilder`
        #. append your widget to the formbuilder
        #. use the formbuilder's *lbl* attribute on your widget.
        
    **Example** (with :ref:`combobox`)::
    
            class GnrCustomWebPage(object):
                def test_1_values(self,pane):
                    bc = pane.borderContainer(datapath='test1')
                    fb = bc.formbuilder()
                    fb.combobox(value='^.record.values',values='Football,Golf,Karate',
                                lbl='loaded from values')
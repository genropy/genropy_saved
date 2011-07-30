.. _label:

=====
label
=====
    
    *Last page update*: |today|
    
    * :ref:`label_def`
    * :ref:`label_validity`: :ref:`lbl_formbuilder`
    
.. _label_def:

definition and description
==========================

    Allow to add a label to your widget.
    
.. _label_validity:

validity
========
    
    Not all the widgets support it. In every widget page is specified if the attribute is
    supported or not. In the next section, we describe you the way to turn around the problem.
    
.. _lbl_formbuilder:

label through formbuilder
-------------------------

    If your widget doesn't support the *label* attribute but you want to give to it a label, you have to:
    
        #. create a form (use the :ref:`formbuilder` form widget)
        #. append your widget to the formbuilder
        #. use the formbuilder's *lbl* attribute on your widget.
        
    **Example** (with :ref:`combobox`)::
    
            class GnrCustomWebPage(object):
                def test_1_values(self,pane):
                    bc = pane.borderContainer(datapath='test1')
                    fb = bc.formbuilder()
                    fb.combobox(value='^.record.values',values='Football,Golf,Karate',
                                lbl='loaded from values')
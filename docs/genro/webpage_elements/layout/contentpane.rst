.. _contentpane:

===========
contentPane
===========
    
    *Last page update*: |today|
    
    **Type**: :ref:`layout widget <layout>`
    
    .. note:: The Genro contentPane has been taken from Dojo without adding any modifies. In this page
              you will find some interesting features that we want to point up. For more information,
              check the Dojo's contentPane documentation.
    
    * :ref:`cp_definition`
    * :ref:`cp_attributes`
    * :ref:`cp_examples`:
    
        * :ref:`cp_example_simple`
        * :ref:`cp_example_form`
    
.. _cp_definition:

Definition
==========

    .. method:: pane.contentPane([**kwargs])

    A contentPane_ is a Dojo widget that can be used as a standalone widget or as a baseclass for
    other widgets. Don’t confuse it with an iframe, it only needs/wants document fragments.

.. _cp_attributes:

Attributes
==========

    **contentPanes attributes**:

        There aren't particular attributes.

    **commons attributes**:

        For commons attributes, see :ref:`layout_common_attributes`.

.. _cp_examples:

Examples
========

.. _cp_example_simple:

simple example
--------------

    Here we show you a simple example of a ``contentPane``::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.div('hello!')
                
    You're wondering about where is the contentPane? It is passed through the root.
    
.. _cp_example_form:
    
form example
------------

    We show you now a :ref:`form`, built through a :ref:`bordercontainer`
    and three contentPanes::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = root.borderContainer(margin='3px')
                top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
                top.div('!!Registry records',_class='pbl_roundedGroupLabel')
                fb = top.formbuilder(margin_left='10px',margin_top='1em',width='370px',cols=2)
                fb.textbox(lbl='Name')
                fb.textbox(lbl='Surname')
                fb.textbox(lbl='Email')
                fb.textbox(lbl='Telephone')
                fb.textbox(lbl='Tax code')
                fb.textbox(lbl='VAT')
                fb.textbox(lbl='Fax',colspan=2,width='100%')
                fb.textArea(lbl='Notes',colspan=2,width='100%')
                fb.combobox(lbl='Company role',values='emplyee, freelance, manager, owner')
                
                left = bc.contentPane(region='left',_class='pbl_roundedGroup',margin='1px',width='50%')
                left.div('!!Staff records',_class='pbl_roundedGroupLabel')
                fb = left.formbuilder(margin_left='10px',margin_top='1em',width='370px')
                fb.textbox(lbl='Internal number',placeholder='example: 202')
                fb.textbox(lbl='Notes',placeholder='Write your notes here')
                
                right = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='1px',width='50%')
                right.div('!User records',_class='pbl_roundedGroupLabel')
                fb = right.formbuilder(margin_left='10px',margin_top='1em',width='370px')
                fb.textbox(lbl='Username')
                fb.textbox(lbl='md5pwd')
                fb.textbox(lbl='Auth tags')
                fb.textbox(lbl='Avatar rootpage')
                
.. _childname:

=========
childname
=========

    *Last page update*: |today|
    
    .. note:: **validity** - the *childname* attribute is supported by:
              
              * every :ref:`cell <cells>`
              * every :ref:`controller <controllers>`
              * every :ref:`form widget <form_widgets>`
              * every :ref:`layout widget <layout>`
              * it works also on :ref:`iframe`, :ref:`menu`, :ref:`slotBar <slotbar>`,
                :ref:`slotToolbar <slotbar>`, :ref:`tree`
                
    * :ref:`childname_def`
    * :ref:`childname_examples`
    
.. _childname_def:

description
===========
    
    The *childname* attribute allow to give an alternative name to a :ref:`webpage element
    <webpage_elements_index>`.
    
    You have to define the *childname* as an attribute of one of your elements, then you
    can attach any element to the element with the *childname* attribute (add??? explain better...)
    
    This attribute is thought to speed up your programming work and...??? (explain of the chain of the
    nodeId that you can call through the "/")
    
.. _childname_examples:

examples
========
    
    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                tc = root.tabContainer(height='100px')
                for k in range(6):
                    tc.borderContainer(title='pane %i' %k, childname='tab_%i' %k)
                for k in range(3):
                    bc = tc.getAttach('tab_%i' %k)
                    bc.contentPane(region='top',childname='top',height='30px',background='red')
                    bc.contentPane(region='center',childname='center',background='gray')
                tc.tab_2.center.div('Here I am')
                tc.tab_3.div('Hello!')
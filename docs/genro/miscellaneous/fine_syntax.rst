.. _genro_fine_syntax:

===========
Fine syntax
===========

    :ref:`syntax_attributes`:
    
    * :ref:`attributes_attachname`
    
    :ref:`syntax_decorators`:
    
    * :ref:`decorators_struct_method`
    
.. _syntax_attributes:

Attributes
==========

.. _attributes_childname:

_childname
----------

    .. module:: gnr.web.gnrwebstruct.GnrDomSrc
    
    The *_childname* attribute allow to give an alternative name for a :ref:`genro_webpage_elements_index`.
    
    You have to define the *_childname* as an attribute of one of your elements, then
    you have to use the :meth:`getAttach`(add???) method to append it to its layout father.
    
    This attribute is thought to speed up your programming work and...??? (explain of the chain of the
    nodeId that you can call through the "/")
    
    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                tc = root.tabContainer(height='100px')
                for k in range(6):
                    tc.borderContainer(title='pane %i' %k, _attachname='tab_%i' %k)
                for k in range(3):
                    bc = tc.getAttach('tab_%i' %k)
                    bc.contentPane(region='top',_attachname='top',height='30px',background='red')
                    bc.contentPane(region='center',_attachname='center',background='gray')
                tc.tab_2.center.div('Here I am')
                tc.tab_3.div('Hello!')
                
    .. _syntax_decorators:

Decorators
==========

.. _decorators_struct_method:

struct_method
-------------

    add???
    
    py_requires='public:Public' (do they really need?)
    
    bc.linee.pannelloLinee()
    
    @struct_method
    def pannelloLinee(…):
    
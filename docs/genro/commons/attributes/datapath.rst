.. _datapath:

========
datapath
========
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *datapath* attribute is supported by:
              
              * the :ref:`formbuilder`
              * every :ref:`layout widget <layout>`
              * it works also on :ref:`iframe`, :ref:`menu`, :ref:`slotBar <toolbar>`,
                :ref:`slotToolbar <toolbar>`, :ref:`tree`
                
              Indeed, you can give the *datapath* attribute to more objects of the previous list,
              but it is useful give this attribute only to the objects that may contain other objects.
              
              So, it is reasonable to give it to a container object (like a :ref:`bordercontainer`) but
              (usually!) it is not reasonable use it on a :ref:`button`
              
    * :ref:`datapath_symbolic`
    * :ref:`datapath_specials`:
    
        * :ref:`attributes_path`
        * :ref:`form_path`
        * :ref:`parent_path`
        
    The *datapath* is an attribute used to create a hierarchy in your data
    
    The element on which you apply this attribute will become the father of his children elements.
    
    A child element can support both a *relative path* (relative to its father) or an *absolute
    path*: in every case, to define the path of a child you have to use the *value* attribute
    
    **Syntax**:
    
    * ``absolutePathInDatastore``: your data will be saved in its absolute path.
    * ``.relativePathInDatastore``: your path will be relative. Pay attention that you can use
      this attribute only for a child object linked to a father on which the *datapath*
      attribute is defined.
      
    Every dot (``.``) that you use have the meaning of a new subfolder; for example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = root.borderContainer(datapath='test1')
                bc.numberTextbox(value='^.number1')
                bc.numberTextbox(value='^number2')
                bc.numberTextbox(value='^.number.number3')
                
    The first numberTextbox will have the following path: ``test1/number1`` (this is a relative path).
    The second one will have the following path: ``number2`` (that is an absolute path!). The third
    one will have the following path: ``test1/number/number3``
    
.. _datapath_symbolic:

symbolic datapath
=================

    A symbolic datapath is a path that allows to assign to an object the same path of another object.
    
    Let's suppose to have two objects (called ``A`` and ``B``): the ``A`` object is the one you want
    to assign the path of the ``B`` object. To create a symbolic datapath, you have to give to the
    ``A`` object a datapath that begins with the sharp character (``#``) followed by a string equal
    to the nodeId value (string) of the ``B`` object.
    
        Example::
    
            add???
            
.. _datapath_specials:

special paths
=============

    There are some special syntaxes that allows you to move through the values' path;
    they are:
    
    * :ref:`attributes_path`: allow to access to an attribute
    * :ref:`form_path`: allow to access to the ... add???
    * :ref:`parent_path`: allow to access to the superior path level
    
.. _attributes_path:

attributes path
---------------

    In order to access to an attribute (of a :ref:`bagnode`), you can ...add???
    
.. _form_path:

#FORM path
----------
    
    add???
    
    ``#FORM.pkey`` is the current pkey of the record
    
.. _parent_path:

parent path
-----------

    add???
    
    You can access to the parent path through the ``#parent`` syntax.
    
    Example::
    
    add??? explanation!
    
        value='^.#parent.batch_note'
        
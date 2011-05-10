.. _genro_datapath:

========
datapath
========

    * :ref:`datapath_def`
    * :ref:`datapath_validity`
    
.. _datapath_def:

Definition and description
==========================

    *datapath* is an attribute used to create a hierarchy of your data's addresses into
    the :ref:`genro_datastore`.
    
    The element on which you apply this attribute will be able to become the father of other
    elements.
    
    In the child elements we can specify through the *value* attribute either to set a relative
    path to the father, or an absolute path.
    
    The syntax:
    
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
    one will have the following path: ``test1/number/number3``.
    
.. _datapath_validity:

Validity
========

    You can give the *datapath* attribute to each object, but it is useful give this attribute only
    to the objects that contain other objects. For example, you can give it to the container objects,
    that are :ref:`genro_accordioncontainer`, :ref:`genro_bordercontainer`, :ref:`genro_stackcontainer`,
    :ref:`genro_tabcontainer`, or if you create a :ref:`genro_form` you can give it to a :ref:`genro_formbuilder`.
    
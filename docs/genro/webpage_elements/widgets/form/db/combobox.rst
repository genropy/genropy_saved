	.. _genro_combobox:

========
comboBox
========

    .. note:: The Genro combobox has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's combobox_ documentation.

    .. _combobox: http://docs.dojocampus.org/dijit/form/ComboBox

    * :ref:`combobox_def`
    * :ref:`combobox_description`
    * :ref:`combobox_attributes`
    * :ref:`combobox_examples`: :ref:`bag_way`, :ref:`values-attribute`
    
.. _combobox_def:

Definition
==========

    .. method:: pane.combobox([**kwargs])

.. _combobox_description:

Description
===========

    Combobox is a graphical user widget that permits the user to select a value from multiple options.
    
    In combobox you have to provide a list of acceptable values: to upload them, you can use a Bag_ or you can use the values_ attribute. As the user types, partially matched values will be shown in a pop-up menu below the input text box. Like an input text field, user can also type values that doesn't belong to the list of accetable ones.
    
    The combobox looks like a :ref:`genro_filteringselect`: the only difference is that it doesn't support keys.
    
.. _combobox_attributes:
    
Attributes
==========
    
    **combobox attributes**:
    
    * *hasDownArrow*: If True, create the selection arrow. Default value is ``True``.
    * *ignoreCase*: If True, user can write ignoring the case. Default value is ``True``.
    * *values*: Set all the possible values for user choice. Default value is ``None``. For more information, check the :ref:`values-attribute` example
    
    **Common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page
    
.. _combobox_examples:

Examples
========

    .. _explanation:
    .. _values:
    .. _values-attribute:

Fill comboBox through *values* attribute
==========================================

    You can add values to combobox using the "values" attribute; check this example for the correct syntax::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.combobox(value='^.record.values',values='Football,Golf,Karate')

    .. note:: Pay attention not to confuse *value* with *values*: *value* is used to allocate user data in a well determined :ref:`genro_datapath`, while *values* is used to fill the comboBox.

    .. _here:
    .. _Bag:
    .. _bag_way:

Fill comboBox through a Bag
===========================

    Postponing all info of a ``Bag`` and of a ``data`` on the relative pages of documentation (:ref:`genro_bag_intro` introduction page and :ref:`genro_data` page), we'll show here how you can add values to ``combobox`` using a ``Bag``.
    
    **Example**::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = root.borderContainer(datapath='test1')
                bc.data('.values.sport',self.sports(),id='.pkey',caption='.Description')
                bc.combobox(value='^.record.Bag',storepath='.values.sport')
                
            def sports(self,**kwargs):
                mytable=Bag()
                mytable['r1.pkey'] = 'SC'
                mytable['r1.Description'] = 'Soccer'
                mytable['r2.pkey'] = 'BK'
                mytable['r2.Description'] = 'Basket'
                mytable['r3.pkey'] = 'TE'
                mytable['r3.Description'] = 'Tennis'
                mytable['r4.pkey'] = 'HK'
                mytable['r4.Description'] = 'Hockey'
                mytable['r5.pkey'] = 'BB'
                mytable['r5.Description'] = 'Baseball'
                mytable['r6.pkey'] = 'SB'
                mytable['r6.Description'] = 'Snowboard'
                return mytable
                
    The advantage of using a Bag is that you can add attributes to your records, but you lose the keys (they aren't supported from combobox).
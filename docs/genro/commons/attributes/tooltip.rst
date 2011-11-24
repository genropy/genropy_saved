.. _tooltip:

=======
tooltip
=======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *tooltip* attribute is supported by every :ref:`webpage element
              <we>`
              
    * :ref:`tooltip_def`
    * :ref:`tooltip_examples`:
    
        * :ref:`tooltip_attribute`
        * :ref:`tooltip_method`

.. _tooltip_def:

description
===========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc.tooltip
    
    .. image:: ../../_images/commons/attributes/tooltip.png
    
    You can:
    
    * pass it as an attribute to an object (:ref:`tooltip - attribute example
      <tooltip_attribute>`)
    * define it as a method attaching it to an object (:ref:`tooltip - method
      example <tooltip_method>`)
    
.. _tooltip_examples:

examples
========

.. _tooltip_attribute:

tooltip - attribute
-------------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                pane = root.borderContainer(**kwargs)
                pane.div(lbl='standard_tooltip',height='40px',width='40px',
                         background='teal',tooltip='This is a standard tooltip')
                       
.. _tooltip_method:

tooltip - method
----------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                pane = root.borderContainer(**kwargs)
                fb = pane.formbuilder(cols=2)
                pane.div(lbl='custom_tooltip',height='40px',width='40px',
                         background='blue').tooltip("""<div style='height:60px;width:250px;color:teal;font-size:18px;'>
                                                           Here we modify the tooltip style!
                                                       </div>""")
                
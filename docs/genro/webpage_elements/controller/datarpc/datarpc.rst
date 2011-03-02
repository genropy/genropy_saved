.. _genro_datarpc:

=======
dataRpc
=======

    The ``dataRpc`` belongs to :ref:`genro_datarpc` family, so it is a :ref:`controllers_server`.
    
    * :ref:`datarpc_def`
    * :ref:`datarpc_examples`
    
.. _datarpc_def:

Definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dataRpc
    
    * In the rpc you can return something, but as we explained in the ``dataRpc`` :ref:`datarpc_def` paragraph, you can skip this parameter if you want to perform only a server action; alternatively, it allows to return a value into the ``path`` of the ``dataRpc``.
    
.. _datarpc_examples:
    
Examples
========

    **First example**::
    
        # -*- coding: UTF-8 -*-
        
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                root.div('Hello assopy',font_size='40pt',border='3px solid yellow',padding='20px')
                
    Now we define a :ref:`genro_data` that describes the current date and it is calculated through Python code and it is served in the main page as a static data::

                root.data('demo.today', self.toText(datetime.datetime.today()))
                
    The next instruction is just a ``div`` to show the data. The first parameter of the div is its value, so you can write value='^demo.today' and it is just a div to show the content of the folder path ``demo.today``. Through this ``div`` we can see the data that has been calculated from the server when the page has been loaded::

                root.div('^demo.today',font_size='20pt',border='3px solid yellow',padding='20px',margin_top='5px')

    now we introduce the ``dataRpc``: when the instruction is triggered the client will call the server method 'getTime' and will put the result in demo.hour::

                root.dataRpc('demo.hour','getTime',_fired='^updateTime',_init=True)
                
                hour=root.div(font_size='20pt',border='3px solid yellow',padding='20px',margin_top='5px' )
                hour.span('^demo.hour')

    Now we introduce a button, so instead of putting the rpc call inside the button script, we use the button just to trigger a formula that we added in the client. A sleeping formula that is fired from this button::
    
                hour.button('Update',fire='updateTime',margin='20px')
                
    Please note that the ``fire`` attribute in :ref:`genro_button` is a shortcut for a script that puts 'true' in the destination path and then put again false. So for a little while we have a true in that location.
    
    Here lies the ``rpc server method`` definition::
    
            def rpc_getTime(self):
                return self.toText(datetime.datetime.now(),format='HH:mm:ss')
                
    Here we report all the example::
    
        # -*- coding: UTF-8 -*-
        
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                root.div('Hello assopy',font_size='40pt',border='3px solid yellow',padding='20px')
                root.data('demo.today', self.toText(datetime.datetime.today()))
                root.div('^demo.today',font_size='20pt',border='3px solid yellow',padding='20px',margin_top='5px')
                root.dataRpc('demo.hour','getTime',_fired='^updateTime',_init=True)
                hour=root.div(font_size='20pt',border='3px solid yellow',padding='20px',margin_top='5px' )
                hour.span('^demo.hour')
                hour.button('Update',fire='updateTime',margin='20px')
                
            def rpc_getTime(self):
                return self.toText(datetime.datetime.now(),format='HH:mm:ss')
                
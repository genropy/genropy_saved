.. _genro_dataremote:

==========
dataRemote
==========
    
    * :ref:`dataremote_def`
    * :ref:`dataremote_examples`

.. _dataremote_def:

Definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dataRemote
    
    **commons attributes**:
    
        For commons attributes (*_init*, *_onStart*, *_timing*) see controllers' :ref:`controllers_attributes`

.. _dataremote_examples:

Examples
========
    
    Let's see an example::
    
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test1')
                pane.button('Show time', action='alert(time);', time='=.time')
                pane.dataRemote('.time', 'get_time', cacheTime=5)
                
            def rpc_get_time(self, **kwargs):
                return datetime.datetime.now()
                
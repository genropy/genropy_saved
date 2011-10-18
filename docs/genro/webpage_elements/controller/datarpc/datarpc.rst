.. _datarpc:

=======
dataRpc
=======
    
    *Last page update*: |today|
    
    **Type**: :ref:`server-side controller <controllers_server>`
    
    The ``dataRpc`` belongs to dataRpc family, so it is a :ref:`server-side controller <controllers_server>`.
    
    * :ref:`datarpc_def`
    * :ref:`datarpc_string`
    * :ref:`datarpc_callable`
    
.. _datarpc_def:

definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dataRpc
    
    * in the ``**kwargs`` you have to define a parameter who allows the ``dataRpc`` to be triggered
      To do this, you can use ``_fired='^anotherFolderPath'``; in this case the dataRpc
      is triggered whenever the value contained in ``anotherFolderPath`` changes;
      the "_" is used to hide the trigger parameter in the :ref:`datastore`.
      
    To use a ``dataRpc`` you have to:
      
    #. Pass the ``dataRpc`` as a string or as a callable
    #. Create the dataRpc method that will execute a server action; you can optionally
       return a value. its form changes a bit according to the way you call it
       (string/callable)
       
.. _datarpc_string:

passing a dataRpc as a string
-----------------------------

    **passing the dataRpc**::
    
        root.dataRpc('pathOfData','RpcName',_fired='^updateTime',**kwargs)
        
    This is an example of a dataRpc called as a string. The first parameter (``pathOfData``) is a
    string with the path of the value returned (if the dataRpc returns something). The second value
    (``RpcName``) is a string with the dataRpc name
    
    **defining the dataRpc**
    
    The syntax is::
    
        def rpc_RpcName(self,args):
            return something
            
    Where: 
    
    * ``RpcName`` is the name of your ``dataRpc``
    * ``args`` contains all the paramaters passed from the ``dataRpc``
    
.. _datarpc_callable:

passing a dataRpc as a callable
-------------------------------

    **passing the dataRpc**::
    
        root.field('id_rate',
                    validate_remote=self.check_rate, validate_remote_error='Error!')
                    
    This is an example of a dataRpc passed as a callable into a :ref:`field` including
    a :ref:`validation <validations>` (the :ref:`validate_remote`) that allows to
    validate a :ref:`form` field through a dataRpc
    
    **defining the dataRpc**::
                      
        @public_method                    
        def check_rate(self,**kwargs):
            return something # Here goes the code for the validate_remote, that must
                             #    return "True" if the conditions have been satisfied,
                             #    "False" if the conditions haven't been satisfied
            
    As you can see, to pass the method as a callable you have to use the :meth:`public_method
    <gnr.core.gnrdecorator.public_method>` decorator; so, you have to import::
    
        from gnr.core.gnrdecorator import public_method
        
	.. _genro-dataremote:

==========
dataRemote
==========
	
	- :ref:`dataremote_def`
	
	- :ref:`dataremote_attr`
	
	- :ref:`dataremote_examples`

.. _dataremote_def:

Definition
==========

	.. method:: pane.dataRemote(path, remote, [**kwargs])
	
	The ``dataRemote`` is a synchronous rpc: it calls a (specified) rpc as a resolver. When ``dataRemote`` is brought to the client, it will be changed in a Javascript resolver that at the desired path perform the rpc (indicated with the ``remote`` attribute).
	
.. _dataremote_attr:

Attributes
==========

	**dataRemote attributes**:
	
	* ``path``: the path where the dataRemote will save the result of the rpc
	* ``remote``: the name of the rpc that has to be executed
	* ``cacheTime=NUMBER``: The cache stores the retrieved value and keeps it for a number of seconds equal to ``NUMBER``.
	
	**common attributes**:
	
		For common attributes (``_init``, ``_onStart``, ``_timing``) see controllers' :ref:`controllers_attributes`

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

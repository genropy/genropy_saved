	.. _genro-datarpc:

=========
 dataRpc
=========

	- :ref:`datarpc-description`

	- :ref:`datarpc-syntax`

	- :ref:`datarpc-examples`
	
	- :ref:`datarpc-common-attributes`

	.. _datarpc-description:

Description
===========

	- The ``dataRpc`` belongs to :ref:`genro-datarpc` family, so it is a server-side controller.

	With ``dataRpc`` [#]_ Genro let the client to make a call to the server and allows the server to perform an action.

	For using ``dataRpc`` you have to:

	- define the ``dataRpc`` into the main.

	- create a class method called the ``rpc server method``. In the ``rpc server method`` there will be executed a server action; you can optionally return a value.

	.. _datarpc-syntax:

Syntax
======

	In the ``main class method`` you have to write the following call:

	``object.dataRpc('folderPath',method='',**kwargs)``

	Where:

	- ``object`` is a form widget or a layout widget on which you append the ``dataRpc``.

	- ``folderPath`` contains the folder path of the result of the ``dataRpc`` action; you have to write it even if you don't return any value in the ``dataRpc`` (in this situation it will become a "mandatory but dummy" parameter).

	- ``method`` is the name of your ``dataRpc``.

	- in the **kwargs you have to define a parameter who allows the ``dataRpc`` to be triggered.
	
	For example, Genro Team uses ``_fired='^anotherFolderPath'``: the dataRpc is triggered whenever the value contained in ``anotherFolderPath`` changes; the "_" is used to hide the trigger parameter in the :ref:`genro-datastore`..

	Then, you have to create a ``rpc server method`` following this syntax:

	``rpc_RpcName(self,args):``

	Where:

	- ``rpc_`` is a keyword.

	- ``RpcName`` is the name of your ``dataRpc``; clearly, you have to put the same name that you gave to the ``dataRpc`` in the main.
	
	- ``args`` contains all the paramaters passed from the main.

	- ``return``; as we explained in the ``dataRpc`` :ref:`datarpc-description` paragraph, you can skip this parameter if you want to perform only a server action; alternatively, it allows to return a value into the ``dataRpc`` ``folderPath``.

	.. _datarpc-examples:

Examples
========

	**First example**::

		# -*- coding: UTF-8 -*-

		import datetime

		class GnrCustomWebPage(object):
			def main(self, root, **kwargs):
				root.div('Hello assopy',font_size='40pt',border='3px solid yellow',padding='20px')
	
	Now we define a :ref:`genro-data` that describes the current date and it is calculated through Python code and it is served in the main page as a static data::
	
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

	..datarpc-common-attributes:

Common attributes
=================

	For a complete reference of ``dataRpc`` common attributes, please check :ref:`rpc-common-attributes`.

**Footnotes**:

.. [#] dataRpc: data remote procedure call.
 
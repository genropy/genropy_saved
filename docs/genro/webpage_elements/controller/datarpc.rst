	.. _genro-datarpc:

=========
 dataRpc
=========

	- :ref:`datarpc-description`

	- :ref:`datarpc-syntax`

	- :ref:`datarpc-examples`

	.. _datarpc-description:

Description
===========

	--- dataRpc ---
		tipo.dataRpc('cartella.sottocartella', 'nomeDellaRpc', _fired='^STESSO NOME DEL _fire NEL button')
		es: root.dataRpc('demo.hour', 'getTime', _fired='^',)

        La dataRpc deve essere seguita da una definizione di Rpc:

    --- definizione Rpc ---
        def rpc_nomeDellaRpc(self):
            return qualcosa
        --- attributi ---
                ATT!!! non si possono passare delle variabili chiamate "name" (piuttosto usare "instance_name"), 
                       poiché in tal caso la Rpc dà problemi!



	``datarpc`` allows to ... ???

	.. _datarpc-syntax:

Syntax
======

	``object``.datarpc('???',...)
	
	Where:

	- first parameter: ???

	.. _datarpc-examples:

Examples
========


 
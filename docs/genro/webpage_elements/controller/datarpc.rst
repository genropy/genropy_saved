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

	With ``dataRpc``, a call is made from the client to the server and the server returns a result.
	
	The ``dataRpc`` belongs to :ref:`genro-server-side-controllers` family.

	
	
	
	
	::
	
		class GnrCustomWebPage(object):
			def main(self, root, **kwargs):
			root.div('Hello!', font_size='40pt', border='3px solid yellow',padding='20px')
	
	Now we define a :ref:`genro-data` that describes the current date and it is calculated through Python code and it is served in the main page as a static data.

			root.data('demo.today', self.toText(datetime.datetime.today()))
	Now this instruction is just a div to show the data. The first parameter of the div is its value, so you can write value='^demo.today' and it is just a div to SHOW the content of demo.today.

	    root.div('^demo.today', font_size='20pt', border='3px solid yellow',
	    padding='20px', margin_top='5px')
	In this way we can see the data that was calculated from the server when the page was loaded. NOW we will add dynamic data and discuss this instruction in detail.

	root.dataRpc('demo.hour','getTime',_fired='^updateTime',_init=True)
	root.dataRpc, is the instruction that says to the client to do a call to the server whenever it is 'triggered'. When the instruction is triggered the client will call the server method 'getTime' and will put the result in demo.hour

	Parameters:

	bag path
	the function name
	_fired='^updateTime'
	remaining parameters are named so their position is not important
	This is a 'fake parameter'

	_fired='^updateTime'

	The result path can be relative or absolute depending if it starts with '.' or not
	The second parameter is the server method without the rpc_ .For security reason we add the rpc_ string.

	The 3rd parameter _fired='^updateTime'

	This is a fake parameter. We don't use it BUT it is important as it is a way to trigger the call, so we install an 'observer' on the path 'updateTime' and whenever this value changes the call is executed. This is a VERY VERY important concept. You can imagine this as a 'virtual' button and you can PUSH this button from code.

	Changing the value of the data at updateTime. In this case we simply create the call and we 'arm' our trap, and next we have to create something to PUSH this button.

	hour.button('Update', fire='updateTime', margin='20px')

	ThIs is our button So instead of putting the rpc call inside the button script, we use the button just to trigger a formula that we added in the client. A sleeping formula that is fired from this button.
	Question: What is the difference between fire and _fired ?

	Answer: _fired is used to trigger every time ^updateTime changes. fire in button is a shortcut for a script that puts 'true' in the destination path and then put again false. So for a little while we have a true in that location. So fire is just a shortcut.

	So this then changes ^updateTime which fires the dataRpc

	The good point is that we can fire an event from many widgets. For example: from a button, from a menu, or from javascript code. BUT we don't use the fired value, as it is a fake parameter. In this case we often use the name '_fired' just to remember that this is not relevant in the formula.

	We could have also relevant parameters, and in this case they will be sent to the server, so we can use them in server.

	Question: Yesterday Saverio explained that when the ^xx data changes . . then this can provide the trigger mechanism . . now you tell me that fire in a button object will temporarily change the value of the data in path xx to true, and then it will go back to false. Does this mean that the trigger will fire twice, because the data is changed twice?

	Answer: Really GOOD question jeff. We have to change the value to true to fire the trigger but if we keep the true value when we fire again, we should store 'false' and it is not easy to do. So in the fire command we do a little trick. First we put true and then we put false but with a parameter that avoids trigger. So we are hiding this second change and the trigger will run only once.
	￼
	But the question is very very good and it shows that you are learning very well
	well . . I assume then that this is automatic with buttons.

	Question: What happens when other ways are used to fire? Do do we need to pass this parameter explicitly ?

	Answer: I think seldom for menu javascript etc. (other ways), as we have many ways to get a fire action.

	We may think that the value fired from a button will always be true or false (0 or 1) that we are passing to the bag data. But there are two syntax's for fire

	fire='foo.bar'

	OR
	fire_spam='foo.bar'

	In this case the string 'spam' is fired instead of the value 'true'. So you can have many buttons with just a formula that receives different values. With fire the state is ALWAYS reversed. So with fire_spam it will be reversed to what the data was before the call (which is always False.
	So for example we use this way for navication buttons:

	fire_first
	fire_next
	fire_prev
	fire_last

	and so on.

	Now we focus on the 4th parameter of our dataRpc .

	_init=True

	This means that the call is done ALSO when the data is set the first time, so during the :ref:`webpage-build-phase`.
	


	--- dataRpc ---
		tipo.dataRpc('cartella.sottocartella', 'nomeDellaRpc', _fired='^STESSO NOME DEL _fire NEL button')

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


 
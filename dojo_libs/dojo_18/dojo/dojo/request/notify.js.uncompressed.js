define("dojo/request/notify", ['../Evented', '../_base/lang', './util'], function(Evented, lang, util){
	// module:
	//		dojo/request/notify
	// summary:
	//		Global notification API for dojo/request
	//
	//		| require('dojo/request', 'dojo/request/notify',
	//		|     function(request, notify){
	//		|         notify('load', function(response){
	//		|             if(response.url === 'someUrl.html'){
	//		|                 console.log('Loaded!');
	//		|             }
	//		|         });
	//		|         request.get('someUrl.html');
	//		|     }
	//		| );

	var pubCount = 0;

	var hub = lang.mixin(new Evented, {
		onsend: function(data){
			if(!pubCount){
				this.emit('start');
			}
			pubCount++;
		},
		_onload: function(data){
			this.emit('done', data);
		},
		_onerror: function(data){
			this.emit('done', data);
		},
		_ondone: function(data){
			if(--pubCount <= 0){
				pubCount = 0;
				this.emit('stop');
			}
		},
		emit: function(type, event){
			var result = Evented.prototype.emit.apply(this, arguments);

			// After all event handlers have run, run _on* handler
			if(this['_on' + type]){
				this['_on' + type].apply(this, arguments);
			}
			return result;
		}
	});

	function notify(type, listener){
		return hub.on(type, listener);
	}
	notify.emit = function(type, event, cancel){
		return hub.emit(type, event, cancel);
	};

	// Attach notify to dojo/request/util to avoid
	// try{ require('./notify'); }catch(e){}
	return util.notify = notify;
});

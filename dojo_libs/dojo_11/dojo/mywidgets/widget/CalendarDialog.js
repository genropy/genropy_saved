dojo.provide("mywidgets.widget.CalendarDialog");
dojo.require("dojo.cldr.supplemental");
dojo.require("dojo.date");
dojo.require("dojo.date.stamp");
dojo.require("dojo.date.locale");
dojo.require("dijit._Widget");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.TimeTextBox");
dojo.require("dijit.form.DateTextBox");
dojo.require("dijit.form.ComboBox");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.FilteringSelect");
dojo.require("dijit._Templated");
dojo.require("dojox.layout.FloatingPane");
dojo.require("dijit.Dialog");
dojo.require("dojo.date");
dojo.require("dojo.data.ItemFileWriteStore");
dojo.declare(
	"mywidgets.widget.CalendarDialogNewEntry",
	[dijit.Dialog],
{
	// summary:
	// This is the actual content.
	templateString: null,
	templatePath: dojo.moduleUrl("mywidgets.widget","templates/newentry.html"),
	widgetsInTemplate: true,
	openerId: "",
	
	postMixInProperties: function(){
		this.inherited(arguments);
		this.messages = dojo.i18n.getLocalization("dijit", "common", this.lang);
		dojo.forEach(["buttonOk", "buttonCancel"], function(prop){
			if(!this[prop]){ this[prop] = this.messages[prop]; }
		}, this);
	},
	
	postCreate:function(){
		// summary: Load the content. Called when first shown
		this.inherited(arguments);
		this.opener = dijit.byId(this.openerId);
		this.ne_subject.value = "";
		this.ne_location.value = "";
		this.ne_categories.value = "";
		this.ne_body.value = "";
		this.ne_alldayevent.checked = false;
		var dDate = new Date();
		this.ne_date.setValue(dDate);
		this.ne_starttime.setValue(dDate);
		dDate.setHours(dDate.getHours()+1);
		this.ne_endtime.setValue(dDate);
		var oEventtypes = this.opener.eventtypes;
		var store = new dojo.data.ItemFileWriteStore({data:{
		identifier: 'name',label: 'name',items: [{name:"No Type", value:""}]}});
		//store.newItem({name:"No Type", value:""}, null);
		for(var i in oEventtypes){store.newItem({name:oEventtypes[i].title, value:oEventtypes[i].title}, null);}
		this.ne_type.store = store;
	},
	
	alldayclicked: function(){
		if(this.ne_alldayevent.checked){
			var dDate = this.ne_date.attr('value')
			if(dDate == null){
				dDate = new Date();
			}
			this.ne_starttime.value = "";
			this.ne_starttime.attr('disabled',true);
			this.ne_endtime.value = "";
			this.ne_endtime.attr('disabled',true);
		}else{
			var dDate = this.ne_date.attr('value')
			if(dDate == null){
				dDate = new Date();
			}else{
				var newDate = new Date();
				dDate.setHours(newDate.getHours(), newDate.getMinutes());
			}
			this.ne_starttime.value = "";
			this.ne_starttime.attr('disabled',false);
			this.ne_endtime.value = "";
			this.ne_endtime.attr('disabled',false);
		}
	},
	
	ok: function(){
		var isOk = true;
		var alertText = '';
		if(this.ne_subject.value == ""){
			isOk = false;
			alertText += '<br />' + 'Title:';
		}
		var attr;
		if(this.ne_alldayevent.checked){
			attr = {
				selector:"date", 
				formatLength:"short"
			};
		}else{
			attr = {
				selector:"dateTime", 
				formatLength:"short"
			};
		}
		var dStartDate = this.ne_date.attr('value');
		dStartDate.setHours(this.ne_starttime.attr('value').getHours(), this.ne_starttime.attr('value').getMinutes());
		if(dStartDate == null){
			isOk = false;
			dStartDate = new Date();
			alertText += '<br />' + 'Start time: Please format time correctly!<br />i.e. ' + dojo.date.locale.format(dStartDate, attr);
		}
		var dEndDate;
		if(!this.ne_alldayevent.checked){
			var dEndDate = this.ne_date.attr('value');
    		dStartDate.setHours(this.ne_endtime.attr('value').getHours(), this.ne_endtime.attr('value').getMinutes());
			if(dEndDate == null){
				isOk = false;
				dEndDate = new Date();
				alertText += '<br />' + 'End time: Please format time correctly!<br />i.e. ' + dojo.date.locale.format(dEndDate, {formatLength:"short"});
			}
		}else{
			dEndDate = dStartDate;
		}
		
		if(!isOk){
			dojo.require("mywidgets.widget.ModalAlert");
			var params = {
				height: "230px",
				iconSrc: dojo.moduleUrl("mywidgets.widget","templates/images/error.gif"),
				alertText: '<strong>Please edit/complete the following field(s):</strong><br />' + alertText
			};
			var modal = new mywidgets.widget.ModalAlert(params);
		}else{
			var oEntry = {
				starttime: dojo.date.stamp.toISOString(dStartDate),
				endtime: dojo.date.stamp.toISOString(dEndDate),
				allday: this.ne_alldayevent.checked,
				repeated: false,
				title: this.ne_subject.value,
				url: "",
				body: this.ne_body.value,
				attributes: {
					Location: this.ne_location.value,
					Categories: this.ne_categories.value
				},
				type: this.ne_type.attr('value')
			};
			
			this.opener._createNewEntry(oEntry);
			this.cancel();
		}
	},
	
	cancel: function(){
		this.hide();
	}
});

dojo.declare(
	"mywidgets.widget.CalendarDialogTimezone",
	[dijit.Dialog],
    {
	// summary:
	// This is the actual content.
	templateString: null,
	templatePath: dojo.moduleUrl("mywidgets.widget","templates/timezones.html"),
	widgetsInTemplate: true,
	openerId: "",

	postMixInProperties: function(){
		this.inherited(arguments);
		this.messages = dojo.i18n.getLocalization("dijit", "common", this.lang);
		dojo.forEach(["buttonOk", "buttonCancel"], function(prop){
			if(!this[prop]){ this[prop] = this.messages[prop]; }
		}, this);
		
	},
	
	postCreate:function(){
		// summary: Load the content. Called when first shown
		this.inherited(arguments);
		this.opener = dijit.byId(this.openerId);
		var store = new dojo.data.ItemFileWriteStore({data:{
		identifier: 'name',label: 'name',items: [{name:"Default", value:""}]}});
		for (var i in this.opener.timezones) {
		    store.newItem({name:this._buildGMT(this.opener.timezones[i].offset) + this.opener.timezones[i].name, value:this.opener.timezones[i].sn}, null);
		}
		this.timezonesnode.store = store;
	},
	_buildGMT: function(/*int*/ offset) {
		if (offset == 0)
			return "(GMT) ";
		
		var hour = Math.abs(parseInt(offset/60));
		var minute = 60 * (Math.abs(offset/60) - hour);
		return "(GMT" + (offset < 0 ? '-' : '+') + dojo.string.pad(""+hour, 2) + ':' + dojo.string.pad(""+minute, 2) + ') '; // string
	},
	ok: function(){
		this.opener._setTimeZone(this.timezonesnode.attr('value'));
		this.cancel();
	},
	cancel: function(){
		this.hide();
	}
});


dojo.declare(
	"mywidgets.widget.CalendarDialogChangeTime",
	[dijit.Dialog],
{
	// summary:
	// This is the actual content.
	templatePath: dojo.moduleUrl("mywidgets.widget","templates/changetime.html"),
	widgetsInTemplate: true,
	openerId: "",
	itemId: "",
	eventChanged: false,
	dropDate: "",
	starttime: "",
	endtime: "",
	newstarttime: "",
	newendtime: "",
	
    postMixInProperties: function(){
		this.inherited(arguments);
		this.messages = dojo.i18n.getLocalization("dijit", "common", this.lang);
		dojo.forEach(["buttonOk", "buttonCancel"], function(prop){
			if(!this[prop]){ this[prop] = this.messages[prop]; }
		}, this);
	},

	postCreate:function(){
		// summary: Load the content. Called when first shown
		this.opener = dijit.byId(this.openerId);
		var oDragObject = this.opener.DragObject;
		var oDropObject = this.opener.DropObject;
		alert('hi');
		this.itemId = oDragObject.getAttribute("itemid");
		this.starttime = new Date(parseInt(oDragObject.getAttribute("starttime")));
		this.endtime = new Date(parseInt(oDragObject.getAttribute("endtime")));

		this.dropDate = dojo.date.stamp.fromISOString(oDropObject.getAttribute("id"));
		this.date_node.innerHTML = dojo.date.locale.format(this.dropDate, {formatLength:"medium", selector:"date", locale:this.opener.lang});
		
		var startPars = {
			storedTime: dojo.date.stamp.toISOString(this.starttime),
			lang: this.opener.lang
		};
		this.startPicker = new TimePicker(startPars, this.starttime_node);
		
		var endPars = {
			storedTime: dojo.date.stamp.toISOString(this.endtime),
			lang: this.opener.lang
		};
		this.endPicker = new TimePicker(endPars, this.endtime_node);
		
	},
	
	ok: function(){
		this.eventChanged = true;
		
		this.newstarttime = new Date(this.startPicker.time);
		this.newendtime = new Date(this.endPicker.time);
		
		this.newstarttime.setFullYear(this.dropDate.getFullYear());
		this.newstarttime.setMonth(this.dropDate.getMonth());
		this.newstarttime.setDate(this.dropDate.getDate());
		this.newendtime.setFullYear(this.dropDate.getFullYear());
		this.newendtime.setMonth(this.dropDate.getMonth());
		this.newendtime.setDate(this.dropDate.getDate());
		
		this.cancel();
	},
	
	cancel: function(){
		this.hide();
		this.opener._eventChanged(this.eventChanged, this.itemId, this.newstarttime, this.newendtime);
		this.startPicker.destroy();
		this.endPicker.destroy();
	}
});

dojo.declare(
	"mywidgets.widget.CalendarDialog",
	[dijit._Widget],
	{
		// summary:
		//		Provides a Dialog which can be modal or normal.
		//templatePath: dojo.moduleUrl("mywidgets.widget","templates/Editor2/EditorDialog.html"),
		// modal: Boolean: Whether this is a modal dialog. True by default.
		modal: true,
		// width: String: Width of the dialog. None by default.
		width: "",
		// height: String: Height of the dialog. None by default.
		height: "",
		// windowState: String: startup state of the dialog
		windowState: "normal",
		displayCloseAction: true,
		// contentClass: String
		contentClass: "",
		openerId: "",

		postMixInProperties: function(){
			var _nlsResources = dojo.i18n.getLocalization("dijit", "common");
			dojo.mixin(this, _nlsResources);
			this.inherited(arguments);
		},

		fillInTemplate: function(args, frag){
			this.fillInFloatingPaneTemplate(args, frag);
			this.inherited(args, frag);
//			mywidgets.widget.CalendarDialog.superclass.fillInTemplate.call(this, args, frag);
		},
		postCreate: function(){
			if(this.modal){
			    
				dojo.widget.ModalDialogBase.prototype.postCreate.call(this);
			}else{
				with(this.domNode.style) {
					zIndex = 999;
					display = "none";
				}
			}
			this.inherited(arguments);
//          dojo.widget.FloatingPaneBase.prototype.postCreate.apply(this, arguments);
			mywidgets.widget.CalendarDialog.superclass.postCreate.call(this);
			if(this.width && this.height){
				with(this.domNode.style){
					width = this.width;
					height = this.height;
				}
			}
		},
		createContent: function(){
			if(!this.contentWidget && this.contentClass){
				this.contentWidget = new this.contentClass();
				this.addChild(this.contentWidget);
			}
		},
		show: function(){
			if(!this.contentWidget){
				this.inherited(arguments);
//              mywidgets.widget.CalendarDialog.superclass.show.apply(this, arguments);
				this.createContent();
				this.hide();
//              mywidgets.widget.CalendarDialog.superclass.hide.call(this);
			}

			if(!this.contentWidget || !this.contentWidget.loadContent()){
				return;
			}
			this.showFloatingPane();
			this.inherited(arguments);
//          mywidgets.widget.CalendarDialog.superclass.show.apply(this, arguments);
			if(this.modal){
				this.showModalDialog();
			}
			if(this.modal){
//              place the background div under this modal pane
				this.bg.style.zIndex = this.domNode.style.zIndex-1;
			}
		},
		onShow: function(){
			mywidgets.widget.CalendarDialog.superclass.onShow.call(this);
			this.onFloatingPaneShow();
		},
		closeWindow: function(){
			this.hide();
			this.inherited(arguments);
//          mywidgets.widget.CalendarDialog.superclass.closeWindow.apply(this, arguments);
		},
		hide: function(){
			if(this.modal){
				this.hideModalDialog();
			}
			this.inherited(arguments)
//          mywidgets.widget.CalendarDialog.superclass.hide.call(this);
		},
		checkSize: function(){
			if(this.isShowing()){
				if(this.modal){
					this._sizeBackground();
				}
				this.placeModalDialog();
				this.onResized();
			}
		}
	}
);

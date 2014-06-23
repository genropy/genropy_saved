dojo.provide("mywidgets.widget.ModalAlert");

dojo.require("dojox.layout.FloatingPane");

dojo.declare("mywidgets.widget.ModalAlert", [dijit._Widget],

	{
	widgetId: "modalAlert",
	title: "Attention",
	iconSrc: "",
	alertText: "",
	width: "350px",
	height: "150px",
	
	execute: function(){
		var button = "<br /><br /><br /><p align=center><button style=\"width:60px;\" onClick=\"dijit.byId('" + this.widgetId + "').hide();\">OK</button></p>";
		if(!dijit.byId(this.widgetId)){
			var div = document.createElement("div");
			div.style.position="absolute";
			div.innerHTML = this.alertText + button;
			
			dojo.body().appendChild(div);
			div.style.width = this.width;
			div.style.height = this.height;
			
			var params = {
				widgetId:this.widgetId,
				id:this.widgetId,
				title:this.title,
				iconSrc:this.iconSrc,
				toggle:"fade",
				resizable:false,
				dockable:false,
				//windowState:"normal",
				hasShadow:true
			};
			var widget = new dojox.layout.FloatingPane(params, div);
			widget.startup();
		}else{
			dojo.byId(this.widgetId+'_container').innerHTML = this.alertText + button;
			dijit.byId(this.widgetId).show();
		}
	}
});

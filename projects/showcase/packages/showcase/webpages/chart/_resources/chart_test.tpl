# -*- coding: UTF-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%  
dojo_13 = mainpage.resolvePathAsUrl('dojo/dojo_13/dojo/dojo.js', folder='*lib')
dojo_css = mainpage.resolvePathAsUrl('dojo/dojo_13/dojo/resources/dojo.css', folder='*lib')
test_css = mainpage.resolvePathAsUrl('dojo/dojo_13/dijit/tests/css/dijitTests.css', folder='*lib')
%>
<html xmlns="http://www.w3.org/1999/xhtml">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<head>
		<title>
			Charting
		</title>
		<style type="text/css">
			@import "${dojo_css}";
			.container{
				border:1px solid green;
				margin:1em;
				padding:1em;
				float:left;
			}
		</style>
		
		<script type="text/javascript" src="${dojo_13}" 
			djConfig="isDebug: false, parseOnLoad: true"></script>	
				
		<script type="text/javascript">
			dojo.require("dojox.charting.widget.Chart2D");
			dojo.require("dojox.charting.widget.Sparkline");
			dojo.require("dojox.charting.themes.Tufte");
			dojo.require("dojox.data.HtmlStore");
			dojo.require("dojox.data.CsvStore");
			dojo.require("dojo.parser");
 makeCharts = function(){
			var chart1 = new dojox.charting.Chart2D("simplechart");
			chart1.addPlot("default", {type: "Lines"});
			chart1.addAxis("x", {labels: [
											{value: 1, text: "Jan"}, 
											{value: 2, text: "Feb"},
											{value: 3, text: "Mar"}, 
											{value: 4, text: "Apr"}, 
											{value: 5, text: "Mag"}
										],
								from:1,
								to:5});
			chart1.addAxis("y", {vertical: true});
			var myserie = [1, 2, 1, 3, 9];
			
			chart1.addSeries("Series 1", myserie);
			chart1.render();
};
dojo.addOnLoad(makeCharts);

		</script>
	</head>
	<body class='tundra'>
		<div id="name">
			Simple
		</div>
		<div id="simplechart" style="width: 600px; height: 200px;">
</html>
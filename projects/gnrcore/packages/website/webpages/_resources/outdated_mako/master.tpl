## master.tpl
<%  
folders=mainpage.db.table('website.folder').query().fetch()

%>

<%def name="header(folders=None)">
	<div class="header">
		<div id="logo">logo</div>
		<div class='menubar'>
	       %for f in folders:
               <a href='/${f["child_code"]}'>${f['title']}</a>&nbsp;
           %endfor
	    </div>
	</div>
</%def>


<%def name="footer()">
    <div class="footer">
    	 I AM MASTER FOOTER
	</div>
</%def>

<%def name="css(css)">
	%for c in mainpage.site.resource_loader.getResourceList(mainpage.resourceDirs, css, 'css'):
		@import url(${mainpage.getResourceUri(c)});
	%endfor
</%def>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<!--<base href="http://www.site.com">-->
		<!--<link rel="shortcut icon" href="favicon.ico">-->
		<style type="text/css">
			${self.css('website.css')}
		</style>
		<title>MySite</title>
	</head>
	
<body>
	<div id="preContainer">
		<div id="container">
			<table id="mainTbl" border="0" cellpadding="0" cellspacing="0">
				<tr>
					<td colspan='6' align='center'>
						${self.header(folders=folders)}
					</td>
				</tr>
				${self.body()}
				<tr height='100' valign='bottom'>
					<td colspan='6' align='center'>
						${self.footer()}
					</td>
				</tr>
			</table>
		</div>
	</div>
</body>

</html>

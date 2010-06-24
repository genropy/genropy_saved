<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8;" />
        
        <%include file="gnr_header_static.tpl" />
		<style type="text/css">    
        
        	@import url("${mainpage.getResourceUri('html_tables/html_tables','css')}") all;
			@import url("${mainpage.getResourceUri('html_tables/html_tables_print','css')}") print;
        
		</style>
		
		<title>${meta.get('title') or meta.get('header')}</title>
    </head>
   <body class="tableWindow ${mainpage.get_bodyclasses()}" >
        <h1 class="only_print">${meta.get('header') or meta.get('title')}</h1>
        <%include file="standard_print_table.tpl" args="mainpage=mainpage, columns=columns, outdata=outdata" />
    </body>
</html>

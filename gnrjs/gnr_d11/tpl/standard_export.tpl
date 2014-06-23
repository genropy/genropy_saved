<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd">
<%
_ = mainpage._
fmt = mainpage.toText

if not columns:
	cols = [c for c in selection.allColumns if not c in ('pkey','rowidx')]
outdata = selection.output('dictlist', columns=cols, asIterator=True)
%>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8;" />
		<title>${title}</title>
		<style type="text/css" title="text/css">
            <!--
            body{background-color: transparent;}
            table{background-color: transparent;}
            -->
        </style>
        
    </head>
   <body>
        <h1>${header}</h1>
        <table border='1px'>
			<thead>
				<tr>
				%for colname in cols:
					<%
					colattr = selection.colAttrs.get(colname, dict())
					%>
					<th>${_(colattr.get('label', colname))}</th>
				%endfor
				</tr>
			</thead>
			<tbody>
			%for r in outdata:
				<tr>
				%for colname in cols:
					<%
					colattr = selection.colAttrs.get(colname, dict())
					%>
					<td>${fmt(r[colname], format=colattr.get('format'), mask=colattr.get('mask')).replace('\n',' ').replace('<br />', ' ')}</td>
				%endfor
				</tr>
			%endfor
			</tbody>
		</table>
    </body>
</html>

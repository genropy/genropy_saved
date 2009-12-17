<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd">
<%!
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, toText
from gnr.web.gnrwebstart import getCssBag, findInheritedFile
from gnr.web.gnrstandardpages import RowFormatter

def test(cond, iftrue='', iffalse=''):
    if cond: return iftrue
    else: return iffalse
%>

<% 
pagelang = mainpage.locale
db=mainpage.db

%>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />

    
    <style type="text/css" title="localcss" media="all">
        body {overflow-y: auto;
            background-color:white; 
            font-size:8pt;
        }
        table {font-size:8pt;}
        th {vertical-align: text-top;
            text-align:center;
            font-size:8pt;
            border-right:1px gray solid;border-top:1px gray solid;border-bottom:1px gray solid;}
        th:first-child {border-left:1px gray solid;}

        caption{
	    background-color: whitesmoke;font-size:11pt;border:1px gray solid;margin-bottom:2px;
        }
        td {border-right:1px gray solid;border-bottom:1px gray solid;}
        td:first-child {border-left:1px gray solid;}
        .tbl{padding-left:2em;padding-bottom:2em;
        }
    </style>

    <style type="text/css" title="localcss" media="print">
        body {overflow:visible;}

    </style> 

    </head>
    <body >
	
	%for pobj in [o for p,o in db.packages.items() if not pkg or p==pkg]:
	    %for tobj in [o for t,o in pobj.tables.items() if not tbl or t==tbl]:
	        <div class='tbl'>
	        <table cellpadding='2' width='500px' cellspacing='0'>
		          <caption>${tobj.fullname}</caption>
                   <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Name Long</th>
                            <th>Relations</th>
                        </tr>
                    </thead>
                    <tbody>
                     %for cobj in tobj.columns.values():
                         <tr>
                            <td >${cobj.name}</td>
                            <td >${cobj.attributes.get('dtype','')}</td>
                            <td >${cobj.attributes.get('size','')}</td>
                            <td >${cobj.attributes.get('name_long','')}</td>
                             %if cobj.relatedColumn() is not None:
                                <td >${cobj.relatedColumn().fullname}</td>
                             %elif cobj.name == tobj.pkey and tobj.relatingColumns:
                                <td >${'<br/>'.join(tobj.relatingColumns)}</td>
                             %else:
                                <td/>
                             %endif
                          </tr>
                      %endfor
                    </tbody>
            </table>
            </div>
         %endfor
    %endfor
<div class="pageBreakAfter" >&nbsp;</div>
    </body>
</html>



# -*- coding: UTF-8 -*-

<%inherit file="master.tpl"/>

<% 
resource = mainpage.getWebResource()
pages =mainpage.getPagesByFolder(resource['folder'])
%>

<%def name="leftBar(pages=[],resource={})">
<div>
	%for p in pages:
	    <a href='${resource["path"]+p["permalink"]}'>${p['title']}</a>&nbsp;<br/>
	%endfor
</div>
</%def>

<tr height='400' valign='top'>
	<td width='140'>
	${self.leftBar(pages=pages,resource=resource)}
	</td>
	<td width='820'>
		%if resource['page']:
			<div>
		        <div class='title'><i style='font-size:250%;'>
		        	${ resource['page']['title']}
		        </i>
				</div>
				<div class='content'>
				${ resource['page']['content']}
				</div>
			</div>
		%endif
	</td>
	<td>&nbsp;</td>
</tr>

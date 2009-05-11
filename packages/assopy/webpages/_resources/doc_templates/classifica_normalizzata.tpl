# -*- coding: UTF-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%  
classifica = mainpage.db.table('assopy.valutazione').creaClassifica()
totalizer=classifica.totalizer()
classificaTalk=totalizer['per_talk']
classificaTrack=totalizer['per_track']
classificaTrack.sort('#a.k_track_code')
classificaTalk.sort('#a.sum_voto_n2:d')
classificaSocio=totalizer['per_socio']
%>
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>
		</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<%include file="gnr_header_static.tpl" />
	</head>
    <style type="text/css">    
    .classifica_talk {
    	font-family: Arial, Helvetica, Geneva, sans-serif;
    	font-size:0.8em;
        margin-bottom:60px;
    }
    .classifica_talk td {

    	padding-left:6px;
    	padding-right:6 px;
    	border-bottom:1px solid silver;
    }
    .classifica_talk th {
    	padding-left:6px;
    	padding-right:6 px;
    	border-bottom:2px solid gray;
    }
    .classifica_talk .DP {
         background-color:#fdffca;
    }
    .classifica_talk .SP {
         background-color:#c1d5ff;
    }
    .classifica_talk .IP {
         background-color:#bcffbb;
    }

    </style>


	<body >
	    <h1>Classifica generale</h1>
	    <table class='classifica_talk'>
			<thead>
				<tr>
				    <th ><div >N.</div></th>
					<th ><div >Speaker</div></th>
					<th ><div >Talk</div></th>
					<th ><div >Voto</div></th>
					<th ><div >Trak</div></th>
					<th ><div >Durata</div></th>
					<th ><div >Voti</div></th>
				</tr>
			</thead>
			<tbody>
			%for k,row in enumerate(classificaTalk.digest('#a')):
			<% row['collect_voto_n2'].sort(reverse=True) %>
				<tr class=${row['k_track_code']}>
				    <td>${str(k+1)}</td>
					<td>${row['k_speaker']}</td>
					<td>${row['k_talk']}</td>
					<td>${row['sum_voto_n2']}</td>
					<td>${row['k_track']}</td>
					<td>${row['k_durata'] or '-'}</td>
					<td>${'+'.join([str(y) for y in row['collect_voto_n2']])}</td>
				</tr>
			%endfor
			</tbody>
		</table>
		
		<h1>Classifica per track</h1>
		%for trackrow,v in classificaTrack.digest('#a,#v'):
		   <% v.sort('#a.sum_voto:d') %>
		   <h2>${trackrow['k_track']}</h2>
		   <table class='classifica_talk'>
   			<thead>
   				<tr>
   				    <th ><div >N.</div></th>
   					<th ><div >Speaker</div></th>
   					<th ><div >Talk</div></th>
   					<th ><div >Durata</div></th>
   					<th ><div >Voto</div></th>
   				</tr>
   			</thead>
   			<tbody>
   			%for k,row in enumerate(v.digest('#a')):
   				<tr class=${row['k_track_code']}>
   				    <td>${str(k+1)}</td>
   					<td>${row['k_speaker']}</td>
   					<td>${row['k_talk']}</td>
   					<td>${row['k_durata'] or '-'}</td>
   					<td>${row['sum_voto_n2']}</td>
   				</tr>
   			%endfor
   			</tbody>
   		</table >
   		
		%endfor
	    
		
	</body>
</html>

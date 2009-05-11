# -*- coding: UTF-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%  
ordine = mainpage.db.table('assopy.ordine').record(ordine_id).output('bag')
righe =  ordine['@assopy_ordine_riga_ordine_id']
righe.sort('#a.numero_riga')
righe.nodes[:] = [n for n in righe.nodes if n.getValue()['tariffa_codice']!='_OMG']


cliente = ordine['@anagrafica_id']
bank = "BCC di Busto Garolfo e Buguggiate - IBAN: IT72R0840450700000000041453  - Swift/BIC: ICRAITMMB80"
%>
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>
		</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<%include file="gnr_header_static.tpl" />
		
	</head>
	<body class='donazione documento'>
		<a style='float: right; margin: 1em; font-size: 1.5em;' class='no_print' href='#' onclick='window.print();'>[Stampa Ricevuta]</a>
		
		<div class='foglio'>
		
			<img src="../_resources/pyconitalia.jpg" style="float: left"/>
			<div class='intestazione' style="float: right">
				PYTHON ITALIA Associazione di Promozione Sociale<br />
				Via Mugellese, 1 - 50013 Campi Bisenzio (FI) <br />
				Partita IVA/V.A.T. 05753460483<br /> 
				Tel/Phone 055.8969650 <br /> 
				Email: amministrazione@pycon.it
			</div>
			<div style='clear: both; height:60px'>&nbsp;</div>
			<table class='header' >
				<tbody>
					<tr>
						<td class='label' >
						    <div class='it'>Numero</div>
							<div class='en'>Number</div>
						</td>
						<td class='value valueshort' >${ordine['numero']}</td>
						<td>&nbsp;</td>
						<td rowspan='3' class='label' >
						    <div class='it'>Donatore</div>
							<div class='en'>Account</div>
						</td>
						<td rowspan='3' class='value cliente'>
							${cliente['titolo'] or '&nbsp;'}<br />
							${cliente['ragione_sociale']}<br />
							${cliente['indirizzo']}<br />
							${cliente['cap']} ${cliente['localita']} ${cliente['provincia']}
						</td>
					</tr>
					<tr>
						<td class='label'>
						    <div class='it'>Data</div>
							<div class='en'>Date</div>
						</td>
						<td class='value'>${mainpage.toText(ordine['fattura_data'], locale='it', format='d/M/Y')}</td>
			
					</tr>
					<tr>
						<td class='label'>
						    <div class='it'>Valuta</div>
							<div class='en'>Currency</div>
						</td>
						<td class='value'>EUR</td>
					</tr>
					<tr>
						<td class='label'>
						    <div class='it'>Partita IVA</div>
							<div class='en'>VAT/EIN</div>
						</td>
						<td class='value'>${cliente['partita_iva'] or '&nbsp;'}</td>
					</tr>
					<tr>
						<td class='label'>
						    <div class='it'>Codice Fiscale</div>
							<div class='en'>Fiscal Code</div>
						</td>
						<td class='value'>${cliente['codice_fiscale'] or '&nbsp;'}</td>
					</tr>
					<tr>
						<td class='label'>
						    <div class='it'>Banca</div>
							<div class='en'>Bank</div>
						</td>
						<td class='value' colspan="4">${bank}</td>
					</tr>		
				<tbody>
			</table>
			<table class='rows'>
				<thead>
					<tr>
						<th style='width: 6em'>
							<div class='it'>Codice</div>
							<div class='en'>Code</div>
						</th>
						<th>
							<div class='it'>Descrizione</div>
							<div class='en'>Description</div>
						</th>
						<th style='width: 5em'>
							<div class='it'>Quantità</div>
							<div class='en'>Quantity</div>
						</th>
						<th style='width: 5em'>
							<div class='it'>Importo</div>
							<div class='en'>Amount</div>
						</th>
					</tr>
				</thead>
				<tbody>
				%for riga in righe.values():
					<tr>
						<td>
							${riga['tariffa_codice']}
						</td>
						<td>
							${riga['tariffa_descrizione']}
							%if riga['@assopy_partecipante_ordine_riga_id.nome'] or riga['@assopy_partecipante_ordine_riga_id.cognome']:
								 - [${riga['@assopy_partecipante_ordine_riga_id.nome'] or ''} ${riga['@assopy_partecipante_ordine_riga_id.cognome'] or ''}]
							%endif
						</td>
						<td class='num'>
							1
						</td>
						<td class='num'>
							${mainpage.toText(riga['importo'] / (1+(float(riga['aliquota_iva'])/100)), locale='it', format='#,###.00')}
						</td>
					</tr>
				%endfor
				%for i in range(6-len(righe)):
				<tr>
					<td>&nbsp;</td>
					<td>&nbsp;</td>
					<td>&nbsp;</td>
					<td>&nbsp;</td>				
				</tr>
				%endfor
				<tr class='foot'>
					<td>&nbsp;</td>
					<td>&nbsp;</td>
					<td>&nbsp;</td>
					<td>&nbsp;</td>				
				</tr>
				</tbody>
			</table>
			
			<table class='rows total' style="float: right">
				<thead>
					<tr>
						<th style='width: 10em'>
							<div class='it'>Totale Donazione</div>
							<div class='en'>Total Donation</div>
						</th>
					</tr>
				</thead>
					<tbody>
					<tr class='foot'>
						<td class='num' style='font-weight: bold;'>
							${mainpage.toText(ordine['totale'], locale='it', format='#,###.00')}
						</td>
					</tr>
					</tbody>
				</table>

		</div>
	</body>
</html>

#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool
import urllib,urllib2
import time
import hashlib
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrstring import templateReplace
import thread
import os

class SmsMobyt(GnrBaseService):

    def __init__(self, parent, username=None, password=None, url=None, auth=None, sender=None):
        self.parent = parent
        self.username=username
        self.password=password
        self.url=url
        self.auth=auth
        self.sender=sender

    def sendsms_template(self, receiver=None,sender=None,
                       opcode=None, data=None, quality=None, messageId=None, batchId=None,
                       urlbatch=None, async=False, **kwargs):
        def get_templated(field):
            value = datasource.get(field)

            if value:
                return templateReplace(value, datasource)
        receiver = receiver or get_templated('receiver')
        sender = sender or get_templated('sender')
        opcode = opcode or get_templated('opcode')
        sender = sender or get_templated('sender')
        quality = quality or get_templated('quality')
        messageId = messageId or get_templated('messageId')
        urlbatch = urlbatch or get_templated('urlbatch')
        data = data or get_templated('data')
        data = templateReplace(data, datasource)
        self.sendsms(receiver=receiver, sender=sender, opcode=opcode,data=data, quality=quality, messageId=messageId,
                     batchId=batchId, urlbatch=urlbatch, async=async)

    def sendsms(self, receiver=None,sender=None,
                       opcode=None, data=None, quality=None, messageId=None, batchId=None,
                       urlbatch=None, async=None,**kwargs):
        parameters=dict()
        parameters['id']=self.username
        parameters['operation']=opcode or 'TEXT'
        sender = sender or self.sender
        if ',' in receiver:
            parameters['rcptbatch']=receiver  
        else:
            parameters['rcpt']=receiver  
        parameters['from']=sender    
        parameters['data']=data 
        if quality:
            parameters['qty']=quality
        parameters['act']=str(messageId or int(time.time()*1000000))
        if batchId:
            parameters['idbatch']=batchId   
        if  urlbatch:
            parameters['urlbatch']=urlbatch     
        if self.auth=='md5':
            ticket=[]
            for k in ['id', 'operation', 'rcpt', 'from', 'data']:
                if parameters[k]:
                    ticket.append(parameters[k])
                else:
                    parameters.pop(k)
            ticket.append(self.password)
            parameters['ticket'] = hashlib.md5(''.join(ticket)).hexdigest().strip()
        else:
            parameters['password'] = password
        parameters=urllib.urlencode(parameters)
        if not async:
            urllib2.urlopen(self.url,parameters)
        else:
            thread.start_new_thread(urllib2.urlopen,(self.url,parameters))

        
    """
2.1 ticket
    √® un parametro obbligatorio se l'autenticazione associata all' account √® di tipo MD5. Usato come token di autenticazione. 
    Il valore del ticket deve essere ricavato applicando la funzione hash MD5 (con output in esadecimale, lowercase) alla 
    stringa risultante dalla concatenazione dei parametri: id, operation, rcpt, from, data, password. 
    Il valore del parametro password viene fornito all'atto dell'attivazione dell'account.
    L'autenticazione √® soddisfatta se l'hash MD5 ricalcolato dal gateway sui parametri ricevuti 
    e la copia locale della password, √® uguale al ticket ricevuto.
    Qualora un parametro non venga inserito nella richiesta POST/GET bisogna ometterlo anche dal calcolo del ticket.

2.2 id -> username
    √® un parametro obbligatorio. Il suo valore deve essere la login dell'account utilizzato.

2.3 password -> password
    √® un parametro obbligatorio se l'autenticazione associata all' account e' di tipo plain-password. 
    Il suo valore deve essere la password dell'account utilizzato.

2.4 operation -> opcode
    √® un parametro obbligatorio. Tramite questo parametro √® possibile indicare il tipo di messaggio che si intende 
    spedire o richiedere determinate informazioni sull'account che si sta utilizzando.
   
    Tipo di messaggio:
        ‚Ä¢ TEXT Il messaggio √® di tipo testo
        ‚Ä¢ MULTI Sono pi√π messaggi che vengono interpretati dal cellulare come un unico SMS
        ‚Ä¢ OLGO Il messaggio √® un logo operatore (Nokia Smart-Messaging)
        ‚Ä¢ GLGO Il messaggio √® un logo gruppo (Nokia Smart-Messaging)
        ‚Ä¢ RING Il messaggio √® una suoneria
        ‚Ä¢ 8BIT Il messaggio √® ad 8 bit
    
    Informazioni account:
        ‚Ä¢ GETCREDIT Ritorna il credito associato all'account Es.: OK 100000
        ‚Ä¢ GETBILL Ritorna il costo del singolo messaggio associato all'account Es.: OK 333
        ‚Ä¢ GETMESS Ritorna il numero di messaggi ancora disponibili, con la relativa qualit√† Es.: OK 10 HQS 
          Sono disponibili ancora 10 messaggi di alta qualit√†
        ‚Ä¢ GETNOTIFY Ritorna il numero di notifiche ancora disponibili Es.: OK 1000
        ‚Ä¢ GETIP Ritorna l'IP associato all'account o un'espressione regolare in presenza di pi√π IP (uno o pi√π IP differenti,
          una o pi√π reti differenti).
        ‚Ä¢ GETURL Ritorna l'URL utilizzato per l'inoltro delle notifiche
        ‚Ä¢ GETMSENT Ritorna il numero di messaggi spediti dal giorno di creazione dell'account.
        ‚Ä¢ GETNSENT Ritorna il numero di notifiche spedite dal giorno di creazione dell'account.

2.5 rcpt -> receiver
    √® un parametro obbligatorio. Indica il numero del terminale mobile a cui spedire il messaggio, 
    secondo il formato internazionale +JJxxxyyyzzkk (Es.: +393112224455)
    
2.6 from -> sender
    √® un parametro opzionale. Indica il generante del messaggio. Il suo valore sar√† mostrato dal
    terminale mobile come mittente del messaggio. Sono consentiti due formati, alfanumerico o 
    un numero nel formato internazionale +393112224455 oppure 00393112224455. 
    Il primo formato consente di utilizzare stringhe alfanumeriche di lunghezza compresa tra 1
    ed 11 caratteri. Nel secondo caso la sua lunghezza non deve essere superiore a 16 caratteri.
      
2.7 data -> data
    √® un parametro obbligatorio. Indica il corpo del messaggio. La lunghezza del parametro dipende dal tipo di messaggio che si invia.
    Per i tipi di operation TEXT il messaggio deve essere in ASCII e la sua lunghezza non deve superare i 160 caratteri.
    Per i tipi di operation OLGO e GLGO deve essere utilizzato l'encoding OTA, la sua lunghezza non deve superare
    i 260 byte per OLGO e 266 byte per GLGO.
    In modalit√† 8BIT deve contenere il payload, codificato in esadecimale. La sua lunghezza sommata alla lunghezza 
    dell'UDH (parametro riportato di seguito, User Data Header) non deve superare i 280 byte.
    Nel caso di un messaggio Wap push il limite della lunghezza testo + URL √® di 126 caratteri.
    Per i tipi di operation MULTI ogni sms non deve superare i 134 caratteri.
    
2.8 udh (omitted)
    √® un parametro obbligatorio, solo per la modalit√† 8BIT, deve contenere lo User Data Header, 
    codificato in esadecimale, deve essere omesso il primo ottetto, l'UDHL (User Data Header Length) 
    il suo valore √® calcolato dal gateway sms.

2.9 qty -> quality
    √® un parametro opzionale. Indica la qualit√† dell' SMS, i valori che questo parametro pu√≤ assumere sono :
        ‚Ä¢ ll (doppia lettera elle minuscola) Qualit√† bassa.
        ‚Ä¢l (lettera elle minuscola) Qualit√† media.
        ‚Ä¢h Qualit√† alta.
        ‚Ä¢a Qualit√† automatica.
        Se il valore di questo parametro √® nullo o differente dai valori possibili (indicati sopra),
        il gateway sms utilizzer√† la qualit√† di default cio√® la qualit√† automatica.
        
2.10 act -> messageId
    Deve contenere un valore intero decimale di lunghezza massima 20 cifre. Questo valore identificher√†
    il messaggio spedito, e sar√† inoltrato al client come notifica di avvenuta ricezione.
    
2.11	rcptbatch -> receiver (se ha ',')
    Pu√≤ contenere una lista di numeri a cui spedire lo stesso messaggio. Ogni numero deve essere espresso
    come descritto per il parametro rcpt Es.: +39329123311,+39123411101,+39318199199
    Consultare la sezione ‚ÄúSPEDIZIONI BATCH‚Äù dello stesso documento.
    
2.12 idbatch -> batchId
    Pu√≤ contenere un identificativo da associare alla spedizione batch che si sta richiedendo.
    Il valore sar√† restituito al cliente al termine della spedizione attraverso una POST HTTP ad URL precedentemente settata.
    L'identificativo della spedizione batch non pu√≤ superare lunghezza 255 e pu√≤ contenere esclusivamente caratteri compresi
    nell'insieme [A-Za-z0-9]. Es.: AF1234U761JJ
    Consultare la sezione ‚ÄúSPEDIZIONI BATCH‚Äù dello stesso documento.
    
2.13 urlbatch
    pu√≤ contenere un URL che sar√† richiamato dal Gateway SMS al termine della spedizione batch richiesta. 
    I parametri che saranno passati sono descritti nella sezione ‚ÄúSPEDIZIONI BATCH‚Äù.

"""
#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

from gnr.core.gnrstring import templateReplace


class GnrCustomWebPage(object):
    maintable='assopy.partecipante'
    py_requires='basecomponent:Public,standard_tables:TableHandler,utils:SendMail'
    
    def windowTitle(self):
        return '!!Assopy Partecipanti'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Partecipanti'
        
    def columnsBase(self):
        return """fullname/Nome e Cognome:10,qualifica_badge/Badge:10,py_level/Esp:2,presenza/Giornate:7,
                   @cliente[ragione_sociale/Cliente:10,provincia/Pr:2,localita:8],
                   @cliente.@utente_id[username:6,email:10],fattura/Fattura:6,tariffa_tipo/Tipo:4"""
        
    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.partecipante.cognome',width='20em')
        fb.field('assopy.partecipante.nome',width='20em') 
        fb.field('assopy.partecipante.qualifica_badge',width='20em') 
        fb.field('assopy.partecipante.presenza_g1',lbl=u"!!Venerdì")
        fb.field('assopy.partecipante.presenza_g2',lbl=u"!!Sabato")
        fb.field('assopy.partecipante.presenza_g3',lbl="!!Domenica")
        fb.field('assopy.partecipante.py_level', width='3em', lbl="!!Esperienza python")
        fb.field('assopy.partecipante.posti_ristorante', width='3em', lbl='!!Posti PyFiorentina')
               
        
    def orderBase(self):
        return 'cognome'
        
    def conditionBase(self):
        return ("$data_conferma IS NOT NULL AND $cognome >'' and $nome >''",{})
    
    def queryBase(self):
        return dict(column='cognome',op='contains', val=None,runOnStart=True)

    def action_mail_treni(self, selection, **kwargs):
        emails = [u[0] for u in selection.output('distinct','_cliente__utente_id_email')]
        
        params_list = [{'email':e} for e in emails]
        send_errors = self.sendMailTemplateMany('treni.xml', 'email', 'locale', params_list)
        
        if send_errors:
            return 'Problemi di spedizione a: %s' % ', '.join(send_errors)
        else:
            return 'Email spedite'
        

    def action_mail_situazione_partecipanti(self, selection, **kwargs):
        users = [u[0] for u in selection.output('distinct','_cliente__utente_id_username')]
        partecipanti = self.db.query('assopy.partecipante', 
                        columns='$username, $email, $nomeutente, $locale, $presenza, $ordine_num, $numero_riga, $fattura_num, *',
                        where='@utente.username IN :users AND @ordine_riga_id.@ordine_id.data_conferma IS NOT NULL', 
                        users=users,
                        relationDict={'username':'@utente.username', 'email':'@utente.email', 
                                      'nomeutente':'@utente.nome_cognome', 'locale':'@utente.locale',
                                      'ordine_num':'@ordine.numero', 'numero_riga':'@ordine_riga_id.numero_riga', 
                                      'fattura_num':'@ordine.fattura_num'}
                        ).selection()
        mailtpldict = {}
        partecipanti.totalize(group_by=['username'], keep=['username', 'email', 'nomeutente','locale'], sum=['posti_ristorante'])
        params_list = []
        for pnode in partecipanti.totalizer():
            params = {}
            for userpar in ['email', 'nomeutente','locale']: 
                params[userpar] = pnode.getAttr('k_%s' % userpar)
                
            locale = params['locale'] or self.locale
            mailtpl = mailtpldict.get(locale)
            if not mailtpl:
                mailtpl = self.getMailTemplate('user_situation.xml', locale=locale)
                mailtpldict[locale] = mailtpl
            
            plist = []
            user_part = partecipanti.output('data', subtotal_rows=pnode.label)
            for partecipante in user_part:
                partecipante = dict([(k,v or '') for k,v in partecipante.items()])
                partecipante['numero_riga'] = (partecipante['numero_riga'] or 0) + 1
                if not partecipante['fattura_num']:
                    partecipante['numero_riga'] = "%s     *** da saldare all'ingresso ***" % partecipante['numero_riga']
                plist.append(templateReplace(mailtpl['onerow'], partecipante))
            params['posti_ristorante'] = pnode.getAttr('sum_posti_ristorante')
            params['ptext'] = '\r\n'.join(plist)
            params['link'] = self.externalUrl('assopy/gestione_partecipanti.py')
            params['username'] = pnode.getAttr('k_username')
            params_list.append(params)
            
                                
        send_errors = self.sendMailTemplateMany('user_situation.xml', 'email', 'locale', params_list)
        if send_errors:
            send_errors=', '.join(send_errors)
            return 'Problemi di spedizione a: %s' %  send_errors
        else:
            return 'Email spedite'


#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Gestione unita """
import time
import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='heroscape.unita'
    py_requires='public:Public,standard_tables:TableHandler'
    css_requires='generali.css'
    def windowTitle(self):
        return '!!Heroscape'
         
    def pageAuthTags(self, method=None, **kwargs):
        return None
        
    def tableWriteTags(self):
        return None
        
    def tableDeleteTags(self):
        return None
        
    def barTitle(self):
        return u'!!Gestione unità'
        
    def columnsBase(self,):
        return """@generale_id.nome/Generale:7,
                  nome:14,
                  @razza_id.nome/Razza:10,
                  @classe_id.nome/Classe:10,
                  @personalita_id.nome/Pers.:10,   
                  vite:3,
                  movimento/Mov.:3,
                  gittata/Git.:3,
                  attacco/Att.:3,
                  difesa/Dif.:3,
                  costo_punti/Costo.:4"""
                  

    def formBase(self,pane,datapath='',disabled=False):
        card=pane.div(datapath=datapath, _class='^form.record.@generale_id.nome', height='500px', width='800px')
        #self.stileCarta(card, disabled)
        self.formCarta(card, datapath, disabled)
        
    

    
    def rpc_imageUrl(self,cardname):
        img='%s.gif' % cardname.replace(' ','_')
        tgt_img='%s_tgt.gif' % cardname.replace(' ','_')
        imgpath=self.utils.siteFolder('data', 'images',img,relative=False)
        tgtpath=self.utils.siteFolder('data', 'images',tgt_img,relative=True)
        return Bag(dict(img=imgpath,tgt=tgtpath, site=self.utils.siteFolder(relative=True)))
        
    def formCarta(self, card, datapath, disabled):
        card.dataRpc('.images', 'imageUrl', cardname='^.nome')
        fb = card.formbuilder(datapath=datapath,cols=3,
                              border_spacing='7px',margin_top='1em',
                              disabled=disabled)
        fb.div('^.nome', _class='nome', colspan=3)
        form=fb.formbuilder(cols=2,disabled=disabled,colspan=2)
        #related=fb.formbuilder(cols=1,disabled=disabled,colspan=1)
        #punteggi=fb.formbuilder(cols=1,disabled=disabled,colspan=1)
        images=fb.formbuilder(cols=1, colspan=1)
        form.field('heroscape.unita.nome',width='12em',value='^.nome',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.unita.costo_punti',width='4em',value='^.costo_punti',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio', font_wight='bold')
        form.field('heroscape.unita.generale_id',width='10em',value='^.generale_id',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.numero_miniature',width='4em',value='^.numero_miniature',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.tipo_id',width='10em',value='^.tipo_id',
                    disabled=disabled, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.unita.vite',width='4em',value='^.vite',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio', color='red')
        form.field('heroscape.unita.razza_id',width='10em',value='^.razza_id',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.movimento',width='4em',value='^.movimento',disabled=disabled,
                                required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.classe_id',width='10em',value='^.classe_id',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.gittata',width='4em',value='^.gittata',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.personalita_id',width='10em',value='^.personalita_id',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.attacco',width='4em',value='^.attacco',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.prodotto_id',width='10em',value='^.prodotto_id',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        form.field('heroscape.unita.difesa',width='4em',value='^.difesa',disabled=disabled,
                            required=True, invalidMessage='!!Obbligatorio')
        #form.field('heroscape.abilita.nome', lbl='Abilità1', width='10em', value='^.@heroscape_abilita_unita_id.nome', disabled=disabled)
        
        
        images.img(_class='cardimg',src='^.images.img')
        images.img(_class='cardimg',src='^.images.tgt')

                      
        
        
        
       
        
        


    def orderBase(self):
        return 'costo'
    
    def queryBase(self):
        return dict(column='@generale_id.nome',op='contains', val=None)
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
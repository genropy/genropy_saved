#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo Hello World """

from gnr.web.gnrwebcore import GnrWebPage, GnrWebClientError
import datetime, subprocess
from gnr.core.gnrbag import Bag, DirectoryResolver
import weakref

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root,padding='2px')
        self.menubar.data('Commands',self.commandMenu(),
                                   action="function(attributes){alert(attributes.toSource())}")
        layout = root.layoutContainer(name='form', height='100%')
        layout.contentPane(name='top', layoutAlign='top').div('Test Placer', _class='demotitle')
        
        client = layout.contentPane(name='client', layoutAlign='client', padding='2px'
                ).splitContainer(name='split', sizerWidth=2, height='100%', orientation='vertical')
        top=client.contentPane(name='formparams', sizeShare=25, background_color='silver')
        #self.topTest(top)
        self.makeTop(top)
        form=client.contentPane(gnrId='mypane',name='testpane', sizeShare=80, 
                                background_color='yellow',
                                remoteContent='makeForm:{params:"@params"}')
                                

    def topTest(self, pane):
        fb=pane.formbuilder(cols=4,datasource='params')
        fb.input(lbl='Dove',fld='utils.anagrafiche.an_localita',datasource='loc',pos='*,-1')
        fb.div(lbl='Data',fld='utils.anagrafiche.sy_inserito_il',datasource='dd',default=datetime.date.today(),pos='+,0')
        fb.input(caption='confermato',fld='utils.anagrafiche.an_aa_dati_anagrafici',datasource='mm',pos='*,3')
        fb.input(lbl='peso',dtype='R',default=45.98,datasource='nnn',pos='+,-2')
                
    def makeTop(self, pane):
        alignmenu='[["Left","left"], ["Center","center"],["Right","right"],["Justify","justify"]]'
        valignmenu='[["Top","top"], ["Middle","middle"],["Bottom","bottom"],["Baseline","baseline"]]'
        fb=pane.formbuilder(cols=2,datasource='params')
        fb.input(lbl='Columns',datasource=':cols',dtype='L',default=2)
        fb.input(lbl='Border',datasource=':border',pos='+')
        fb.select(lbl='Label position',datasource=':lblpos',default='L',values='[["Left","L"], ["Top","T"]]')
        fb.select(lbl='Label align',datasource=':lblalign',default='right',values=alignmenu)
        fb.select(lbl='Label vertical align',datasource=':lblvalign',default='middle',values=valignmenu)
        fb.select(lbl='Field align',datasource=':fldalign',default='left',values=alignmenu)
        fb.select(lbl='Field vertcal align',datasource=':fldvalign',default='middle',values=valignmenu)
        fb.input(lbl='Cell spacing',datasource=':cellspacing')
        fb.input(lbl='Cell padding',datasource=':cellpadding')
        fb.button('Make form',action='genro.mypane.updateContent()',pos='+,-1')
        
    def commandMenu(self):
        b=Bag()
        b.setItem('make', None, action='genro.mypane.updateContent()')
        b.setItem('crea', None)
        b.setItem('-', None)
        b.setItem('trasforma.basso', None, caption=u'Giù', dir='d')
        b.setItem('trasforma.alto', None, caption='Su', dir='u')
        return b
        
    def rpc_makeForm(self, params=None):
        result=self.newSourceRoot()
        if params:
            self.gnotify('params:', str(params))
            params=params.asDict(ascii=True)
            form=result.formbuilder(datasource='formdata',dbtable='utils.anagrafiche',**params)
            #form.textarea(lbl='Note',cols=30,rows=6,rowspan=8,datasource=':note',default='pippo')
            #form.input(lbl='Campo x',datasource=':aa',default='a')
            #form.input(lbl='Campo y',rowspan=8,datasource=':bb',default='b')
            form.place(self.testField1())
            #form.input(fld='an_ragione_sociale',datasource=':ragsoc')
        return result
        
    def testField1(self):
        fields=[{'fld':'an_ragione_sociale','datasource':':ragsoc','lbl':'pippo'},
               {'fld':'an_indirizzo','datasource':':indirizzo'},
               {'fld':'an_cap','datasource':':cap'},
               {'fld':'an_localita','datasource':':loc'},
               {'fld':'an_provincia','datasource':':prov'},
               {'tag':'button','caption':'manda zombo in galera','action':'alert("a marcire!")'},
               {'fld':'sy_modificato_il','datasource':':mod'},
               {'fld':'tc_aa_telecomunicazioni','datasource':':tc'},
               {'tag':'dbselect','lbl':'vacanza a','datasource':':vac', 'dbtable':'utils.localita'},
               {'fld':'utils.localita.localita','lbl':'loc','datasource':':posto', 'validate_db':'utils.localita', 'tag':'dbselect'},
               {'tag':'bagfilteringtable','lbl':'clienti','_class':'dojo','alternateRows':'True','columns':'an_ragione_sociale,an_indirizzo','datasource':'_valid.utils.localita.lastrecord.@utils_anagrafiche_an_localita'}]
        return fields
        
    
    def testField3(self):
        fields=[{'tag':'textarea','content':'pippo','datasource':':note','lbl':'Note','cols':'40','rows':'12','rowspan':'2'},
               {'tag':'input','lbl':'Campo x','default':'aa','datasource':':x'},
               {'tag':'input','lbl':'Campo y','default':'bb','datasource':':y'},
               {'tag':'input','lbl':'Campo z','default':'bb','datasource':':z'}
               ]
        return fields
    def testField2(self):
        fields=[{'fld':'an_ragione_sociale','datasource':':ragsoc', 'colspan':'2'},
               {'fld':'an_indirizzo','datasource':':indirizzo','pos':'+','colspan':'2'},
               {'fld':'an_cap','datasource':':cap','pos':'+'},
               {'fld':'an_provincia','datasource':':prov'},
               {'fld':'an_localita','datasource':':loc', 'colspan':'2', 'size':'40'},
               {'tag':'textarea','datasource':':note','lbl':'Note','cols':'40','rows':'5','rowspan':'5','pos':'+'},
               {'fld':'ds_codice_fiscale','datasource':':codfisc'},
               {'fld':'ds_partita_iva','datasource':':piva'}
               ]
        return fields
        
#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
    
    

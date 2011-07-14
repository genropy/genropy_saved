# -*- coding: UTF-8 -*-

# template.py
# Created by Francesco Porcari on 2011-07-11.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=2)
        fb.dbSelect(dbtable='glbl.regione',value='^regione',lbl='Regione')
        fb.dbSelect(dbtable='adm.doctemplate',value='^doctemplate',lbl='Template')
        root.div('^renderedtemplate')
        root.dataRpc('renderedtemplate', 'renderTemplate', doctemplate_id='^doctemplate',
                     templates='^html_template_name', #carta intestata se c'è
                      _POST =True,record_id='^regione',_if='doctemplate_id')


    def rpc_renderTemplate(self, doctemplate_id=None, record_id=None, templates=None, **kwargs):
        doctemplate = self.db.table('adm.doctemplate').record(pkey=doctemplate_id).output('bag')
        templatebag = doctemplate['templatebag']
        if not templatebag:
            return
        tpltable = self.db.table('adm.doctemplate')
        tplbuilder = tpltable.getTemplateBuilder(templatebag=templatebag, templates=templates)
        return tpltable.renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))

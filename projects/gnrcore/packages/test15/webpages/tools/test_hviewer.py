# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    js_requires = 'test_hviewer'
    css_requires = 'test_hviewer'

    #dojo_source=True
    def main(self,root,**kwargs):
        tblnuts = self.db.table('glbl.nuts')
        b = Bag()
        root_id = tblnuts.readColumns(columns='$id',where='$code=:c',c='IT')
        z = tblnuts.query(where="""$hierarchical_pkey LIKE :p || '%%'""",p=root_id,
                        order_by='$hierarchical_pkey',columns='$hierarchical_pkey,$code,$description,$level').fetch()
        comuni_gruped = self.db.table('glbl.comune').query(columns='$codice_comune,$sigla_provincia,$denominazione,$superficie,$popolazione_residente,@sigla_provincia.nome AS nome_provincia',
                        addPkeyColumn=False).fetchGrouped('nome_provincia')  
        for r in z:
            r = dict(r)
            v = Bag()
            b.setItem(r['hierarchical_pkey'].replace('/','.'), v,**r)
            if r['level'] == 3 and r['description'] in comuni_gruped: 
                for c in comuni_gruped[r['description']]:
                    c['level'] = r['level']+1
                    v.setItem(c['codice_comune'],None,**dict(c))

        root.data('albero_comuni',b)   
        root.div(margin='20px').tree(storepath='albero_comuni',labelCb='return treeCompanion.labelCb(this,400);',
                    hideValues=True,_class="testhviewer branchtree noIcon",autoCollapse=True)

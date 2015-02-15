# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    js_requires = 'test_hviewer'
    css_requires = 'test_hviewer'

    def isDeveloper(self):
        return True
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

        root.data('albero_comuni_z',b)   
        root.dataFormula('albero_comuni','albero_comuni.deepCopy()',albero_comuni='=albero_comuni_z',_onStart=1000)
        bc = root.borderContainer()
        left = bc.contentPane(region='left',width='600px',splitter=True)
        bc.contentPane(region='center',background='red')
        tree = left.treeGrid(storepath='albero_comuni')
        tree.column('descrizione',name='Descrizione',
                    contentCb="""return this.attr.description || (this.attr.codice_comune +'-'+ this.attr.denominazione)""")
        tree.column('superficie',dtype='L',size=60,emptyValue=0,name='Sup.')
        tree.column('popolazione_residente',dtype='L',size=60,emptyValue=0,name='Pop.')
        bc.contentPane(region='bottom',height='150px',splitter=True,background='green')

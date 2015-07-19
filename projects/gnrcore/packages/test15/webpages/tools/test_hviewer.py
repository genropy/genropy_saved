# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag
from random import randint

class GnrCustomWebPage(object):
    js_requires = 'test_hviewer'
    css_requires = 'test_hviewer'
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def isDeveloper(self):
        return True


    def test_1_nuts(self,root,**kwargs):
        b = self.getComuniGrouped()
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

    def test_2_dynamic(self,root,**kwargs):
        bc = root.borderContainer(height='600px')
        bc.contentPane(region='top').button('Start',fire='.start')
        center = bc.contentPane(region='center')
        treeroot = center.div()
        rpc = bc.dataRpc(".nutsdata",self.getComuniGrouped,_fired='^.start',_lockScreen=True)
        rpc.addCallback("""
            treeroot.clearValue();
            treeroot.freeze()
            treeGrid = treeroot._('treeGrid',{'storepath':'.nutsdata'});
            var truevalue =  "<div style='background:green;height:15px;'>&nbsp;</div>";
            var falsevalue =  "<div style='background:red;height:15px;'>&nbsp;</div>";
            var format = truevalue+',&nbsp;'    
            treeGrid._('column',{field:'descrizione',name:'descrizione',
                contentCb:"return this.attr.description || (this.attr.codice_comune +'-'+ this.attr.denominazione)"
                })
            for (var i=0; i<19; i++){
                treeGrid._('column',{field:'s_'+_F(i,'00'),size:30,name:'C'+_F(i,'00'),format:format,dtype:'B'});
            }
            treeroot.unfreeze();
            return result   

            """,treeroot=treeroot)

    @public_method
    def getComuniGrouped(self):
        tblnuts = self.db.table('glbl.nuts')
        b = Bag()
        root_id = tblnuts.readColumns(columns='$id',where='$code=:c',c='IT')
        z = tblnuts.query(where="""$hierarchical_pkey LIKE :p || '%%'""",p=root_id,
                        order_by='$hierarchical_pkey',columns='$hierarchical_pkey,$code,$description,$level').fetch()
        comuni_gruped = self.db.table('glbl.comune').query(columns='$codice_comune,$sigla_provincia,$denominazione,$superficie,$popolazione_residente,@sigla_provincia.nome AS nome_provincia',
                        addPkeyColumn=False).fetchGrouped('nome_provincia')  
        weeks = dict()
        for k in range(20):
            weeks['s_%02i' %k] = False
        for r in z:
            r = dict(r)
            v = Bag()
            b.setItem(r['hierarchical_pkey'].replace('/','.'), v,**r)
            if r['level'] == 3 and r['description'] in comuni_gruped: 
                for c in comuni_gruped[r['description']]:
                    w = dict(weeks)
                    c['level'] = r['level']+1
                    l = randint(0,19)
                    l2 = randint(l,19)
                    for k in range(l,l2):
                        w['s_%02i' %k] = True
                    c.update(w)
                    v.setItem(c['codice_comune'],None,**dict(c))
        return b

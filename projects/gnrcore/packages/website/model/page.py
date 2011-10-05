#!/usr/bin/env python
# encoding: utf-8
# VISTOAL: 291008
class Table(object):
   
    def config_db(self, pkg):
        """website.page"""
        tbl =  pkg.table('page', name_plural = u'!!Pages', pkey='id',name_long=u'!!Page', rowcaption='$title')
        self.sysFields(tbl)
        tbl.column('title', size=':30',name_long = '!!Title',base_view=True)
        tbl.column('extended_title', name_long = '!!Extended Title')
        tbl.column('permalink', size=':254',name_long = '!!Permalink')
        tbl.column('content',name_long = '!!Content')
        tbl.column('position', dtype='I',name_long = '!!Position')
        tbl.column('publish',dtype='D', name_long = '!!Publish')
        tbl.column('folder',size=':22',name_long='!!Folder').relation('website.folder.id',
                                                                        relation_name='pages',
                                                                        mode='foreignkey',
                                                                        onDelete='CASCADE')
        tbl.formulaColumn('path',"""CASE WHEN #THIS.publish>=:env_workdate 
                                            THEN '<a target=\"_blank\" href=\"/'||translate(@folder.code, '.', '/')||'/'||$permalink||'\">'||$permalink||'</a>'
                                            ELSE '<a target=\"_blank\" href=\"/'||'preview/'||translate(@folder.code, '.', '/')||'/'||$permalink||'\">(Preview)'||$permalink||'</a>'
                                            END
                                    """)
        #
        #'<a href=\"'||translate(@folder.code, '.', '/')||'/'||$permalink||'\">'||$permalink||'</a>'
        #
        #translate(@folder.code, '.', '/')||'/'||$permalink
        #       tbl.formulaColumn('indirizzo_completo',"$indirizzo||'<br/>'||$cap||' '||$localita||'-'||$provincia")
        #       
        #       tbl.formulaColumn('bancali','ceil($n_colli/NULLIF(@prodotto_id.n_colli_per_pallet,0))',dtype='R')
        #           tbl.formulaColumn('esistenza', """(SELECT sum(quantita * segno) FROM #ENV(getDepositoId))""",
        #                           dtype='qta',name_long=u'!!Esistenza')
        #
        #       def env_getDepositoId(self):
        #           deposito_id = self.db.currentEnv.get('deposito_id')
        #           data_esistenza = self.db.currentEnv.get('data_esistenza') or self.db.currentEnv.get('workdate')
        #           if deposito_id:
        #               return """automag.automag_movimento AS movimento,automag.automag_operazione AS operazione 
        #                                   WHERE movimento.lotto_id=#THIS.id AND
        #                                       movimento.operazione_id=operazione.id AND
        #                                       operazione.deposito_id = '%s' AND 
        #                                       operazione.data<= '%s' """%(deposito_id,data_esistenza)

    def trigger_onInserting(self, record):
        if record['content']:
            contenuto=record['content']
            if contenuto:
                record['content'] = str(contenuto).replace('../_site','/_site')

    def trigger_onUpdating(self, record,old_record):
        if record['content']:
            record['content'] = record['content'].replace('../_site','/_site')
            
    def getPageByPermalink(self,permalink=None,**kwargs):
        if not permalink:
            return []
        return self.query(where='$permalink=:perma',perma=permalink,**kwargs).fetch()
        
    def folder_view(self,struct):
        r = struct.view().rows()
        r.cell('@folder.title',name='Folder',width='10em')
        r.cell('position',width='3em')
        r.cell('title',name='Title',width='20em')
        r.cell('permalink',name='Permalink',width='20em')
        r.cell('path',width='100%')
        return struct
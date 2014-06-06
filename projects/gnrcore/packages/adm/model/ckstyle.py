#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('ckstyle', pkey='id', name_long='Ckeditor style', name_plural='!!Ckeditor styles',caption_field='name',lookup=True)
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('element' ,values='div,span,h1,h2,h3',name_long='!!Dom element',name_short='Element')
        tbl.column('styles',name_long='!!Styles')
        tbl.column('attributes',name_long='!!Attributes')
        tbl.column('stylegroup',name_long='!!Group')
        tbl.formulaColumn('sgroup',"COALESCE($stylegroup,'')")

    def getCustomStyles(self,stylegroup=None):
        groups = stylegroup.split(',') if stylegroup else []
        groups = ['']+groups
        styles = self.query(where="$sgroup IN :gr",
                        addPkeyColumn=False,
                        gr = groups,
                        columns='$name,$element,$styles,$attributes,$sgroup').fetchGrouped('sgroup')
        cs = dict()
        for gr in groups:
            stylelist = styles[gr]
            sdict = dict()
            for st in stylelist:
                st = dict(st)
                st.pop('sgroup')
                sdict[st['name']] = st
            cs.update(sdict)
        if cs:
            return [dict(v) for v in cs.values()]




 # dict()
 # cs.update(style_table.query(where="$stylegroup IS NULL OR $stylegroup=''",g=stylegroup,columns='$name,$element,$styles,$attributes').fetchAsDict('name'))
 # if stylegroup:
 #             for st in stylegroup.split(','):
 #                 cs.update(style_table.query(where='$stylegroup=:g',g=stylegroup,columns='$name,$element,$styles,$attributes').fetchAsDict('name'))
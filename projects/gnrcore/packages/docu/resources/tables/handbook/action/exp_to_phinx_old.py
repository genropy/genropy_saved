# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag

caption = 'Export to sphinx'
description = 'Export to sphinx'
tags = '_DEV_'
class Main(BaseResourceBatch):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'ESW'
    batch_title =  'Export to sphinx'
    batch_cancellable = False
    batch_delay = 0.5

    def do(self):
        root_id = self.batch_parameters['extra_parameters']['root_id']
        if self.batch_parameters['from_root']:
            root_id=None
        doc_data = self.tblobj.getHierarchicalData(root_id=root_id, condition='$is_published IS TRUE')['root']
        self.destpath=self.db.application.getPreference('.sphinx_path',pkg='docu')
        self.languages = self.batch_parameters['languages'].split(',')
        
        toc = self.prepare(doc_data,[])
        pathlist=[]
        for l in self.languages:
            self.createFile(pathlist=pathlist, lang=l, name='index', title='Table of contents', rst='', toc=toc)

    def prepare(self, data, pathlist):
        result=[]
        for n in data:
            v = n.value
            record = self.tblobj.record(n.label).output('dict')
            name=record['name']
            docbag = Bag(record['docbag'])
            toc=[]
            if isinstance(v,Bag):
                result.append('%s/%s.rst' % (name,name))
                toc=self.prepare(v, pathlist+[name])
            else:
                result.append(name)
            for l in self.languages:
                lbag=docbag[l]
                if not lbag['title']:
                    continue
                self.createFile(pathlist=pathlist+[name], lang=l, name=name, title=lbag['title'], rst=lbag['rst'], toc=toc)
        return result
             
    def createFile(self, pathlist=None, lang=None, name=None, title=None, rst=None, toc=None):
        print 'createFile',name
        tocstring='\n%s\n\n   %s' % (".. toctree::", '\n   '.join(toc))
        content = '\n'.join([title, '='*len(title), tocstring, '\n\n', rst])
        
        storageNode = self.page.site.storageNode('/'.join([self.destpath,lang]+pathlist))
        with storageNode.child('%s.rst' % name).open('wb') as f:
            f.write(content)


    def table_script_parameters_pane(self,pane,**kwargs):
        fb = pane.formbuilder(cols=3, border_spacing='5px',)
        fb.checkbox(value='^.from_root', lbl='', label='Start from root', colspan=3)
        languages = [l['code'] for l in self.db.table('docu.language').query().fetch()]
        fb.data('.languages', ','.join(languages))
        fb.checkBoxText(table='docu.language', lbl='Languages:', value='^.languages', cols=3)
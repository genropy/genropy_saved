# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
import re
import urllib
import os

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
        handbook_id = self.batch_parameters['extra_parameters']['handbook_id']
        self.handbook_record = self.tblobj.record(handbook_id).output('bag')
        self.doctable=self.db.table('docu.documentation')
        doc_data = self.doctable.getHierarchicalData(root_id=self.handbook_record['docroot_id'], condition='$is_published IS TRUE')['root']
        default_path = '%s/%s' % (self.db.application.getPreference('.sphinx_path', pkg='docu'),self.handbook_record['name'])
        self.destpath= self.handbook_record['sphinx_path'] or default_path
        self.imagesDict = dict()
        self.imagesPath='_static/images'
        toc = self.prepare(doc_data,[])
        self.createFile(pathlist=[], name='index', title='Table of contents', rst='', toc=toc)
        self.destNode = self.page.site.storageNode(self.destpath)
        for k,v in self.imagesDict.items():
            source_url = self.page.externalUrl(v) if v.startswith('/_vol') else v
            child = self.destNode.child(k)
            with child.open('wb') as f:
                f.write(urllib.urlopen(source_url).read())
        
    def prepare(self, data, pathlist):
        IMAGEFINDER = re.compile(r"\.\. image:: ([\w./]+)")
        LINKFINDER = re.compile(r" `([^`]*) <([\w./]+)>`_\b")

        result=[]
        for n in data:
            
            v = n.value
            record = self.doctable.record(n.label).output('dict')
            name=record['name']
            docbag = Bag(record['docbag'])
            toc=[]
            
            if n.attr['child_count']>0:
                result.append('%s/%s.rst' % (name,name))
                toc=self.prepare(v, pathlist+[name])
                self.curr_pathlist = pathlist+[name]
            else:
                result.append(name)
                self.curr_pathlist=pathlist
            lbag=docbag[self.handbook_record['language']]
            rst = IMAGEFINDER.sub(self.fixImages, lbag['rst'])
            rst = LINKFINDER.sub(self.fixLinks, rst)
            self.createFile(pathlist=self.curr_pathlist, name=name,
                            title=lbag['title'], 
                            rst=rst, toc=toc,
                            hname=record['hierarchical_name'],
                            tocdepth=1)
        return result

    def fixImages(self, m):
        old_filepath = m.group(1)
        filename = old_filepath.split('/')[-1]
        new_filepath = '%s/%s' % (self.imagesPath, '/'.join(self.curr_pathlist+[filename]))
        self.imagesDict[new_filepath]=old_filepath
        result = ".. image:: /%s" % new_filepath
        return result
        
    def fixLinks(self, m):
        prefix = '%s/' % self.db.package('docu').htmlProcessorName()
        title= m.group(1)
        ref = m.group(2).replace(prefix,'')
        result = ' :ref:`%s<%s>` ' % (title, ref)
        return result
        
             
    def createFile(self, pathlist=None, name=None, title=None, rst=None, toc=None, hname=None, tocdepth=None):
        reference_label='.. _%s:\n' % hname if hname else ''
        maxdepth_chunk= '   :maxdepth: %i' % tocdepth if tocdepth else ''
        if toc:
            tocstring='\n%s\n%s\n\n   %s' % (".. toctree::", maxdepth_chunk, '\n   '.join(toc))
        else:
            tocstring= ''
        content = '\n'.join([reference_label, title, '='*len(title), tocstring, '\n\n', rst])
        
        storageNode = self.page.site.storageNode('/'.join([self.destpath]+pathlist))
        with storageNode.child('%s.rst' % name).open('wb') as f:
            f.write(content)

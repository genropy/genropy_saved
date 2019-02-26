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
    batch_steps = 'prepareRstDocs,buildHtmlDocs'

    def pre_process(self):
        handbook_id = self.batch_parameters['extra_parameters']['handbook_id']
        self.handbook_record = self.tblobj.record(handbook_id).output('bag')
        self.doctable=self.db.table('docu.documentation')
        self.doc_data = self.doctable.getHierarchicalData(root_id=self.handbook_record['docroot_id'], condition='$is_published IS TRUE')['root']['#0']
        self.handbookNode= self.page.site.storageNode(self.handbook_record['sphinx_path']) #or default_path
        self.sphinxNode = self.handbookNode.child('sphinx')
        self.sourceDirNode = self.sphinxNode.child('source')
        self.page.site.storageNode('rsrc:pkg_docu','sphinx_env','default_conf.py').copy(self.page.site.storageNode(self.sourceDirNode.child('conf.py')))
        self.imagesDict = dict()
        self.imagesPath='_static/images'
        self.imagesDirNode = self.sourceDirNode.child(self.imagesPath)

    def step_prepareRstDocs(self):
        "Prepare Rst docs"

        if self.handbook_record['toc_roots']:
            toc_roots = self.handbook_record['toc_roots'].split(',')
            toc_trees = []
            for doc_id in toc_roots:
                if doc_id in self.doc_data.keys():
                    toc_elements = self.prepare(self.doc_data[doc_id],[])
                    r = self.doctable.record(doc_id).output('dict')
                    title = Bag(r['docbag'])['%s.title' % self.handbook_record['language']] 
                    toctree = self.createToc(elements=toc_elements, includehidden=True, titlesonly=True, caption=title)
                    toc_trees.append(toctree)
            tocstring = '\n\n'.join(toc_trees)
        else:
            toc_elements = self.prepare(self.doc_data,[])
            tocstring = self.createToc(elements=toc_elements, includehidden=True, titlesonly=True)

        self.createFile(pathlist=[], name='index', title=self.handbook_record['title'], rst='', tocstring=tocstring)
        for k,v in self.imagesDict.items():
            source_url = self.page.externalUrl(v) if v.startswith('/_vol') else v
            child = self.sourceDirNode.child(k)
            with child.open('wb') as f:
                f.write(urllib.urlopen(source_url).read())

    def step_buildHtmlDocs(self):
        "Build HTML docs"

        self.resultNode = self.sphinxNode.child('build')
        build_args = dict(project=self.handbook_record['title'],
                          version=self.handbook_record['version'],
                          author=self.handbook_record['author'],
                          release=self.handbook_record['release'],
                          lang=self.handbook_record['language'])
        args = []
        for k,v in build_args.items():
            if v:
                args.extend(['-D', '%s=%s' % (k,v)])
        self.page.site.shellCall('sphinx-build', self.sourceDirNode.internal_path , self.resultNode.internal_path, *args)


    def post_process(self):
        if self.batch_parameters['download_zip']:
            self.zipNode = self.handbookNode.child('%s.zip' % self.handbook_record['name'])
            self.page.site.zipFiles([self.resultNode.internal_path], self.zipNode.internal_path)
        
    def result_handler(self):
        r=dict()
        if self.batch_parameters['download_zip']:
            r=dict(url=self.zipNode.url())
        return 'Html Handbook created', r
        
    def prepare(self, data, pathlist):
        IMAGEFINDER = re.compile(r"\.\. image:: ([\w./]+)")
        LINKFINDER = re.compile(r" `([^`]*) <([\w./]+)>`_\b")

        result=[]
        for n in data:
            
            v = n.value
            record = self.doctable.record(n.label).output('dict')
            name=record['name']
            docbag = Bag(record['docbag'])
            toc_elements=[name]
            
            if n.attr['child_count']>0:
                result.append('%s/%s.rst' % (name,name))
                toc_elements=self.prepare(v, pathlist+toc_elements)
                self.curr_pathlist = pathlist+[name]
                tocstring = self.createToc(elements=toc_elements,
                            hidden=True,
                            titlesonly=True,
                            maxdepth=1)
            else:
                result.append(name)
                self.curr_pathlist=pathlist
                tocstring=''
            lbag=docbag[self.handbook_record['language']]
            rst = IMAGEFINDER.sub(self.fixImages, lbag['rst'])
            rst = LINKFINDER.sub(self.fixLinks, rst)

            
            tocstring = self.createToc(elements=toc_elements,
                            hidden=True,
                            titlesonly=True,
                            maxdepth=1)
                            
            self.createFile(pathlist=self.curr_pathlist, name=name,
                            title=lbag['title'], 
                            rst=rst,
                            tocstring=tocstring,
                            hname=record['hierarchical_name'])
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
        
    def createToc(self, elements=None, maxdepth=None, hidden=None, titlesonly=None, caption=None, includehidden=None):
        toc_options=[]
        if includehidden:
            toc_options.append('   :includehidden:')
        if maxdepth:
            toc_options.append('   :maxdepth: %i' % maxdepth)
        if hidden:
            toc_options.append('   :hidden:')
        if titlesonly:
            toc_options.append('   :titlesonly:')
        if caption:
            toc_options.append('   :caption: %s' % caption)

        return '\n%s\n%s\n\n\n   %s' % (".. toctree::", '\n'.join(toc_options),'\n   '.join(elements))


             
    def createFile(self, pathlist=None, name=None, title=None, rst=None, hname=None, tocstring=None, footer=''):
        reference_label='.. _%s:\n' % hname if hname else ''
        content = '\n'.join([reference_label, title, '='*len(title), tocstring, '\n\n', rst, footer])
        storageNode = self.page.site.storageNode('/'.join([self.sourceDirNode.internal_path]+pathlist))
        with storageNode.child('%s.rst' % name).open('wb') as f:
            f.write(content)


    def table_script_parameters_pane(self,pane,**kwargs):   
        fb = pane.formbuilder(cols=1, border_spacing='5px')
        fb.checkbox(lbl='Download Zip', value='^.download_zip')


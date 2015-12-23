#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from datetime import timedelta

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'

    @public_method
    def rst(self,*args,**kwargs):
        language = kwargs['selected_language'] if 'selected_language' in kwargs else self.locale.split('-')[0]
        language = language.lower()
        doctable = self.db.table('docu.documentation')
        pkey,docbag = doctable.readColumns(columns='$id,$docbag',
                                                    where='$hierarchical_name=:hname',
                                                    hname='/'.join(args))
        
        docbag = Bag(docbag)
        rst = docbag['%s.rst' %language] or docbag['en.rst'] or docbag['it.rst'] or 'To do...'
        rsttable = doctable.dfAsRstTable(pkey)
        if rsttable:
            rst = '%s\n\n%s' %(rst,rsttable) 
        js_script_url= self.site.getStaticUrl('rsrc:common','localiframe.js',nocache=True)

        return self.site.getService('rst2html')(rst,scripts=[js_script_url])

    @public_method
    def vtt(self,*args,**kwargs):
        callArgs = self.getCallArgs('handler','video_id','kind','language')
        language,ext = callArgs['language'].split('.')
        kind = callArgs['kind']
        tblobj = self.db.table('docu.video_track_cue')
        f = tblobj.query(where='$video_id=:vid AND $kind=:ki',
                            vid=callArgs['video_id'],ki=kind,order_by='start_time asc',
                            bagFields=True).fetch()
        result = ['WEBVTT FILE']
        for r in f:
            t0 = self.catalog.asText(timedelta(seconds=r['start_time']),)
            t1 = self.catalog.asText(timedelta(seconds=r['end_time']))
            subtitle = Bag(r['subtitles'])[language]
            result.append('\n%s\n%s --> %s\n%s' %(r['name'],t0,t1,subtitle))
        self.forced_mimetype = "text/vtt"
        return '\n'.join(result)




#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  jstools.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
import hashlib
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.web.jsmin import jsmin
import tempfile
import shutil

def compress_js(jsfiles, site=None):
    ts = str(max([os.path.getmtime(fname) for fname in jsfiles]))
    key = '-'.join(jsfiles)
    cpfile = '%s.js' % hashlib.md5(key + ts).hexdigest()
    jspath = site.getStatic('site').path('_static', '_jslib', cpfile)
    jsurl = site.getStatic('site').url('_static', '_jslib', cpfile)
    rebuild = True
    if os.path.isfile(jspath):
        #cpf = file(cppath, 'r')
        #tsf = cpf.readline()
        #cpf.close()
        #if ts in tsf:
        #    rebuild = False
        rebuild = False
    if rebuild:
        path = site.getStatic('site').path('_static', '_jslib')
        if not os.path.exists(path):
            os.makedirs(path)
        outfile_handle, outfile_path = tempfile.mkstemp(prefix='gnrcompress',suffix='.js')
        with os.fdopen(outfile_handle, "w") as cpf:
            cpf.write('// %s\n' % ts)
            for fname in jsfiles:
                f = file(fname)
                js = f.read()
                f.close()
                cpf.write(jsmin(js))
                cpf.write('\n\n\n\n')
            cpf.flush()
            os.fsync(cpf.fileno())
        shutil.move(outfile_path, jspath)
        
        
        
    return jsurl

class GnrWebJSTools(GnrBaseProxy):
    def init(self, **kwargs):
        pass

    def jsmin(self, js):
        return jsmin(js)

    def closurecompile(self, jsfiles):
        from subprocess import call

        ts = str(max([os.path.getmtime(fname) for fname in jsfiles]))
        key = '-'.join(jsfiles)
        cpfile = '%s-%s.js' % (hashlib.md5(key + ts).hexdigest(), ts)
        cppath = self.page.site.getStatic('site').path('_static', '_jslib', cpfile)
        jspath = self.page.site.getStatic('site').url('_static', '_jslib', cpfile)
        rebuild = True
        if os.path.isfile(cppath):
            rebuild = False
        if rebuild:
            path = self.page.site.getStatic('site').path('_static', '_jslib')
            if not os.path.exists(path):
                os.makedirs(path)
            call_params = ['java', '-jar', os.path.join(os.path.dirname(__file__), 'compiler.jar')]
            for path in jsfiles:
                call_params.append('--js=%s' % path)
            call_params.append('--js_output_file=%s' % cppath)
            call(call_params)
        return jspath

    def compress(self, jsfiles):
        return compress_js(jsfiles, site=self.page.site)
        

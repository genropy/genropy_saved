#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.

from __future__ import print_function
from past.builtins import basestring
import os
from gnr.web.gnrbaseclasses import BaseComponent

from gnrpkg.sys.services.ftp import SftpService,SftpDirectoryResolver
from gnr.core.gnrlang import GnrException


try:
    import pysftp
except:
    pysftp = False

class Service(SftpService):
    def __init__(self, parent=None,host=None,username=None,password=None,private_key=None,port=None,**kwargs):
        self.parent = parent
        if not pysftp:
            raise GnrException('Missing pysftp. hint: pip install pysftp')
        self.host = host
        self.username = username
        self.password = password
        self.private_key = private_key
        self.port = port

    def __call__(self,host=None,username=None,password=None,private_key=None,port=None):
        port = port or self.port
        username = username=username or self.username
        password = password or self.password
        private_key = private_key or self.private_key
        port = int(port) if port else None
        pars = {}
        if username:
            pars['username'] = username
        if password:
            pars['password'] = password
        if private_key:
            pars['private_key'] = private_key
        if port:
            pars['port'] = port
        return pysftp.Connection(host or self.host,**pars)

    def downloadFilesIntoFolder(self,sourcefiles=None,destfolder=None,
                                callback=None,preserve_mtime=None,thermo_wrapper=None,**kwargs):
        if isinstance(sourcefiles,basestring):
            sourcefiles = sourcefiles.split(',')
        if thermo_wrapper:
            sourcefiles = thermo_wrapper(thermo_wrapper)
        if callback is None:
            def cb(curr,total):
                print('dl %i/%i' %(curr,total))
            callback = cb
        with self(**kwargs) as sftp:
            for filepath in sourcefiles:
                basename = os.path.basename(filepath)
                getkw = {}
                if callback:
                    getkw['callback'] = callback
                if preserve_mtime:
                    getkw['preserve_mtime'] = preserve_mtime
                sftp.get(filepath,os.path.join(destfolder,basename),**getkw)

    def uploadFilesIntoFolder(self,sourcefiles=None,destfolder=None,
                                callback=None,preserve_mtime=None,
                                thermo_wrapper=None,confirm=None,**kwargs):
        if isinstance(sourcefiles,basestring):
            sourcefiles = sourcefiles.split(',')
        if thermo_wrapper:
            sourcefiles = thermo_wrapper(thermo_wrapper)
        if callback is None:
            def cb(curr,total):
                print('up %i/%i' %(curr,total))
            callback = cb
        with self(**kwargs) as sftp:
            for filepath in sourcefiles:
                basename = os.path.basename(filepath)
                putkw = {}
                if callback:
                    putkw['callback'] = callback
                if preserve_mtime:
                    putkw['preserve_mtime'] = preserve_mtime
                if confirm:
                    putkw['confirm'] = confirm
                sftp.put(filepath,os.path.join(destfolder,basename),**putkw)


class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.host',lbl='Host')
        fb.textbox(value='^.username',lbl='Username')
        fb.textbox(value='^.password',lbl='Password',type='password')
        fb.textbox(value='^.private_key',lbl='Private key')
        fb.textbox(value='^.port',lbl='Port')
# -*- coding: utf-8 -*-

# pysftp component
# Created by Francesco Porcari on 2017-12-18.
# Copyright (c) 2017 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class SftpClient(BaseComponent):
    py_requires='public:Public'

    @struct_method
    def sftp_sftpClientLayout(self,pane,ftpname=None,
                            datapath='.sftpclient',destdir=None,remotedir=None,**kwargs):
        bc = pane.borderContainer(datapath=datapath,_anchor=True,**kwargs)
        self.sftp_remoteTree(bc.roundedGroupFrame(region='left',title='!!Remote',
                            datapath='.remote',width='50%',
                            splitter=True),ftpname=ftpname,remotedir=remotedir)
        self.sftp_localTree(bc.roundedGroupFrame(region='center',title='!!Local',
                            datapath='.local'),ftpname=ftpname,destdir=destdir)

    def sftp_remoteTree(self,frame,ftpname=None,remotedir=None):
        resolver = self.getService('ftp',ftpname).sftpResolver()
        frame.data('.tree',resolver())
        self.sftp_fileTree(frame,nodeId='%s_src' %ftpname,topic='%s_upload' %ftpname)
        frame.dataRpc(None,self.sftp_uploadFiles,ftp=ftpname,
                    _onResult="""kwargs._dropnode.refresh(true);""",
                    **{'subscribe_%s_upload' %ftpname:True})

    def sftp_localTree(self,frame,ftpname=None,destdir=None):
        resolver= DirectoryResolver(destdir or self.site.getStatic('site').path())
        frame.data('.tree',resolver())
        self.sftp_fileTree(frame,nodeId='%s_dest' %ftpname,
                            topic='%s_download' %ftpname)
        frame.dataRpc(None,self.sftp_downloadFiles,ftp=ftpname,
                    _onResult="""kwargs._dropnode.refresh(true);""",
                        **{'subscribe_%s_download' %ftpname:True})


    def sftp_onDrag(self):
        return """var children=treeItem.getValue('static')
                  if(!children){
                      dragValues['fsource']=[treeItem.attr.abs_path];
                      return
                  }
                   result=[];
                   children.forEach(function(n){
                        if (n.attr.checked && !n._value){result.push(n.attr.abs_path);
                    }},'static');
                   dragValues['fsource']= result; 
               """

    @public_method
    def sftp_downloadFiles(self,sourcefiles=None,destfolder=None,ftp=None,**kwargs):
        self.getService('ftp',ftp).downloadFilesIntoFolder(sourcefiles=sourcefiles,
                                                destfolder=destfolder,**kwargs)

    @public_method
    def sftp_uploadFiles(self,sourcefiles=None,destfolder=None,ftp=None,**kwargs):
        self.getService('ftp',ftp).uploadFilesIntoFolder(sourcefiles=sourcefiles,
                                                destfolder=destfolder,**kwargs)


    def sftp_fileTree(self,pane,topic=None,**kwargs):
        tree = pane.treeGrid(storepath='.tree',hideValues=True, 
                      selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      checked_abs_path='.checked_abs_path',
                      #labelAttribute='nodecaption',
                       autoCollapse=True,
                      onDrag_fsource=self.sftp_onDrag(),
                      headers=True,draggable=True,dragClass='draggedItem',
                      onDrop_fsource="""
                         if(dropInfo.treeItem.attr.file_ext!='directory'){
                             return false;
                         }else{
                             genro.publish('%s',{
                                destfolder:dropInfo.treeItem.attr.abs_path,
                                _dropnode:dropInfo.treeItem,
                                sourcefiles:data});
                         }
                     """ %topic,dropTargetCb_fsource="""
                     if(dropInfo.selfdrop || dropInfo.treeItem.attr.file_ext!='directory'){
                         return false;
                     }
                     return true;
                     """,**kwargs)
        tree.column('nodecaption',header='!!Name')
        tree.column('file_ext',size=50,header='!!Ext')
        #tree.column('dtype',size=40,header='DT')
        tree.column('size',header='!!Size(KB)',size=60,dtype='L')
        tree.column('mtime',header='!!MTime',size=100,dtype='DH')
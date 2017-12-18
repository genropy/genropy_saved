# -*- coding: UTF-8 -*-
# 

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,services/ftp/pysftp/component:SftpClient"
    
    def test_1_ftplist(self, pane):
        pane.button('Run',fire='.run')
        pane.dataRpc('.result',self.ftplist,_fired='^.run')
        pane.div('^.result')

    
    def test_2_dirtree(self, pane):
        resolver = self.getService('ftp_genropy').sftpResolver()
        pane.data('.root.genropy',resolver())
        pane.tree(storepath='.root',hideValues=True, selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      checked_abs_path='.checked_abs_path',
                      labelAttribute='nodecaption', autoCollapse=True)
        

    def test_3_dl(self, pane):
        bc = pane.borderContainer(height='900px')
        resolver = self.getService('ftp_genropy').sftpResolver()
        left = bc.framePane(region='left',width='500px',datapath='.remote')
        left.data('.tree.root',resolver())
        tree = left.center.contentPane(overflow='auto').treeGrid(storepath='.tree',hideValues=True, selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      checked_abs_path='.checked_abs_path',
                      labelAttribute='nodecaption', autoCollapse=True,
                      onDrag_fsource=self.fsource_onDrag(),
                      headers=True,draggable=True,dragClass='draggedItem')
        tree.column('caption',header='Caption')
        tree.column('file_ext',size=50,header='Ext')
        #tree.column('dtype',size=40,header='DT')
        tree.column('size',header='Size(KB)',size=60,dtype='L')
        tree.column('mtime',header='MTime',size=100,dtype='DH')

        right = bc.framePane(region='right',width='300px',datapath='.local')
        resolver= DirectoryResolver(self.site.getStatic('site').path())
        right.data('.tree.root',resolver())
        right.center.contentPane(overflow='auto').tree(storepath='.tree',hideValues=True, 
                    selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      labelAttribute='nodecaption', autoCollapse=True,onDrop_fsource="""
                        if(dropInfo.treeItem.attr.file_ext!='directory'){
                            return false;
                        }else{
                            genro.publish('sftpdownload',{
                                destfolder:dropInfo.treeItem.attr.abs_path,
                                sourcefiles:data});
                        }
                    """,dropTargetCb_fsource="""
                    if(dropInfo.treeItem.attr.file_ext!='directory'){
                        return false;
                    }
                    return true;
                    """,
                    dropTarget=True)
        bc.dataRpc(None,self.downloadFiles,ftp='ftp_genropy',subscribe_sftpdownload=True)


    def fsource_onDrag(self):
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
    def downloadFiles(self,sourcefiles=None,destfolder=None,ftp=None,**kwargs):
        self.getService(ftp).downloadFilesIntoFolder(sourcefiles=sourcefiles,
                                                destfolder=destfolder,**kwargs)

    @public_method
    def uploadFiles(self,sourcefiles=None,destfolder=None,ftp=None,**kwargs):
        self.getService(ftp).uploadFilesIntoFolder(sourcefiles=sourcefiles,
                                                destfolder=destfolder,**kwargs)



    @public_method
    def ftplist(self):
        with self.getService('ftp_genropy')() as sftp:
            for attr in sftp.listdir_attr():
                b = Bag()
            return '<br/>'.join(sftp.listdir())


    def test_4_component(self, pane):
        pane.sftpClientLayout('ftp_genropy',height='600px',widht='900px')
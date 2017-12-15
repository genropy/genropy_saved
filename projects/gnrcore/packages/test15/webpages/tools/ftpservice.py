# -*- coding: UTF-8 -*-
# 

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
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
        bc = pane.borderContainer(height='600px')
        resolver = self.getService('ftp_genropy').sftpResolver()
        left = bc.framePane(region='left',width='300px',datapath='.remote')
        left.data('.tree.root',resolver())
        left.center.contentPane(overflow='auto').tree(storepath='.tree',hideValues=True, selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      checked_abs_path='.checked_abs_path',
                      labelAttribute='nodecaption', autoCollapse=True)
        right = bc.framePane(region='right',width='300px',datapath='.local')
        resolver= DirectoryResolver(self.site.getStatic('site').path(),include='directory')
        right.data('.tree.root',resolver())
        right.center.contentPane(overflow='auto').tree(storepath='.tree',hideValues=True, selectedLabelClass='selectedTreeNode',
                      selected_abs_path='.abs_path',selected_file_ext='.file_ext',
                      labelAttribute='nodecaption', autoCollapse=True)
        bar = right.bottom.slotToolbar('*,downloadbtn,5')
        bar.downloadbtn.slotButton('Download')

    @public_method
    def ftplist(self):
        with self.getService('ftp_genropy')() as sftp:
            for attr in sftp.listdir_attr():
                b = Bag()
            return '<br/>'.join(sftp.listdir())

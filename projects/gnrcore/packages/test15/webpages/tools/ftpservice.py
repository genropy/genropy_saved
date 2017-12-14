# -*- coding: UTF-8 -*-
# 

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

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
                      labelAttribute='nodecaption', autoCollapse=True)

    @public_method
    def ftplist(self):
        with self.getService('ftp_genropy')() as sftp:
            for attr in sftp.listdir_attr():
                b = Bag()
            return '<br/>'.join(sftp.listdir())

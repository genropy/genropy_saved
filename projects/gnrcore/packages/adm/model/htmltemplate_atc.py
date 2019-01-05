# encoding: utf-8

from gnr.app.gnrdbo import AttachmentTable

class Table(AttachmentTable):
    pass


    def use_dbstores(self,forced_dbstore=None, env_forced_dbstore=None,**kwargs):
        return True

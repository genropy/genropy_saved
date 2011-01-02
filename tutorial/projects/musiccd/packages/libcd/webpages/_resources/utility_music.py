from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag

class Common(BaseComponent):
    def rpc_save(self, data, table, **kwargs):
        tbl = self.db.table(table)
        if data['id']:
            tbl.update(data)
        else:
            tbl.insert(data)
        self.db.commit()
        return 'ok'

    def edit_record_dialog(self, root, title=None, height='400px', width='400px',
                           nodeId=None, datapath=None):
        dlg = root.dialog(title='Add Album', height='400px', width='400px', nodeId='album_dlg', datapath='album')
        dlg.dataController("genro.wdgById('album_dlg').show()", _fired="^.show")
        dlg.dataController("genro.wdgById('album_dlg').hide()", _fired="^.hide")
        return dlg

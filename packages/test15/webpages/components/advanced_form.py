#!/usr/bin/python

"""advanced form"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public'

    def main(self, rootBC, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(rootBC, title="!!Terapia", margin="1em", **kwargs)

        btPane = center.contentPane(region="bottom")
        buttons = btPane.div(width="100%")
        buttons.dbselect(value="^scheda.loadingPkey", dbtable="glbl.provincia")
        buttons.dataController(
                """genro.formById('miaForm').load({destPkey:newPkey,cancelCb:function(){genro.setData("scheda.loadingPkey",oldPkey)}})"""
                ,
                newPkey='^scheda.loadingPkey', oldPkey='=scheda.pkey',
                _if='newPkey!=oldPkey')
        buttons.button('Salva', float="right", action="genro.formById('miaForm').save(); ")

        cp = center.contentPane(region="center", formId="miaForm", datapath="scheda.dati", controllerPath="scheda.form",
                                pkeyPath="scheda.pkey")
        fb = cp.formbuilder(cols=2, border_spacing='4px', width="100%", fld_width="100%")
        fb.textbox(value="^.sigla", lbl="Sigla", validate_notnull=True)
        fb.textbox(value="^.nome", lbl="Nome", validate_notnull=True)

        cp.dataRpc('scheda.dati', 'caricaDati', nodeId="miaForm_loader", pkey="=scheda.pkey",
                   _onResult="genro.formById('miaForm').loaded()")
        cp.dataRpc('dummy', 'salvaDati', nodeId="miaForm_saver", dati="=scheda.dati",
                   _onResult="genro.formById('miaForm').saved(); genro.formById('miaForm').load();")

    def rpc_caricaDati(self, pkey, **kwargs):
        return self.db.table('glbl.provincia').recordAs(pkey, 'bag')

    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati

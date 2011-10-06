#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag

class ThermoUtils(BaseComponent):
    setThermo('pippo', 'fatture', progress_fatture=20, message='Stampo xxx')
    setThermo('pippo', progress_1=21, message_1='Pippo')

    def initThermo(self, name, lines='pippo,pluto,paperino', maximum_pippo=100, progress_pippo='+s', message_pippo='',
                   step_pippo=5):
        thermoBag = Bag()
        session.setInPageData('thermo.%s' % name, thermoBag)
        session.saveSessionData()

    setThermo(self, name, thermo_pippo=dict(progress_p=20, message='progresso'),
              thermo_pluto=dict(progress=20, message='progresso'))

    stepThermo('pippo', step_fatture='')
    stepThermo('pippo.fatture', message='')

    def setThermo(self, name, **kwargs):
        session = self.page.session
        session.loadSessionData()
        if command == 'init':
            thermoBag = Bag()
        else:
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoId) or Bag()

        max = maximum_1 or thermoBag['t1.maximum']
        prog = progress_1 or thermoBag['t1.maximum']
        if max and prog > max:
            end = True

        if command == 'end':
            thermoBag['status'] = 'end'
            thermoBag['message'] = '!!Execution completed'
        elif command == 'stopped':
            thermoBag['status'] = 'stopped'
            thermoBag['message'] = '!!Execution stopped'
        else:
            params = dict(progress_1=progress_1, message_1=message_1, maximum_1=maximum_1)
            params.update(kwargs)
            for k, v in params.items():
                if v is not None:
                    key, thermo = k.split('_')
                    thermoBag['t%s.%s' % (thermo, key)] = v

        session.setInPageData('thermo_%s' % thermoId, thermoBag)
        session.saveSessionData()
        if thermoBag['stop']:
            return 'stop'

    def rpc_getThermo(self, thermoId, flag=None):
        session = self.page.session
        if flag == 'stop':
            session.loadSessionData()
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoId) or Bag()
            thermoBag['stop'] = True
            session.setInPageData('thermo_%s' % thermoId, thermoBag)
            session.saveSessionData()
        else:
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoId) or Bag()
        return thermoBag

    def _make_dialog(self, name, title='', height='', width='', datapath='',
                     cb_center=None, cb_bottom=None, **kwargs):
        dialog = self.pageSource().dialog(title=title, nodeId=name, datapath=datapath, **kwargs)
        bc = dialog.borderContainer(height=height, width=width)
        if cb_bottom:
            cb_bottom(bc, region='bottom', _class='dialog_bottom')
        if cb_center:
            cb_center(bc, region='center', datapath='.data', _class='pbl_roundedGroup',
                      formId=formId, dlgId=dlgId)
        bc.dataController('genro.wdgById(dialogId).show();', dialogId=name, _fired="^.show")
        bc.dataController('genro.wdgById(dialogId).hide();', dialogId=name, _fired="^.hide")
        return bc

    def progressHandler(self, name, thermoPars=None, mode='dialog', title=''):
        #sync use dialog, async put the thermo inside a pane
        self.progressController()
        if mode == 'dialog':
            self._make_dialog('%s_dlg' % name, title=title, height='340px', width='340px',
                              cb_center=self.progressBarPane, cb_bottom=self.progressDialogBottom)
        else:
            pane = self.pageSource('pbl_bottomBarLeft')
            self.progressBarPane(pane)

    def progressDialogCenter(self, parent, thermoId='thermo', **kwargs):
        pane = parent.contentPane(**kwargs)
        self.progressBarPane(pane)

    def progressBarPane(self, pane):
        pass

    def progressDialogBottom(bc, **kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Cancel', baseClass='bottom_btn', float='left', margin='1px', fire='.hide')
        bottom.button('!!Confirm', baseClass='bottom_btn', float='right', margin='1px', fire_always='.save')


    def OLD_thermoDialog(self, pane, thermoId='thermo', title='', thermolines=1, fired=None, alertResult=False):
        dlgid = 'dlg_%s' % thermoId
        dlg = pane.dialog(nodeId=dlgid, title=title, datapath='_thermo.%s.result' % thermoId,
                          closable='ask', close_msg='!!Stop the batch execution?', close_confirm='Stop',
                          close_cancel='Continue',
                          close_action='FIRE ^_thermo.%s.flag = "stop"' % thermoId,
                          connect_show='this.intervalRef = setInterval(function(){genro.fireEvent("_thermo.%s.flag")}, 500)' % thermoId,
                          connect_hide='clearInterval(this.intervalRef);')
        #onAskCancel
        bc = dlg.borderContainer(width='330px', height='%ipx' % (100 + thermolines * 40))
        footer = bc.contentPane(region='bottom', _class='dialog_bottom')
        body = bc.contentPane(region='center')
        for x in range(thermolines):
            tl = body.div(datapath='.t%i' % (x + 1, ), border_bottom='1px solid gray', margin_bottom='3px')
            tl.div('^.message', height='1em', text_align='center')
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum',
                           places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')

        footer.button('Stop', baseClass='bottom_btn',
                      action='genro.wdgById("%s").onAskCancel();' % dlgid)
        pane.dataController('console.log("open thermo %s");genro.wdgById("%s").show()' % (dlgid, dlgid), fired=fired)
        pane.dataController('genro.wdgById(dlgid).hide();', dlgid=dlgid,
                            status='^_thermo.%s.result.status' % thermoId, _if='(status=="stopped" || status=="end")')
        if alertResult:
            pane.dataFormula('gnr.alert', 'msg', msg='=_thermo.%s.result.message' % thermoId,
                             status='^_thermo.%s.result.status' % thermoId, _if='(status=="stopped" || status=="end")')

        pane.dataRpc('_thermo.%s.result' % thermoId, 'app.getThermo', thermoId=thermoId,
                     flag='^_thermo.%s.flag' % thermoId)
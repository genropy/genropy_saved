from gnr.web.gnrbaseclasses import BaseComponent

class PluginOrganizer(BaseComponent):
    py_requires='th/th:TableHandler'
    css_requires = 'orgn_components'
    def btn_organizer(self,pane,**kwargs):
        pane.pluginButton('organizer',caption='!!Organizer',iconClass='alarm_check',defaultWidth='400px')

    def mainLeft_organizer(self, pane):
        """!!Organizer"""
        bc = pane.borderContainer(detachable=True)
      # top = bc.contentPane(region='top',height='100px',background='#666')
      # bottom = bc.contentPane(region='bottom',height='100px',background='#666')
        center = bc.contentPane(region='center')
        center.dialogTableHandler(table='orgn.annotation',
                                  formResource='ActionOutcomeForm',
                                  viewResource='ViewPlugin',
                                  liveUpdate=True,
                                  dialog_noModal=True,
                                  rowStatusColumn=False,
                                  condition='$plugin_assigment IS TRUE AND $done_ts IS NULL',
                                  view_store__onBuilt=True,
                                  configurable=False,
                                  _class='noheader orgn_action_grid')
#
from gnr.web.gnrbaseclasses import BaseComponent

class PluginOrganizer(BaseComponent):
    py_requires='th/th:TableHandler'
    def btn_organizer(self,pane,**kwargs):
        pane.pluginButton('organizer',caption='!!Organizer',iconClass='alarm_check',defaultWidth='500px')

    def mainLeft_organizer(self, pane):
        """!!Organizer"""
        pane = pane.contentPane(detachable=True,overflow='hidden')
        pane.plainTableHandler(table='orgn.annotation',condition='$plugin_assigment IS TRUE AND $done_ts IS NULL',viewResource='ViewPlugin',
                                view_store_onStart=True,configurable=False)

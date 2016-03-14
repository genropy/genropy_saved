from gnr.web.gnrbaseclasses import BaseComponent

class PluginOrganizer(BaseComponent):
    py_requires='th/th:TableHandler'
    def btn_organizer(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='alarm_check',tip='!!Organizer',
                 connect_onclick="""SET left.selected='organizer';genro.getFrameNode('standard_index').publish('showLeft');""",
                 nodeId='plugin_block_organizer')

    def mainLeft_organizer(self, pane):
        """!!Organizer"""
        pane = pane.contentPane(detachable=True,overflow='hidden')
        pane.plainTableHandler(table='orgn.action',condition='$assigned_to_me IS TRUE AND $done_ts IS NULL',viewResource='ViewPlugin',
                                view_store_onStart=True)

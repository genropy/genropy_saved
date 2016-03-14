from gnr.web.gnrbaseclasses import BaseComponent

class PluginOrgn(BaseComponent):
    py_requires='th/th:TableHandler'
    def btn_orgn(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='alarm_check',tip='!!Organizer',
                 connect_onclick="""SET left.selected='orgn';genro.getFrameNode('standard_index').publish('showLeft');""",
                 nodeId='plugin_block_orgn')

    def mainLeft_orgn(self, pane):
        """!!Organizer"""
        pane = pane.contentPane(detachable=True,overflow='hidden')
        pane.plainTableHandler(table='orgn.action',condition='$assigned_to_me IS TRUE AND $done_ts IS NULL',viewResource='ViewPlugin')

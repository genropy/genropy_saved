from gnr.web.gnrbaseclasses import BaseComponent

class PluginTodo(BaseComponent):
    py_requires='th/th:TableHandler'
    def btn_todo(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='alarm_check',tip='!![it]Todo notification',
                 connect_onclick="""SET left.selected='todo';genro.getFrameNode('standard_index').publish('showLeft');""",
                 nodeId='plugin_block_todo')

    def mainLeft_todo(self, pane):
        """!![it]Todo list"""
        pane = pane.contentPane(detachable=True,overflow='hidden')
        pane.plainTableHandler(table='todo.action',condition='$assigned_to_me IS TRUE AND $done_ts IS NULL',viewResource='ViewPlugin')

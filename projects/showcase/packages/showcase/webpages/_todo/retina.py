# -*- coding: UTF-8 -*-
"""Retina"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_icons = 'retina/gray'
    retina_values = ['add_record','add_row','alarm','alarm_check','alarm_off','alarm_on','app','app_globe',
                     'app_lock','app_remove','arrow','arrow_circle_left','arrow_circle_right','arrow_down',
                     'arrow_left','arrow_right','arrow_up','attach','auction','book','book_bookmark',
                     'bookmark','bookmark_add','brightness','brush','bulb_off','bulb_on','calculator',
                     'calendar','cancel','cart','case','chart_area','chart_bar','chart_bar1','chart_bar_down',
                     'chart_bar_up','chart_down','chart_line','chart_pie','chart_up','checkmark','clock',
                     'comment','comment_check','comment_delete','comment_minus','comment_plus','concole',
                     'contrast','copy','credit_card','cut','delete','delete_record','delete_row','disk',
                     'dismiss','display_off', 'display_on','document','document_empty','edit','export',
                     'favorites_add','favorites_remove','first','flag','flag1','flash','folder',
                     'folder_bookmark','folder_in','font','font_case','font_down','font_italic','font_p',
                     'font_underline','font_up','forward','frame','gear','globe','hat','heart','help',
                     'home','inbox','info', 'key','keyboard','laptop','last','link','list','lock',
                     'magnifier','mail','man','med','mic','minus','money','moving','next','note','on_off',
                     'outbox', 'paint','paper_plane','pencil','phone','photo','plus','previous','print',
                     'reload','resize','revert','rss','ruler','run','safe','save','shopping_bag','sitemap',
                     'smile','smile_sad','sound','spanner','speaker','star','stop','storage','sum','tag',
                     'tag_add','tag_cancel','tag_remove','trash', 'trash_mac','tray','tray_full','tray_mail',
                     'twg_logo','unlock','volume_down','volume_up','wallet','warning','warning1','wifi',
                     'zoom_in','zoom_out']
                     
    def test_1_retina(self, pane):
        """Retina icons"""
        #NISO: to fix!!
        #    1) the remote method musn't run on start
        #    2) find a way to handle the "css_icons"...
        bc = pane.borderContainer(height='445px')
        top = bc.contentPane(region='top', height='38px')
        fb = top.formbuilder(cols=2)
        fb.filteringSelect(value='^.filtering', height='18px',
                           values="""retina/blue:blue,retina/gray:gray,retina/green:green,
                                     retina/red:red,retina/violet:violet""")
        fb.slotButton('Reload', iconClass='iconbox reload', action='genro.pageReload();')
        center = bc.contentPane(region='center', border='3px solid gray', rounded=5)
        center.remote('buttons', filtering='^.filtering')
        
    def remote_buttons(self, center, filtering):
        css_icons = filtering
        fb = center.formbuilder(cols=2)
        for i in self.retina_values:
            fb.slotButton(i, iconClass='iconbox %s' %i, action='alert("iconbox %s")' %i)
            fb.div("iconClass=\'iconbox %s\'" %i)
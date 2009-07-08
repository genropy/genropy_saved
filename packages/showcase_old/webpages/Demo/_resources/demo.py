from gnr.web.gnrwebpage import BaseComponent

class Demo(BaseComponent):
    css_requires = 'demo,public,standard_tables/standard_tables'
    
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def addLocalizer(self, pane):
        lc = pane.layoutContainer(height='90%')
        pane = lc.contentPane(layoutAlign='bottom', height='30px', background_color='silver')
        pane.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass', float='left')
        pane.dataScript('gnr.localizerClass',"""return 'localizer_'+status""",status='^gnr.localizerStatus',_init=True,_else="return 'localizer_hidden'")
        return lc.contentPane(layoutAlign='client')
    
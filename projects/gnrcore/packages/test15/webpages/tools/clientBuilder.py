# -*- coding: UTF-8 -*-
class GnrCustomWebPage(object):
    def source_viewer_open(self):
        return 'close'

    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        frame = root.framePane(datapath='main')
        bar = frame.top.slotToolbar('10,run,*')
        bar.run.slotButton('Run',fire='.run')
        center = frame.center.borderContainer()
        left = center.contentPane(region='left',width='50%',splitter=True,border_right='1px solid silver')
        left.data('.jssource',"root._('div',{'innerHTML':'Hello world'})")
        left.codemirror(value='^.jssource',config_mode='javascript',
                                config_addon='search,lint',

                                  config_lineNumbers=True,height='100%')
        right = center.contentPane(region='center',datapath='.center')
        frame.dataController("""
                                right._('plainTableHandler',{'table':'glbl.provincia',py_requires:'th/th:TableHandler',datapath:'pippo'});
          
                                
                            """,_fired='^.run',jssource='=.jssource',right=right)
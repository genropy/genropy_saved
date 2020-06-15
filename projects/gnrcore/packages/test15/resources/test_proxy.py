from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import BaseComponent,page_proxy
#from gnrpkg.test15.proxies.bbt import TvSeries,BigBangProxy

@page_proxy
class BigBangProxy(BaseComponent):
    def fakeLaugh(self):
        print('AH AH AH')

@page_proxy
class Sheldon(BaseComponent):  
    py_requires = 'gnrcomponents/framegrid:FrameGrid' 

    def printBazinga(self):
        print('bazinga')

    @public_method
    def remoteBazinga(self):
        return 'bazinga'

    def bazingaBox(self,pane):
        p = self.trovaProvincia()
        pane.div('Bazinga {sigla}!!'.format(sigla=p['sigla']),font_size='42px',color='blu')
    
    def trovaProvincia(self):
        return  self.db.table('glbl.provincia').query(limit=1).fetch()[0]

@page_proxy(inherites='test_proxy:BigBangProxy')
class Leonard(BaseComponent):
    def makeBox(self,pane):
        pane.div('Hello everybody')

    @public_method
    def callPenny(self):
        print('penny,penny,penny')
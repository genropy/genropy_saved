from gnr.core.gnrdecorator import public_method
from gnrpkg.test15.proxies.bbt import TvSeries,BigBangProxy

class Sheldon(TvSeries,BigBangProxy):  
    py_requires = 'gnrcomponents/framegrid:FrameGrid' 
    proxy=True

    def printBazinga(self):
        print('bazinga')

    @public_method
    def remoteBazinga(self):
        print(x)
        return 'bazinga'

    def bazingaBox(self,pane):
        p = self.trovaProvincia()
        pane.div('Bazinga {sigla}!!'.format(sigla=p['sigla']),font_size='42px',color='blu')
    
    def trovaProvincia(self):
        return  self.db.table('glbl.provincia').query(limit=1).fetch()[0]


class Leonard(object):
    proxy= 'sheldon'

    @public_method
    def callPenny(self):
        print('penny,penny,penny')
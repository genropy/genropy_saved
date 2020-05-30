from gnr.core.gnrdecorator import public_method
from gnrpkg.test15.proxies.bbt import TvSeries,BigBangProxy

class Sheldon(TvSeries,BigBangProxy):   
    proxy=True
    def printBazinga(self):
        print('bazinga')

    @public_method
    def remoteBazinga(self):
        return 'bazinga'

class Leonard(object):
    proxy= 'sheldon'

    @public_method
    def callPenny(self):
        print('penny,penny,penny')
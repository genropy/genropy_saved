from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class Sheldon(BaseComponent):   
    proxy=True
    def printBazinga(self):
        print('bazinga')

    @public_method
    def remoteBazinga(self):
        return 'bazinga'
from gnrpkg.sys.services import SysServiceType
from gnr.services import GnrBaseService

class ServiceType(SysServiceType):
    pass

class TranslationService(GnrBaseService):
    def __init__(self, parent=None,api_key=None):
        self.parent = parent
        self.api_key = api_key
        
    @property
    def translator(self):
        pass

    @property
    def languages(self):
        pass

    def translate(self,what=None, to_language=None,from_language=None,format=None):
        pass
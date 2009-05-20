import os

#from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.app.gnrapp import GnrApp
#from gnr.core.gnrlang import gnrImport

class GnrWsgiWebApp(GnrApp):
    
    def __init__(self,*args,**kwargs):
        if 'site' in kwargs:
            self.site=kwargs.get('site')
            kwargs.pop('site')
        else:
            self.site=None
        super(GnrWsgiWebApp,self).__init__(*args,**kwargs)
    
    def onInited(self):
        pass

    def checkPagePermission(self, pagepath, tags):
        pagepath = pagepath.replace('.','_').replace('/','.')
        pageAuthTags = self.webpageIndex.getAttr('root.%s' % pagepath, 'pageAuthTags')
        return self.checkResourcePermission(pageAuthTags, tags)

    def _get_pagePackageId(self, filename):
        _packageId = None
        fpath, last = os.path.split(os.path.realpath(filename))
        while last and last!='webpages':
            fpath, last = os.path.split(fpath)
        if last=='webpages':
            _packageId = self.packagesIdByPath[fpath]
        if not _packageId:
            _packageId= self.config.getAttr('packages','default')
        return _packageId
    
    def newUserUrl(self):
        if self.config['authentication?canRegister']:
            authpkg = self.authPackage()
            if authpkg and hasattr(authpkg,'newUserUrl'):
                return authpkg.newUserUrl()
        
    def modifyUserUrl(self):
        authpkg = self.authPackage()
        if authpkg and hasattr(authpkg,'modifyUserUrl'):
            return authpkg.modifyUserUrl()
        
    def loginUrl(self):
        authpkg = self.authPackage()
        if authpkg and hasattr(authpkg,'loginUrl'):
            return authpkg.loginUrl()


            
    
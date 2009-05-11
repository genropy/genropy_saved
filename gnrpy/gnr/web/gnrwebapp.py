import os

#from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.app.gnrapp import GnrApp
#from gnr.core.gnrlang import gnrImport

class GnrWsgiWebApp(GnrApp):
    
    def onInited(self):
        pass
        #self.webpageIndex = Bag()
        #if 'pagesFolder' in self.kwargs:
        #    self.buildWebpageIndex(self.kwargs['pagesFolder'])
        
    #def buildWebpageIndex(self, path):
    #    self.webpageIndex['root'] = DirectoryResolver(path, cacheTime=600, 
    #                                                 callback=self.webpageAnalyze, 
    #                                                 include='*.py',
    #                                                 exclude='_*,.*')
    def checkPagePermission(self, pagepath, tags):
        pagepath = pagepath.replace('.','_').replace('/','.')
        pageAuthTags = self.webpageIndex.getAttr('root.%s' % pagepath, 'pageAuthTags')
        return self.checkResourcePermission(pageAuthTags, tags)

    #def webpageAnalyze(self, fullpath):
    #    result = {}
    #    if os.path.isfile(fullpath):
    #        pkgId =  self._get_pagePackageId(fullpath)
    #        if pkgId:
    #            result['packageId'] = pkgId
    #            result['pageAuthTags'] = self.db.package(pkgId).attributes.get('auth_tags','')
    #        try:
    #            m = gnrImport(fullpath)
    #            custompage = getattr(m,'GnrCustomWebPage', None)
    #            if custompage:
    #                custompage = custompage()
    #                if hasattr(custompage, 'pageAuthTags'):
    #                    result['pageAuthTags'] = self.addResourceTags(result.get('pageAuthTags'), custompage.pageAuthTags())
    #                result['__doc__'] = custompage.__doc__
    #                if hasattr(custompage, 'getPageinfo'):
    #                    result['info'] = custompage.getPageinfo()
    #        except:
    #            pass
    #    return result

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


            
    
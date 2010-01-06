import os

from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrApp
#from gnr.core.gnrlang import gnrImport

class GnrWsgiWebApp(GnrApp):
    
    def __init__(self,*args,**kwargs):
        if 'site' in kwargs:
            self.site=kwargs.get('site')
            kwargs.pop('site')
        else:
            self.site=None
        self._siteMenu = None
        super(GnrWsgiWebApp,self).__init__(*args,**kwargs)
    
    def notifyDbEvent(self,tblobj,record,event,old_record=None):
        self.site.notifyDbEvent(tblobj,record,event,old_record=old_record)
        
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
            
    def debugger(self,debugtype,**kwargs):
        self.site.debugger(debugtype,**kwargs)

    def _get_siteMenu(self):
        if not self._siteMenu:
            self._siteMenu = self._buildSiteMenu()
        return self._siteMenu
    siteMenu = property(_get_siteMenu)
    
    def _buildSiteMenu(self):
        menubag=None
        if 'adm' in self.db.packages:
            menubag=self.db.table('adm.menu').getMenuBag()
        if not menubag:
            menubag=self.config['menu']
        if not menubag:
            menubag=Bag()
            for pathlist,node in self.site.automap.getIndex():
                attr=dict(label=node.getAttr('name') or node.label.capitalize())
                if isinstance(node.getValue(),Bag):
                    attr['basepath']='/%s'% ('/'.join(pathlist))
                else:
                    attr['file']=node.label
                menubag.setItem(pathlist,None,attr)
        return menubag
        

            
    
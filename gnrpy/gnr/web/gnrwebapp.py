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
        menubag=self._buildSiteMenu_prepare(menubag)
        return menubag
        
    def _buildSiteMenu_prepare(self,menubag, basepath=None):
        basepath=basepath or []
        result=Bag()
        for node in menubag.nodes:
            value=node.getStaticValue()
            attributes={}
            attributes.update(node.getAttr())
            currbasepath=basepath
            if 'basepath' in attributes:
                newbasepath=attributes.pop('basepath')
                if newbasepath.startswith('/'):
                    currbasepath=[self.site.home_uri+newbasepath[1:]]
                else:
                    currbasepath=basepath+[newbasepath]
            if isinstance(value,Bag):
                value = self._buildSiteMenu_prepare(value,currbasepath)
            else:
                value=None
                filepath=attributes.get('file')
                if filepath: 
                    if not filepath.startswith('/'):
                        attributes['file'] = os.path.join(*(currbasepath+[filepath]))
                    else:
                        attributes['file'] = self.site.home_uri + filepath.lstrip('/')
            result.setItem(node.label,value,attributes)
        return result
        
    def setPreference(self, path, data, pkg):
        if self.db.package('adm'):
            self.db.table('adm.preference').setPreference(path,data,pkg=pkg)
            
    def getPreference(self, path, pkg, dflt=''):
        if self.db.package('adm'):
            return self.db.table('adm.preference').getPreference(path,pkg=pkg, dflt=dflt)
    
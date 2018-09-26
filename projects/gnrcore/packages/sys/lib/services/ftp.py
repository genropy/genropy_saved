import os
import datetime
from gnr.core import gnrstring
from gnr.core.gnrbag import Bag,DirectoryResolver,BagResolver

from gnrpkg.sys.services import SysServiceType,GnrBaseService


class ServiceType(SysServiceType):
    def test(self):
        print 'test'



class SftpService(GnrBaseService):
    def __init__(self, parent=None,host=None,username=None,password=None,private_key=None,port=None):
        pass

    def __call__(self,host=None,username=None,password=None,private_key=None,port=None):
        pass

    def downloadFilesIntoFolder(self,sourcefiles=None,destfolder=None,
                                callback=None,preserve_mtime=None,thermo_wrapper=None,**kwargs):
        pass

    def uploadFilesIntoFolder(self,sourcefiles=None,destfolder=None,
                                callback=None,preserve_mtime=None,
                                thermo_wrapper=None,confirm=None,**kwargs):
        pass

    def sftpResolver(self,path=None,**kwargs):
        return SftpDirectoryResolver(path,_page=self.parent.currentPage,
                                        ftpservice=self.service_name,
                                        **kwargs)
    
        

class SftpDirectoryResolver(DirectoryResolver):
    classKwargs = {'cacheTime': 500,
                   'readOnly': True,
                   'invisible': False,
                   'relocate': '',
                   'ext': 'xml',
                   'include': '',
                   'exclude': '',
                   'callback': None,
                   'dropext': False,
                   'processors': None,
                   'ftpservice':None,
                   '_page':None
    }
    classArgs = ['path', 'relocate']
    
    def resolverSerialize(self):
        self._initKwargs.pop('_page')
        return BagResolver.resolverSerialize(self)
        
    def load(self):
        """TODO"""
        extensions = dict([((ext.split(':') + (ext.split(':'))))[0:2] for ext in self.ext.split(',')]) if self.ext else dict()
        extensions['directory'] = 'directory'
        result = Bag()
        ftp = self._page.getService(self.ftpservice)()
        try:
            directory = sorted(ftp.listdir(self.path) if self.path else ftp.listdir())
        except OSError:
            directory = []
        if not self.invisible:
            directory = [x for x in directory if not x.startswith('.')]
        for fname in directory:
            nodecaption = fname
            fullpath = os.path.join(self.path, fname) if self.path else fname
            relpath = os.path.join(self.relocate, fname)
            addIt = True
            if ftp.isdir(fullpath):
                ext = 'directory'
                if self.exclude:
                    addIt = gnrstring.filter(fname, exclude=self.exclude, wildcard='*')
            else:
                if self.include or self.exclude:
                    addIt = gnrstring.filter(fname, include=self.include, exclude=self.exclude, wildcard='*')
                fname, ext = os.path.splitext(fname)
                ext = ext[1:]
            if addIt:
                label = self.makeLabel(fname, ext)
                handler = getattr(self, 'processor_%s' % extensions.get(ext.lower(), None), None)
                if not handler:
                    processors = self.processors or {}
                    handler = processors.get(ext.lower(), self.processor_default)
                try:
                    stat = ftp.stat(fullpath)
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    atime = datetime.fromtimestamp(stat.st_atime)
                    #ctime = datetime.fromtimestamp(stat.st_ctime)
                    size = stat.st_size
                except OSError:
                    mtime = None   
                    #ctime = None  
                    atime = None                   
                    size = None
                caption = fname.replace('_',' ').strip()
                m=re.match(r'(\d+) (.*)',caption)
                caption = '!!%s %s' % (str(int(m.group(1))),m.group(2).capitalize()) if m else caption.capitalize()
                nodeattr = dict(file_name=fname, file_ext=ext, rel_path=relpath,
                               abs_path=fullpath, mtime=mtime, atime=atime, #ctime=ctime,
                                nodecaption=nodecaption,
                               caption=caption,size=size)
                if self.callback:
                    self.callback(nodeattr=nodeattr)
                result.setItem(label, handler(fullpath),**nodeattr)
        ftp.close()
        return result

    def processor_directory(self, path):
        """TODO
        
        :param path: TODO"""
        return SftpDirectoryResolver(path,  os.path.basename(path), 
                                    **self.instanceKwargs)
        

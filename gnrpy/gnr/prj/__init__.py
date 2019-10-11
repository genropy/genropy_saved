#from builtins import object
import sys
import imp
import os
import pdb
from gnr.app.gnrdeploy import PathResolver, EntityNotFoundException


class GnrProjectMeta(object):
    
    prj_importers=dict()
    def __init__(self, *args):
        self.path_resolver = PathResolver()
        
    def find_module(self, fullname, path=None):
        if fullname.startswith('gnr.prj.'):
            splitted=fullname.split('.')
            
            
            project_name = splitted[2]
            return self._get_prj_importer(project_name)
 
    def _get_prj_importer(self, project_name):
        if project_name in self.prj_importers:
            return self.prj_importers[project_name]
        try:
            project_path = self.path_resolver.project_name_to_path(project_name)
        except EntityNotFoundException:
            project_path = None

        if not project_path:
            self.prj_importers[project_name] = None
            return
        self.prj_importers[project_name] = GnrPrjImporter(project_name, project_path)
        return self.prj_importers[project_name]
        
 

sys.meta_path = sys.meta_path+[GnrProjectMeta()]

class GnrPrjImporter(object):
    
    def __init__(self, project_name, project_path):
        self.project_name = project_name
        self.project_path = project_path
        self.module_path=os.path.join(project_path,'lib')
        self.pkg_name = 'gnr.prj.%s'%project_name
        self.register_new_module(self.pkg_name, self.module_path)
        packages_path = os.path.join(project_path,'packages')
        self.packages = dict([(p,os.path.join(packages_path,p,'lib')) for p in os.listdir(packages_path) if os.path.isdir(os.path.join(packages_path,p))])

    def load_module(self,fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        splitted = fullname.split('.')
        len_splitted = len(splitted)
        if len_splitted<4:
            return
        gnrpackage_name = splitted[3]
        if gnrpackage_name in self.packages:
            segmenti_iniziali = 4
        else:
            segmenti_iniziali = 3
            gnrpackage_name = None
        if len_splitted==segmenti_iniziali:
            if gnrpackage_name:
                return self.make_package(gnrpackage_name)
            else:
                return sys.modules[self.pkg_name]
        if len_splitted>segmenti_iniziali:
            parent_module_name = '.'.join(splitted[:-1])
            mod_fullname = '.'.join(splitted[-1:])
            return self.load_module_from_parent(fullname,mod_fullname, parent_module_name)
                
    def register_new_module(self, module_name, module_path):
        pkg_module=imp.new_module(module_name)
        sys.modules[module_name]=pkg_module
        pkg_module.__file__ = None
        pkg_module.__name__ = module_name
        pkg_module.__path__ = [module_path]
        pkg_module.__package__ = module_name

    def make_package(self, gnrpackage_name):
        pkg_name = '%s.%s'%(self.pkg_name,gnrpackage_name)
        gnrpackage_path = self.packages[gnrpackage_name]
        if not gnrpackage_path:
            return
        self.register_new_module(pkg_name, gnrpackage_path)
        return sys.modules[pkg_name]

    def load_module_from_parent(self, fullname, mod_fullname, parent_module_name):
        parent_module = sys.modules[parent_module_name]
        if not parent_module:
            return
        mod = None
        try:
            mod_file,mod_pathname,mod_description=imp.find_module(mod_fullname, parent_module.__path__)
        except ImportError:
            return
        try:
            mod = imp.load_module(fullname,mod_file, mod_pathname, mod_description)
            sys.modules[fullname]=mod
        finally:
            if mod_file:
                mod_file.close()
        return mod


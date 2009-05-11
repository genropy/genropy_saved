from distutils.core import setup

import os

def isToImport(fname):
    name, ext = os.path.splitext(fname)
    if name.startswith('.'):
        return False
    if ext not in ('.pyc',):
        return True
        
def getAllFiles(path, installPath):
    data_files = []
    for dirpath, dirnames, filenames in os.walk(path):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): del dirnames[i]
        data_files.append([os.path.join(installPath, dirpath.replace(path,'')), [os.path.join(dirpath, f) for f in filenames if isToImport(f)]])
    return data_files

data_files = []
data_files.extend(getAllFiles('gnrjs/','/usr/local/genro/lib/gnrjs/'))
data_files.extend(getAllFiles('gnrpy/packages/','/usr/local/genro/packages/'))
data_files.extend(getAllFiles('bin/','/usr/local/genro/bin/'))
data_files.append(['/usr/local/genro/data/sites',['README.txt']])
data_files.append(['/usr/local/genro/data/instances',['README.txt']])

setup(name='gnrFramework',
    version='0.1',
    author='Giovanni Porcari, Francesco Cavazzana, Saverio Porcari, Francesco Porcari',
    url='http://www.genropy.org/',
    author_email='info@genropy.org',
    license='LGPL',
    packages=['gnr', 'gnr.core', 'gnr.app','gnr.web', 'gnr.sql'],
    package_dir={'gnr': 'gnrpy/gnr'},
    data_files=data_files
    
    )
    


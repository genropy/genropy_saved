# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrsys : a connection to the os.
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA



"""
sys
"""
import os

def mkdir(path, privileges=0777):
    if path and not os.path.isdir(path):
        head, tail = os.path.split(path)
        mkdir(head, privileges)
        os.mkdir(path, privileges)
        
def expandpath(path):
    return os.path.expanduser(os.path.expandvars(path))
    
def listdirs(path, invisible_files=False):
    """returns a list of all files contained in path and its descendant"""
    def callb(files,top,names):
        for name in names:
            file_path = os.path.realpath(os.path.join(top,name))
            if (invisible_files or not name.startswith('.')) and os.path.isfile(file_path):
                files.append(file_path)
    files=[]
    os.path.walk(path,callb,files)
    return files

def resolvegenropypath(path):
    """resolvegenropypath(path)
       To make it easier to resolve document paths between different installations 
       of genropy where sometimes it is installed in the user path and sometimes 
       at root, ie. /genropy/... or ~/genropy/., so that file path given within 
       genropy will be resolve to be valid if possibe and we do not have to edit 
       for example our import files . 
       Of course I expect it to be rejected and / or refactored"""
       
    if path.find('~') == 0:
        path = expandpath(path)
        if os.path.exists(path):
            return path

    if path.find('/') == 0:
        if os.path.exists(path):
            return path
        else: #try making it into a user directory path
            path = '%s%s' %('~', path)
            path = expandpath(path)
            if os.path.exists(path):
                return path
    else:
        if os.path.exists(path):
            return path
        else:
            path = '%s%s' %('~/', path)
            path = expandpath(path)
            if os.path.exists(path):
                return path

if __name__ == '__main__':
    print resolvegenropypath('~/genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')
    print resolvegenropypath('/genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')
    print resolvegenropypath('genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')
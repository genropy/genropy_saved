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
        
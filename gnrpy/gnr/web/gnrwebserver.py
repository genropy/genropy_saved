#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os
import sys
from gnr.core.gnrsys import expandpath

def getSiteHandler(site_name, gnr_config=None):
    gnr_config = or getGnrConfig()
    path_list = []
    gnrenv = gnr_config['gnr.environment_xml']
    sites = gnr_config['gnr.environment_xml.sites']
    projects = gnr_config['gnr.environment_xml.projects']
    if sites:
        sites = sites.digest('#a.path,#a.site_template')
        path_list.extend([(expandpath(path), site_template) for path, site_template in sites 
                                                            if os.path.isdir(expandpath(path))])
    if projects:
        projects.digest('#a.path,#a.site_template') 
        projects = [(expandpath(path), template) for path, template in projects
                                                 if os.path.isdir(expandpath(path))]
        for project_path, site_template in projects:
            sites = glob.glob(os.path.join(project_path, '*/sites'))
            path_list.extend([(site_path, site_template) for site_path in sites])
    for path, site_template in path_list:
        site_path = os.path.join(path, site_name)
        if os.path.isdir(site_path):
            site_script = os.path.join(self.site_path, 'root.py')
            if not os.path.isfile(site_script):
                site_script = None
            return dict(site_path=site_path,
                            site_template=site_template,
                            site_script = site_script)

def getGnrConfig(config_path=None):
    config = Bag()
    config_path = config_path or '~/.gnr' if sys.platform != 'win32' else '~\gnr'
    config_path = expandpath(config_path)
    if os.path.isdir(config_path):
        config = Bag(config_path)
    return config



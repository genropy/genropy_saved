# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
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

from builtins import object
class AppPref(object):
    def permission_orgn(self, **kwargs):
        return 'admin'

    def prefpane_orgn(self, parent, **kwargs):
        pane = parent.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.checkbox(value='^.organizer_enabled',label='!!Organizer enabled')
        fb.textbox(value='^.orgn_superuser_tag',lbl='!!Superuser tag',attr_dbenv=True)
        fb.checkbox(value='^.orgn_author_only',label='!!Upd author only',attr_dbenv=True)
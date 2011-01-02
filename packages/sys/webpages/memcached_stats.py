# -*- coding: UTF-8 -*-
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


from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def windowTitle(self):
        return 'user'

    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootContentPane(root, title='!!Mem Stats')
        center.dataRpc('root', 'getStats', _timing=45, _init=True)
        center.tree(storepath='root')

    def rpc_getStats(self):
        result = Bag()
        stats = self.site.shared_data.storage.get_stats()
        result['stats'] = Bag(stats[0][1])
        return result
#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package            : GenroPy web - see LICENSE for details
# module gnrhtmlpage : Genro Web structures implementation
# Copyright (c)      : 2004 - 2009 Softwell sas - Milano 
# Written by         : Giovanni Porcari, Michele Bertoldi
#                      Saverio Porcari, Francesco Porcari
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

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
        
class GnrHeadlessPage(GnrWebPage):
    
    def rootPage(self, *args, **kwargs):
        kwargs = kwargs or {}
        args = args or tuple()
        return Bag({'page_id':self.page_id,
                 'connection_id':self.connection_id,
                 'user':self.user}).toXml()
                 
    def rpc_handle_anwsers(self, answers=None):
        answers=Bag(answers or '')
        for page_id,page_answers in answers.items():
            with self.clientPage(page_id) as clientPage:
                for value,changepath in page_answers.digest('#v,#a.client_path'):
                    clientPage.set(changepath,value)
                    print 'HEY SETTO IN CLIENTPAGE'
    
    
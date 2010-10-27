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



class GnrCustomWebPage(object):
    def windowTitle(self):
         return 'test remote'
         
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region = 'top',height='100px')
        top.button('Build',fire='build')

        top.button('Add element',fire='add')
        top.dataController("""var pane = genro.nodeById('remoteContent')
                              pane._('div',{height:'200px',width:'200px',background:'lightBlue',
                                            border:'1px solid blue','float':'left',
                                            remote:{'method':'test'}});

                            """,_fired="^add")
                            
        center = bc.contentPane(region = 'center').div(nodeId='remoteContent')
        center.div().remote('test',_fired='^build')
        
    def remote_test(self,pane,**kwargs):
        print 'pippo'
        pane.div('hello',height='40px',width='80px',background='lime')
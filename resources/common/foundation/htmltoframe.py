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

"""
Component for recordtohtmlframe:
"""
from gnr.web.gnrbaseclasses import BaseComponent

class RecordToHtmlFrame(BaseComponent):
    def _custom_print_toolbar(self, toolbar):
        pass

    def recordToHtmlFrame(self, bc, frameId='', table='', delay=None,
                          respath=None, pkeyPath='', background_color='white',
                          enableConditionPath='', condition_function=None, condition_value='',
                          docNamePath='', runKwargsPath=None, customToolbarCb=None, rebuild=True,
                          reloadOnPath=None, **kwargs):
        table = table or self.maintable
        frameId = frameId or self.getUuid()
        runKwargs = None
        enableCondition = None

        if runKwargsPath:
            runKwargs = '=%s' % runKwargsPath

        controllerPath = 'aux_frames.%s' % frameId
        top = bc.contentPane(region='top', height='32px')
        toolbar = top.toolbar(height='23px', margin_top='2px')
        custom_toolbarCb = customToolbarCb or getattr(self, '_custom_print_toolbar')
        custom_toolbarCb(toolbar)
        toolbar.button('!!PDF', fire='%s.downloadPdf' % controllerPath, iconClass='icnBasePdf',
                       position='absolute', right='10px', top='5px', showLabel=False, )
        toolbar.button('!!Print', fire='%s.print' % controllerPath, showLabel=False,
                       position='absolute', right='40px', top='5px', iconClass='icnBasePrinter')

        #top.checkbox("Don't cache", value='%s.noCache' % controllerPath,)

        top.dataController("""
                             var runKwargs=runKwargs || {};
                             var docName = docName || record;
                             var docName=docName.replace('.', '');
                             var downloadAs =docName +'.pdf';
                             var parameters = {'record':record,
                                               'table':'%s',
                                               'downloadAs':downloadAs,
                                               'pdf':true,
                                               'respath':'%s',
                                               'rebuild':rebuild,
                                               'print_button':false,
                                               runKwargs:runKwargs}
                             objectUpdate(parameters,moreargs);
                             console.log(parameters);
                             genro.rpcDownload("callTableScript",parameters);
                             """ % (table, respath),
                           _fired='^%s.downloadPdf' % controllerPath,
                           record='=%s' % pkeyPath,
                           runKwargs=runKwargs, #aggiunto
                           docName='=%s' % docNamePath,
                           moreargs=kwargs,
                           rebuild=rebuild)
        #rebuild='=%s.noCache' % controllerPath)
        rpc_args = {}
        for k, v in kwargs.items():
            rpc_args['rpc_%s' % k] = v

        center = bc.stackContainer(region='center', background_color=background_color,
                                   selected='^%s.selectedPane' % controllerPath)
        emptyPane = center.contentPane()
        loadingPane = center.contentPane(_class='waiting')
        iframePane = center.contentPane(overflow='hidden')

        if enableConditionPath:
            enableCondition = '=%s' % enableConditionPath
            center.dataController("FIRE %s.load;" % controllerPath, _fired='^%s' % enableConditionPath)
        center.dataController("FIRE %s.load;" % controllerPath,
                              _fired='^%s' % pkeyPath,
                              _aux_fired='^%s' % reloadOnPath or pkeyPath)
        frame = iframePane.iframe(nodeId=frameId,
                                  border='0px',
                                  height='100%',
                                  width='100%',
                                  delay=delay,
                                  condition_function=condition_function,
                                  condition_value=condition_value,
                                  rpcCall='callTableScript',
                                  rpc_record='=%s' % pkeyPath,
                                  rpc_print_button=False,
                                  rpc_runKwargs=runKwargs, #aggiunto
                                  rpc_table=table,
                                  rpc_respath=respath,
                                  #rpc_rebuild='=%s.noCache' % controllerPath,
                                  onUpdating='genro.setData("%s.selectedPane", 1);' % controllerPath,
                                  onLoad='genro.setData("%s.selectedPane", 2);' % controllerPath,
                                  rpc_rebuild=rebuild,
                                  _print='^%s.print' % controllerPath,
                                  _reloader='^%s.load' % controllerPath,
                                  _if=enableCondition,
                                  **rpc_args)
# -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.


from builtins import object
class GnrCustomWebPage(object):
    py_requires = 'services/ftp/pysftp/component:SftpClient'
    auth_main='admin'

    #FOR ALTERNATE MAIN HOOKS LOOK AT public:TableHandlerMain component
    def main(self,root,**kwargs):
        callArgs = self.getCallArgs('ftpname')  
        if callArgs['ftpname']:
            root.sftpClientLayout(callArgs['ftpname'],datapath='main')
        else:
            bc = root.borderContainer()
            top = bc.contentPane(region='top',datapath='pars')
            fb = top.formbuilder()
            fb.dbselect(value='^.service',dbtable='sys.service',condition='$service_type=:f',
                        condition_f='ftp',lbl='Ftp',hasDownArrow=True,
                        selected_service_name='.service_name')
            fb.dataFormula('.url',"`/sys/ftpservice/${service_name}`",
                            service_name='^.service_name')
            center = bc.contentPane(region='center')
            center.iframe(src='^pars.url',height='100%',width='100%',border=0)
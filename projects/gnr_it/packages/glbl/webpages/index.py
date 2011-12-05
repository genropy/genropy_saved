# -*- coding: UTF-8 -*-

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    user_polling = 0
    auto_polling = 0
    py_requires="""th/th:TableHandler"""
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
    
    def windowTitle(self):
         return '!!Glbl'

    def main(self, root, **kwargs):
        bc = root.borderContainer()
        self.top(bc.borderContainer(datapath='glbl',region='top',height='50%'))
        self.center(bc.borderContainer(datapath='glbl.localita',region='center',height='50%'))

    def top(self,bc):
        th1 = bc.contentPane(region='left',width='50%').dialogTableHandler(table='glbl.provincia',
                                    dialog_height='280px',rounded=8,border='1px solid gray',margin='2px',
                                    dialog_width='540px',
                                    dialog_title=u'!!Provincia',lockable=True)
        th1.view.store.attributes.update(_onStart=True)
        th2 = bc.contentPane(region='center',width='50%').dialogTableHandler(table='glbl.regione',
                                    dialog_height='280px',rounded=8,border='1px solid gray',margin='2px',
                                    dialog_width='540px',
                                    dialog_title=u'!!Regione',lockable=True)
        th2.view.store.attributes.update(_onStart=True)

    def center(self,bc):
        th1 = bc.contentPane(region='center').dialogTableHandler(table='glbl.localita',
                                    dialog_height='280px',rounded=8,border='1px solid gray',margin='2px',
                                    dialog_width='540px',
                                    dialog_title=u'!!Località',lockable=True)
        th1.view.store.attributes.update(_onStart=False)

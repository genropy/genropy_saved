# -*- coding: utf-8 -*-


from gnr.core.gnrdecorator import public_method
from time import sleep

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull"""

    def test_1_long_thermo(self,pane):
        pane.numberTextBox(value='^.numero',lbl='Numero')
        pane.numberTextBox(value='^.pausa',lbl='Pausa')

        pane.button('Procedi',fire='.procedi')
        pane.dataRpc(None,self.rpcConTermometro,
                    _fired='^.procedi',
                    numero='=.numero',
                    pausa='=.pausa',
                    _lockScreen=dict(thermo=True))

    def test_2_long_thermo_province(self,pane):
        pane.dbSelect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        pane.button('Procedi',fire='.procedi')
        pane.dataRpc(None,self.rpcProvince,
                    _fired='^.procedi',
                    regione='=.regione',
                    _lockScreen=dict(thermo=True))


    @public_method
    def rpcConTermometro(self,numero=None,pausa=None):
        numero = numero or 20
        pausa = pausa or .5
        lista= ['Numero {i}'.format(i=i) for i in range(numero)]
        for elem in self.utils.quickThermo(lista,labelfield='prova'):
            self.log(elem)
            sleep(pausa)

    @public_method
    def rpcProvince(self,regione=None):
        province = self.db.table('glbl.provincia').query(
            where='$regione=:reg',reg=regione
        ).fetch()
        for provincia in self.utils.quickThermo(province,labelfield='nome'):
            print(provincia)
            sleep(1)


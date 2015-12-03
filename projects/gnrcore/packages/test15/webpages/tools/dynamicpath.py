# -*- coding: UTF-8 -*-

# iframerunner.py
# Created by Francesco Porcari on 2011-04-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"iframerunner"

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    
    def xxxtest_1_firsttest(self,pane):
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.filteringSelect(value='^.var_x',values='alfa,beta,gamma')
        fb.filteringSelect(value='^.var_y',values='foo,bar,spam')

        center = bc.contentPane(region='center')
        center.data('.var_x','alfa')
        center.data('.var_y','foo')

        center.data('.data.alfa.foo',Bag(dict(nome='Piero',cognome='Rossi')))
        center.data('.data.alfa.bar.nome',Bag(dict(nome='Antonio',cognome='Barbera')))
        center.data('.data.beta.foo.nome',Bag(dict(nome='Camilla',cognome='Iseri')))
        center.data('.data.beta.bar.nome',Bag(dict(nome='Roberta',cognome='Piedipiatti')))

        fb2 = center.formbuilder(cols=1,border_spacing='3px',datapath='.data')
        fb2.textbox(value='^.(var_x).(var_y).nome',lbl='Nome')
        fb2.textbox(value='^.(var_x).(var_y).cognome',lbl='Cognome')

    def mygrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('codice', name='Codice', width='10em',edit=True)
        r.cell('descrizione', name='Descrizione', width='30em',edit=True)

    def test_2_tagliacolore(self,pane):
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px',nodeId='aaa')
        fb.filteringSelect(value='^.selectedLabel',values='CO:Colore,TG:Taglia,MS:Misura scarpa')

        #fb.div(nodeId='pippo',)
        fb.data('data',self.testBag())
        center = bc.contentPane(region='center')
        center.bagGrid(storepath='==_selectedLabel?"data."+_selectedLabel:".emptystore"',
                            grid__selectedLabel='^#aaa.selectedLabel',
                            datapath='mygrid',struct=self.mygrid_struct)
        #fb.dataController("""var p = selectedLabel? "data."+selectedLabel:"fakepath";
        #                    SET foo = p;""",
        #                    selectedLabel='^.selectedLabel',grid=f.grid.js_widget)
    def testBag(self):
        return Bag(
        """<?xml version="1.0" encoding="utf-8"?>
<GenRoBag>
<CO descrizione="Colore" _loadedValue="::NN">
<n_1007 _pkey="n_1007">
<codice>RO</codice>
<descrizione>Rosso</descrizione>
</n_1007>
<n_1023 __old="::NN" _pkey="n_1023">
<codice dtype="::NN">AR</codice>
<descrizione dtype="::NN">Arancione</descrizione>
</n_1023>
<n_1015 _pkey="n_1015">
<codice>VE</codice>
<descrizione>Verde</descrizione>
</n_1015>
</CO>
<TG descrizione="Taglia" _loadedValue="::NN">
<n_1025 _pkey="n_1025">
<codice>M</codice>
<descrizione>Medio</descrizione>
</n_1025>
<n_1033 _pkey="n_1033">
<codice>S</codice>
<descrizione>Piccolo</descrizione>
</n_1033>
<n_1041 _pkey="n_1041">
<codice>X</codice>
<descrizione>Grande</descrizione>
</n_1041>
<n_1049 _pkey="n_1049">
<codice>XL</codice>
<descrizione>Molto grande</descrizione>
</n_1049>
</TG>
<MS descrizione="Misura scarpa" _loadedValue="::NN">
<n_1012 __old="::NN" _pkey="n_1012">
<codice dtype="::NN">01</codice>
<descrizione dtype="::NN">36</descrizione>
</n_1012>
<n_1020 __old="::NN" _pkey="n_1020">
<codice dtype="::NN">02</codice>
<descrizione dtype="::NN">37</descrizione>
</n_1020>
<n_1028 __old="::NN" _pkey="n_1028">
<codice dtype="::NN">03</codice>
<descrizione dtype="::NN">38</descrizione>
</n_1028>
<n_1036 __old="::NN" _pkey="n_1036">
<codice dtype="::NN">04</codice>
<descrizione dtype="::NN">39</descrizione>
</n_1036>
<n_1044 __old="::NN" _pkey="n_1044">
<codice dtype="::NN">05</codice>
<descrizione dtype="::NN">40</descrizione>
</n_1044>
<n_1052 __old="::NN" _pkey="n_1052">
<codice dtype="::NN">06</codice>
<descrizione dtype="::NN">41</descrizione>
</n_1052>
<n_1060 __old="::NN" _pkey="n_1060">
<codice dtype="::NN">07</codice>
<descrizione dtype="::NN">42</descrizione>
</n_1060>
</MS>
</GenRoBag>""")

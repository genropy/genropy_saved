
############ CODICE ORIGINALE (NON FUNZIONANTE) #################

#class GnrCustomWebPage(object):
#    def main(self, root, **kwargs):
#        r=tbl.tr()
#        r.td('Year')
#        r.td().numberSpinner(value='^.year')
#        r.td('fieldspinner')
#        r.td().field('showcase.cast.person_id',tag='numberSpinner')
#        
#        cp = root.contentPane(margin='1em',padding='10px')
#        fb=cp.formBuilder(datapath='myform')
#        fb.div('fields')
#        fb.field('showcase.cast.person_id',lbl='Year',width='15em',zoom=False,tag='numberSpinner')


############ MIO TENTATIVO (NON FUNZIONANTE) #################

#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        cp = root.contentPane(margin='1em',padding='10px')
        fb=cp.formBuilder(datapath='myform',cols=2)
        fb.numberSpinner(value='^value')
        fbb = fb.div('fieldspinner')
        fbb.field('showcase.cast.person_id',lbl='Year',width='15em',zoom=False,tag='numberSpinner')
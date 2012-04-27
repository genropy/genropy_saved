# -*- coding: UTF-8 -*-

"""Radio Button Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height=200,description='Combobox filled through "values" attribute')
    def combobox1(self, pane):
        pane.combobox(value='^.record.values', values='Football,Golf,Karate',
                      lbl='loaded through values')
                      
    def doc_combobox1(self,pane):
        """A combo box presents a menu of items loaded from the values attribute either by a comma seperated list
or from a bag storepath.  A combobox allows the operator to select either one of the menu items or type in a value.
"""

    @example(code=1,height=450,description='Combobox filled through a Bag')
    def combobox2(self, pane):
        from gnr.core.gnrbag import Bag
        def sports():
            mytable = Bag()
            mytable['r1.pkey'] = 'SC'
            mytable['r1.Description'] = 'Soccer'
            mytable['r2.pkey'] = 'BK'
            mytable['r2.Description'] = 'Basket'
            mytable['r3.pkey'] = 'TE'
            mytable['r3.Description'] = 'Tennis'
            mytable['r4.pkey'] = 'HK'
            mytable['r4.Description'] = 'Hockey'
            mytable['r5.pkey'] = 'BB'
            mytable['r5.Description'] = 'Baseball'
            mytable['r6.pkey'] = 'SB'
            mytable['r6.Description'] = 'Snowboard'
            return mytable
        pane.data('.values.sport', sports(), id='.pkey', caption='.Description')
        pane.combobox(value='^.record', storepath='.values.sport')

    def doc_combobox2():
        """kjhkjh"""

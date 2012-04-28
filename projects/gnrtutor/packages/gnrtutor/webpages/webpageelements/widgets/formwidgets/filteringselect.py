# -*- coding: UTF-8 -*-

"""Filtering Select"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"
    
    @example(code=1,height=200,description='Filtering Select values loaded from values attribute')
    def filteringselectvalues(self, pane):
        fb = pane.formbuilder(cols=2, margin='5px')
        fb.filteringSelect(value='^.sport',
                           values="SC:Soccer,BK:Basket,HK:Hockey,TE:Tennis,BB:Baseball,SB:Snowboard",lbl="Sports")
        fb.div("Values loaded through the 'values' attribute")
        

    def doc_filteringselectvalues(self):
        """The filtering select can be populated from values directly assigned to the values attribute in the form of
a specially formatted string. \"pkey1:value1,pkey2:value2\"

When a menu item is selected the pkey is placed as the data at the path specified by the value parameter.

Note the observer (^) at path .sport so that any change in this path by any other method or widget will fire the filteringSelect widget.
"""


    @example(code=2,height=450,description='Filtering Select values loaded from a bag')
    def filteringselectbag(self, pane):
        from gnr.core.gnrbag import Bag
        def sports():
            mytable = Bag()
            mytable['r1.pkey'] = 'SC'
            mytable['r1.description'] = 'Soccer'
            mytable['r2.pkey'] = 'BK'
            mytable['r2.description'] = 'Basket'
            mytable['r3.pkey'] = 'TE'
            mytable['r3.description'] = 'Tennis'
            mytable['r4.pkey'] = 'HK'
            mytable['r4.description'] = 'Hockey'
            mytable['r5.pkey'] = 'BB'
            mytable['r5.description'] = 'Baseball'
            mytable['r6.pkey'] = 'SB'
            mytable['r6.description'] = 'Snowboard'
            return mytable

        fb = pane.formbuilder(cols=2)
        pane.data('.bag', sports(), id='.pkey', caption='.description')
        fb.filteringSelect(value='^.value_bag', storepath='.bag',lbl="Sports")
        fb.div('Values loaded through a Bag')


    def doc_filteringselectbag(self):
        """The filtering select can be populated from values assigned from a bag.
The Bag class must be imported from: gnr.core.gnrbag import Bag.

The 'data', data controller loads the bag into the datastore at path '.bag'.  This path can then be used as the storepath parameter.

When a menu item is selected the code (pkey) is placed as the data at the path specified by the value parameter.
Note the observer (^) at path .sport so that any change in this path by any other method or widget will fire the filteringSelect widget.
"""

    
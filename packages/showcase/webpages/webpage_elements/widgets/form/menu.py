#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('values.states', self.tableData_states())
        root.data('records', self.myRecords())
        root.data('values.sex', self.tableData_sex())
        fb = root.formbuilder(cols='4', datapath='records', background_color='silver', margin='30px')
        for r in range(4):
            self.makeRow(fb, r)

        self.pageCtrlMenu(fb.dropdownbutton('pagemenu'))
        self.dropDownContent(fb.dropdownbutton('Open me'))
        self.connectionDialog(fb.dropdownbutton('Connection mode'))
        self.saveDialog(root, 'savedlg')
        fb.button('Save as...', action='genro.savedlg.show()')

    def makeRow(self, fb, r):
        name = fb.textBox(value='^.r%i.name' % r, lbl='Name')
        age = fb.numberSpinner(value='^.r%i.age' % r, lbl='Age')
        sex = fb.filteringSelect(value='^.r%i.sex' % r, storepath='values.sex', lbl='Sex')
        state = fb.filteringSelect(value='^.r%i.state' % r, storepath='values.states', lbl='State')

    def pageCtrlMenu(self, dropdownbutton):
        menu = dropdownbutton.menu()
        menu.menuline('Open...', gnrIcon='Save', action="alert('Opening now...')")
        menu.menuline('Close...', action="alert('Closing now')")
        menu.menuline('-')
        submenu = menu.menuline('Print to').menu()
        submenu.menuline('Laser first floor', background_color='green', action="alert('Printing on the laser')")
        submenu.menuline('Ink Jet', color='red', action="alert('Wasting ink...')")

    def dropDownContent(self, dropdownbutton):
        menu = dropdownbutton.menu(action="function(menuline){alert('Selected: '+menuline.label)}")
        menu.menuline('Do This')
        menu.menuline('Do That')
        submenu = menu.menuline('Print to').menu()
        submenu.menuline('Printer')
        submenu.menuline('Fax')
        submenu.menuline('-')
        submenu.menuline('File')
        menu.menuline('-')
        menu.menuline('Do nothing', disabled=True)

    def connectionDialog(self, dropdownbutton):
        tooltip = dropdownbutton.tooltipDialog(datapath='connection').formbuilder(cols='2', background_color='yellow')
        tooltip.textbox(value='^.url', lbl_color='red', lbl='Url')
        tooltip.textbox(value='^.user', lbl='User')
        tooltip.numberTextBox(value='^.mintime', lbl='Min time')
        tooltip.numberTextBox(value='^.maxtime', lbl='Max time')

    def saveDialog(self, root, gnrId):
        dlg = root.dialog(title='Save', datapath='saving', gnrId=gnrId).formbuilder(cols='2')
        dlg.textbox(value='^.filename', lbl='Filename')
        dlg.checkbox(value='^.docopy', label='Make a copy')
        dlg.button(action='genro.%s.hide()' % gnrId, label='Ok')

    ############################# filling Bag methods ####################################################

    def tableData_states(self):
        mytable = Bag()
        mytable.setItem('r1', None, id='CA', caption='California')
        mytable.setItem('r2', None, id='IL', caption='Illinois')
        mytable.setItem('r3', None, id='NY', caption='New York')
        mytable.setItem('r4', None, id='TX', caption='Texas')
        mytable.setItem('r5', None, id='AL', caption='Alabama')
        return mytable

    def myRecords(self):
        data = Bag()
        data['r0.name'] = 'John'
        data['r0.age'] = 26
        data['r0.sex'] = 'M'
        data['r0.state'] = 'TX'
        data['r1.name'] = 'Mary'
        data['r1.age'] = 31
        data['r1.sex'] = 'F'
        data['r1.state'] = 'CA'
        return data

    def tableData_sex(self):
        mytable = Bag()
        mytable.setItem('r1', None, id='M', caption='Male')
        mytable.setItem('r2', None, id='F', caption='Female')
        return mytable
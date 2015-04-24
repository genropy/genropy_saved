#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    root.thpage(u"!!Company", table="uke.company")
    root.thpage(u"!!Customer", table="uke.customer")
    root.thpage(u"!!Help", table="uke.help")
    root.thpage(u"!!Localization", table="uke.localization")
    root.thpage(u"!!Package", table="uke.package")
    root.thpage(u"!!People", table="uke.person")
    root.thpage(u"!!Project", table="uke.project")
    root.thpage(u"!!Ticket", table="uke.ticket")
    root.thpage(u"!!Ticket type", table="uke.ticket_type")

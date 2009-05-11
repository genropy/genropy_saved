""" GnrDojo Examples & Tutorials """

#from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
import os

# ----- GnrWebPage subclass -----

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        lc = root.layoutContainer(height='97%',margin='10px')
        lc.contentPane(_class='demoTitlePane',layoutAlign='top').div("Genro Demo Zone")
        client = lc.contentPane(_class='demoClientPane',layoutAlign='client')
        tbl=client.table(border="0", _class='demoindex', height='100%',width='100%')
        tbl=tbl.tbody()
        r1=tbl.tr()
        r1.td(u'!!Genro vs The Form',connect_onclick="genro.gotoURL('login.py')")
        r1.td(u'!!Genro vs The Datastore',connect_onclick="genro.gotoURL('nuovo_utente.py')")
        r2=tbl.tr()
        r2.td(u'!!Genro vs The Layout',connect_onclick="genro.gotoURL('nuovo_utente.py')")
        r2.td(u'!!Genro vs The Demo',connect_onclick="genro.gotoURL('demo/pagebrowser.py')")
        
#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

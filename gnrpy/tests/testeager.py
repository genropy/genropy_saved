from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace


app = GnrApp('icond')
db = app.db
prov = db.table('studio.pr_evento')
evento = prov.record(pkey='htM4Cp15N46VwDFyRDYHuw').output('bag')
tplbag = Bag('/Users/fporcari/sviluppo/softwell/progetti/icond/packages/studio/resources/tables/pr_evento/tpl/cruscotto.xml')
result = templateReplace(tplbag.getItem('compiled'),evento, safeMode=True,noneIsBlank=False,locale='IT-it')
print result

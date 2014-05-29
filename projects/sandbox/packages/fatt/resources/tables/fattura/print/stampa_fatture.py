from gnr.web.batch.btcprint import BaseResourcePrint

caption = 'Stampa Fatture'
tags = 'user'
description='Stampa fatture selezionate'

class Main(BaseResourcePrint):
    batch_prefix = 'ft'
    batch_prefix = 'st_fatt'
    batch_title = 'Stampa fattura'
    batch_immediate = 'print'
    batch_delay = 0.5
    html_res = 'html_res/fattura_stampa'
    templates = 'cartafattura'
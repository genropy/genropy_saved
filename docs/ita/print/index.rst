**TODO:** questa pagina è da riscrivere e riorganizzare.

################
Stampe e Reports
################

In GenroPy, le stampe sono gestite come *resource script* delle tabelle. In questo modo possono essere facilmente personalizzate per ogni installazione.

Per costruire una stampa o un report, si crea una classe derivata da :class:`gnr.web.gnrtablescript.RecordToHtmlNew`. Esempio::

	from gnr.web.gnrtablescript import RecordToHtmlNew 

	class Main(RecordToHtmlNew):
	    maintable = 'package.tabella'
	    page_header_height = 0
	    page_footer_height = 0 
	    doc_header_height = 10
	    doc_footer_height = 10
	    grid_header_height = 6.2
	    grid_footer_height = 0 
	    row_mode='attribute'
	    grid_col_widths=[15,12,0,0,15,17,12,12]
	    grid_col_headers = 'Data,Ora,Medico,Prestazione,Conv.,Fattura,Importo,Costo'
	    grid_row_height=10
	    rows_path = 'rows'

Questi parametri possono essere specificati come attributi della classe (scritti usando *underline_come_separatore*) o come metodi della classe (scritti in *camelCase*), nel caso fossero calcolati dinamicamente.

Layout, righe e celle
*********************

Per posizionare le cose, abbiamo a disposizione tre oggetti:

	* **layout**. Possono contenere soltanto righe.
	* **row**. Possono contenere soltanto celle. Le righe hanno l'altezza, se non viene specificata (o se è zero) la riga è elastica.
	* **celle**. Possono contenere layout. Le celle hanno la larghezza. Due celle attaccate autocollassano i bordi (rimane un bordo solo).
	
Le lunghezze sono sempre specificate in millimetri (mm). Vedi :mod:`gnr.core.gnrhtml` per ulteriori dettagli.

Attributi e callbacks
*********************

Il foglio è diviso in varie parti che hanno corrispondenti callbacks:

(attributo, callback)

attributo page_header, callback pageHeader -- header della pagina (es. per carta intestata)
page_footer, callback pageFooter -- footer della pagina (es. per carta intestata)
callback docHeader -- intestazione del documento
callback docFooter -- footer del documento
callback prepareRow -- chiamato per ogni riga del corpo

Il ``pageHeader``/``pageFooter`` è solitamente riservato alla carta intestata o al template, ``docHeader``/``docFooter`` viene usato per la testata/footer. Ad esempio, in una stampa fattura, l'intestazione va nel ``docHeader`` mentre le righe nel corpo.

``prepareRow`` viene chiamata in automatico per ogni riga. Ha una sintassi tipo field.

Il componente prende i dati da una tabella, ma se invece si vogliono passare dati con altro sistema si può ridefinire il metodo ``loadRecord``. 

Invocazione della stampa
************************

La stampa può essere invocata in vari modi: si può mettere un bottone in una standardtable (c'è un callback apposta), stampa tutte le righe selezionate. Il componente ``serverPrint()`` mostra una finestra di dialogo per la stampa (in cui è possibile aggiungere ulteriori parametri, con un callback) e poi prepara il batch di stampa.

Esempio::

    def bottomPane_stampaPrestazioni(self,pane):
        pane.button(fire="#stampaprestazione.open",label='!!Stampa prestazioni')
        self.serverPrint(pane,name='stampaprestazione',table_resource='html_res/medico_prestazioni',
                        parameters_cb=self.cb_period,docName='prestazioni_medici',thermoParams=True)
*************************
 Appunti vari su GenroPy
*************************

Costruzione delle bags
======================

Esistono vari modi per costruire bags in GenRo:

* da un file XML;
* utilizzando le istruzioni python del modulo ``gnr.core.gnrbag``, in questo caso il codice è simile alla costruzione di un dizionario;
* utilizzando il modulo ``gnr.core.gnrstructures``, in questo caso il codice è costituito da una serie di chiamate di metodi python. Il codice per la costruzione dei modelli di database e delle webpages costruisce in realtà delle bags, appoggiandosi a questo modulo.


Mappatura da modelli a struttura del database
=============================================

In GenroPy, il passaggio dalle classi di modello al database avviene in questo modo:

1. Il codice nei files in ``<nome package>/models/<nome modello>.py``, in realtà costruisce una Structure di GenRo (cioé una Bag costruita con codice Python).
2. La bag così costruita viene tradotta in oggetti Python.
3. Genro confronta questi oggetti con la struttura del database ed apporta gli eventuali aggiornamenti

Il programma ``gnrdbsetup`` viene usato per questo scopo.

Siti, Istanze, packages e componenti
====================================

Le applicazioni GenroPy sono suddivise in vari strati, che consentono la personalizzazione (garantendo un facile aggiornamento anche in presenza di customizzazioni) e il riuso di codice e risorse fra vari progetti.

Un progetto GenroPy è costituito da:


il sito:
	si occupa di tutto ciò che riguarda la configurazione dell'applicazione per una particolare installazione **Web**. Include cioé i componenti e le configurazioni necessari all'esecuzione via Web. In genere, contiene la configurazione WSGI e lo script ``root.py`` (quest'ultimo viene usato anche come eseguibile se si vuole usare un debugger, come WingIDE).

l'istanza:
	contiene le personalizzazioni per il particolare cliente. In genere contiene i parametri di accesso al database. Dispone di una sottocartella ``data`` che si può usare per memorizzare dati nel filesystem. Quando si lavora con l'interprete python o con strumenti a linea di comando, in genere si lavora a livello d'istanza::
	
		#!python
		from gnr.app.gnrapp import GnrApp
		istanza = GnrApp('elezioni')

	Giovanni ha accennato al concetto di sottoistanza, utilizato per modificare la configurazione di un'applicazione a runtime (ad esempio, per poter accedere a dati storici ormai eliminati dal database corrente dell'istanza principale).

i packages:
	sono i vari moduli che compongono il codice applicativo di Genro, compreso il package principale che costituisce l'applicazione sviluppata. Genro fornisce moduli aggiuntivi che implementano funzioni comuni a tutte le applicazioni (gestione utenti, tabella dei comuni italiani, etc.). E' dentro al package dell'applicazione (o dei packages accessori) che si concentra la maggior parte del codice Python (a parte quello del core del framework che è nel package python ``gnr`` e nei suoi figli).
	
	Il package ``glbl`` contiene già una tabella delle località e comuni italiani. (**TODO**: chiedere a Giovanni i dati della tabella, perché non mi sembra siano presenti in SVN).

	**Nota**: i packages di Genro non sono packages Python (=insieme di moduli collegati, contenente un file ``__init__.py``), perché non si possono importare con l'istruzione ``import <modulo>`` o ``from <package> import <modulo o classe>``.

i componenti e le risorse:
	sono elementi comuni e riusabili. Comprendono sia il codice Javascript e CSS che quello Python (es. ``includedView``, tabelle standard). E' inserito nela sottocartella ``webpages/_resources`` di packages, istanze (e -credo- siti). Viene usato nelle webpages attraverso ``py_requires``, ``css_requires`` e ``js_requires``. Il codice in ``gnr.web.gnrwsgisite`` si occupa di fare il mixin delle risorse.

	
Mixin delle classi a runtime
****************************

GenroPy costruisce le classi dell'applicazione facendo *mixin* delle classi a runtime. I metodi e le risorse (CSS, JS, ma anche componenti Python) vengono aggregati a runtime secondo regole precise che consentono di personalizzare il funzionamento per la singola installazione e di mantenere queste customizzazioni, con il minimo impatto, anche per i futuri aggiornamenti.

La costruzione avviene all'avvio dell'applicazione wsgi (e non per ogni richiesta).

E' possibile fare mixin sia per l'interfaccia (webpages, componenti, CSS, JS, etc.) che per la struttura del database (models).

**TODO:** Si veda sul wiki del sito http://projects.softwell.it/ alla pagina *Customization* per una spiegazione delle regole di mixin e personalizzazione degli applicativi.

Funzionamento web di GenroPy
============================

Nella costruzione delle pagine, GenroPy prima di tutto fa caricare al browser la sua componente javascript. Una volta caricato il motore JS, viene inviata al client la descrizione della pagina e del contenuto iniziale del datastore sotto forma di bags. A questo punto, il codice JS può fare chiamate al codice python.

In pratica, GenroPy si comporta in questo modo:

1. Il client fa la richiesta HTTP per la pagina ``foo``::

	client ----------- HTTP ----------> server (wsgisite)

2. GenroPy manda una pagina standard vuota, contenente in pratica solo il motore ``gnrjs``::

	client <----- motore javascript --- server (wsgisite)

3. Il motore javascript chiede al server il contenuto della pagina, lato Python viene chiamata la funzione ``main`` della ``WebPage``::

    motore js ------- ready -----------> server (pagina ``main.py``)

4. Il server invia una descrizione del contenuto della pagina di alto livello, in termini di widgets e contenuto del datastore, sotto forma di bags::

    pagina js <------ bags ------------- pagina python

5. Da qui in poi, la comunicazione procede principalmente facendo aggiornamenti al datastore (o all'interfaccia utente) utilizzando le funzioni di rpc::

    pagina js <- dataRpc() o remote() -> pagina python

WSGI
====

WSGI è lo standard per interfacciare frameworks Web Python con i webserver. Consente anche di comporre vari componenti web fra loro, attraverso un sistema di middlewares (concetto simile, ma non compatibile, con gli analoghi componenti in Django). Sul sito WSGI_ sono presenti link a moltissime utili risorse (frameworks, middlewares, servers).

.. _WSGI: http://wsgi.org/wsgi

Un'applicazione WSGI definisce una funzione che accetta la richiesta web e restituisce la risposta. Un middleware WSGI è semplicemente un'applicazione che ne richiama un'altra, come nel pattern Decorator_.
Lo standard WSGI definisce un formato standard per la richiesta (che può essere decorata con altre informazioni durante l'elaborazione nei vari middlewares) e per la risposta (che può anche essere asincrona).

.. _Decorator: http://en.wikipedia.org/wiki/Decorator_pattern

GenroPy utilizza il middleware Beaker_ per la gestione delle sessioni e weberror per la gestione dei traceback (compresa l'utilissima capacità di aprire un interprete python nel punto dove si verifica l'errore). GenroPy utilizza Paste_ e WebOb_ durante lo sviluppo con server standalone (credo che la funzione weberror sia fornita da Paste).

.. _Beaker: http://beaker.groovie.org/
.. _Paste: http://pythonpaste.org/
.. _WebOb: http://pythonpaste.org/webob/reference.html

Per un esempio di middleware, vedi ``gnrpy/gnr/web/gzipmiddleware.py`` (lo script non funziona attualmente in genro, ma per altri motivi secondo Michele Bertoldi che se ne sta occupando). Il file ``root.py`` all'interno dei siti Genro è un'applicazione WSGI.

Apache e WSGI
*************

Per utilizzare WSGI con apache, è necessario installare il modulo ``mod_wsgi`` e configurarlo::

	<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www
	WSGIDaemonProcess gnr user=genro group=genro python-eggs=/tmp threads=25
	SetEnv PROCESS_GROUP gnr
	WSGIProcessGroup %{ENV:PROCESS_GROUP}
	# modify the following line to point your site
	WSGIScriptAlias / /home/genro/progetti/mmusic/sites/provarci/root.py
	#WSGIRestrictProcess gnr
	<Directory /home/genro/progetti/mmusic/sites/provarci>
	Options Indexes FollowSymLinks
	AllowOverride All
	Order allow,deny
	Allow from all
	</Directory>
	</VirtualHost>

Tipo di dati aggiuntivi, non presenti nel bundle TextMate
=========================================================

Tipo ``DH``:
	TimeStamp

GnrApp
======

Il codice per creare un'istanza è::

	#!python
	from gnr.app.gnrapp import GnrApp
	istanza = GnrApp('elezioni')

1. ``GnrApp.__init__`` carica la configurazione dell'istanza da ``instanceconfig.xml``.
2. ``GnrApp.init`` esegue:
	* l'hook ``onIniting``
	* crea gli oggetti package necessari
	* l'hook ``onInited``

GnrPackage
==========

Nel file ``main.py`` di un package, si definiscono le classi ``Package`` e ``Table``. I metodi di queste classi sono rispettivamente disponibili alle pagine web come ``self.package.<nome metodo>`` e come ``self.db.table('nome tabella').<nome metodo>``.

Pagine
======

Gli oggetti pagina posso accedere ai vari componenti di un'applicazione Genro usando variabili d'istanza:

* ``self.package``
* ``self.db``
* ``self.application`` (es. ``self.application.config``)
* ``self.site`` (es. ``self.site.config``)

Oggetti Tabella
===============

Gli oggetti tabella sono accessibili dalle pagine con ``self.db.table('ppackage.tabella')``. Il metodo ``query`` degli oggetti tabella restituisce un oggetto di ricerca nel db configurato secondo i parametri specificati, ma non esegue la query sul db. Su questo oggetto ricerca, possono essere usati il metodo ``selection`` per avere i risultati in vari formati oppure il metodo ``fetch`` per ottenerli semplicemente (come lista/dizionari/iteratore/bag? boh, **TODO:** controllare).

Esempio::

	#!python
	
	db = ...
	tbl = db.table('comuni')
	qry = tbl.query(...)
	sel = qry.selection()
	
	# modifica in memoria dei record, anche aggiungendo nuovi campi (es. per i campi calcolati da mandare al client)
	sel.apply(lambda r: dict(area=r.base*r.altezza))
	
	sel.output(formato)

Le selezioni supportano vari formati:

bag:
	Bag di Genro (vedi ``gnr.core.gnrbag``)

json:
	Serializzazione in formato JSON

*altro*:
	per gli altri formati, guardare i metodi con prefisso ``out_`` degli oggetti selection

Le selezioni hanno metodi per fare totali o analisi statistiche (medie, somme, etc.) aggregate per vari campi, vedere i metodi ``analyze`` e ``totalize``.

**NOTA**: le selezioni sono implementate a livello di bags (e non di database), quindi possono essere utilizzate anche con sorgenti dati diverse dai db.

Vedi anche ``gnr.gnrsql.gnrsqldata`` per info su selection/query/record.

Tools utili
===========

BonjourFoxy:
	plugin di Firefox per vedere i siti web registrati nella rete locale con Bonjour (utile nella fase di sviluppo)

Navicat:
	editor di database con buon supporto per Postgres


pycallgraph
===========

Utilizza il profiler di python e mostra le chiamate come grafico utilizzando graphviz. Per installarlo, usare ``easy_install`` o ``pip``::

	easy_install pycallgraph

Bags
====

Le bag di GenroPy sono molto potenti e sono pervasive nel design del framework. (Questa è una gran cosa, ma può avere risvolti negativi dal punto di vista della sicurezza).

Al costruttore delle bags, si possono passare:

* un dizionario
* una lista chiave/valore
* un'altra bag
* il nome di un file xml
* il nome di una directory, in questo caso si può percorrere l'albero ed anche leggere il contenuto dei files XML (come se facessero parte dello stesso albero)

La potenza delle bags risiede nei resolvers, che lavorano come i mount points di un filesystem. Sono la promessa di restituire una bag. I resolver possono fare cache della bag restituita oppure fornire nuovi dati ad ogni chiamata.

Video interessante sul design dei frameworks web in Python
==========================================================

Djangocon 2008, `Building a better framework`_

.. _Building a better framework: http://www.youtube.com/watch?v=fipFKyW2FA4&feature=related

DOJO
====

La documentazione di DOJO è disponibile come applicazione AIR (cercare *DOJO Toolbox*), ma non è particolarmente aggiornata. In ogni caso, Genro utilizza la versione 1.1 di Dojo (mentre ora siamo alla 1.4).

Il datastore e il codice Javascript di Genro
============================================

Attraverso vari comandi python, si può collegare il codice javascript agli eventi dei componenti d'interfaccia oppure agli eventi generati dal datastore.

Il datastore è una bag di genro.

Sintassi per i datapath
***********************

I path nel datastore seguono la sintassi:

* ``path.assoluto.nel.datastore``
* ``.path.relativo.nel.datastore``
* ``#ID.path.relativo.da.un.ID``

E' possibile indicare di recuperare i dati dal datastore praticamente in ogni elemento dell'interfaccia (viene implementato nella lettura della Bag dell'interfaccia, e quindi comprende moltissime cose: ad esempio, è possibile anche specificare le classi CSS di un elemento HTML legandole ad un elemento del datastore), usando i prefissi:

* "tegolino" (accento circonflesso): ``^accesso.con.resolver``, imposta una sorta di observer. Il componente verrà informato delle modifiche al datastore.
* uguale: ``=accesso.senza.resolver``, legge il contenuto del datastore.

Accesso al datastore da Javascript
**********************************

Le operazioni possibili sul datastore sono:

**SET**:
	imposta un valore e scatena gli eventi associati (cioé eventuali osservatori o resolver collegati tramite "^")
**PUT**:
	imposta un valore, ma NON scatenare gli eventi associati
**GET**:
	legge il contenuto di un valore nel datastore.
**FIRE**:
	imposta un valore nel datastore, scatena gli eventi associati e poi reimposta il valore a nullo (senza scatenare eventi). Viene usato quando interessa più di tutti lo scatenare eventi passando un dato temporaneo agli observers.

Queste operazioni possono essere specificate nel codice javascript degli eventi associati all'interfaccia, il framework gnrjs si occupa di fare l'espansione di queste macro. E' possibile accedere al datastore dal propri codice javascript (i.e. da codice scritto in file .JS e quindi letto senza l'espansione delle macro) utilizzando semplici funzioni javascript.

Componenti utili (definiti come risorse)
========================================

includedViewBox:
	lista di record, utile per implementare viste master/detail

recordDialog:
	finestra popup di modifica di un singolo record. Di solito, utilizzata per la modifica dei record della includedViewBox.

Studiare questi due componenti per maggiori informazioni su come definire componenti complessi tramite le risorse.

Idea per un tool utile allo sviluppo in Genro
=============================================

Estratte relazioni (leggendo gli observers) fra l'interfaccia ed il datastore e mostrarle in forma grafica con graphviz.

Politica opensource della Softwell
==================================

* La shell (packages in ``gnr.*``) rimarrà sempre opensource.
* In futuro, Softwell potrebbe decidere di continuare lo sviluppo delle risorse (``_resources``) come software chiuso.

Sicurezza nei files PDF
=======================

Per leggere dati in locale o i parametri dell'URL, potrebbe essere necessario un certificato al fine di evitare il security alert (ma forse utilizzandolo da browser e caricando il PDF dal server, questo non è necessario).

Testgarden
==========

Il progetto testgarden contiene demo per tutti gli widgets inclusi in genro. Può essere usato per le prove e per verificare di non rompere nulla.

**NOTA**: tuttavia non mi sembra che sia mantenuto attivamente e credo che sia già mezzo rotto allo stato attuale.

DOJO
====

Genro utilizza Dojo_ versione 1.1, per la documentazione vedere anche il `Dojo Campus`_.

.. _Dojo: http://www.dojotoolkit.org/
.. _Dojo Campus: http://dojocampus.org/

In Dojo, gli widget possono essere di due tipi: Container, ContentPanes.

* I Container possono contenere altri Containers o ContentPanes.
* I ContentPanes possono contenere widgets o elementi HTML.

In pratica, seguono il pattern *Composite*.

Nelle versioni precedenti di Dojo, nel ``borderContainer`` era necessario specificare per ultimo l'oggetto inserito al centro. E' buona norma farlo anche ora, seppur non necessario, perché così si velocizza il caricamento della pagina (non si può calcolare l'occupazione dell'elemento centrale senza aver prima caricato e calcolato quella degli elementi ai bordi).

Risorsa ``public``
==================

La risorsa ``public`` implementa gli elementi base dell'interfaccia in Genro.

Fornisce anche le classi CSS:

pbl_RoundedGroup:
	utilizzata per dividere la pagina in due gruppi logicamente separati.

pbl_RoundedGroupLabel:
	lavora con il precedente, per dare un titolo al gruppo.

Questi elementi vengono spesso usati all'interno di borderContainers.

Eventi ed azioni
================

Ogni elemento d'intefaccia (widget o tag HTML) permette di agganciare eventi javascript utilizzando la sintassi ``connect_<nome evento>``.
Esempio::

	def divProva(self, parentContainer):
		cp = parentContainer.contentPane(...)
		cp.div(connect_onDoubleClick='codice JS')

Come convenzione, la sintassi ``connect_<nome evento>`` viene usata per gli eventi di Javascript o di DOJO, mentre la sintassi ``<evento>_action`` viene usata per gli eventi e le azioni di genropy.

includedView
============

Le includedView sonoben documentate. Alcuni parametri come ``formPars`` e ``pickerPars`` sono però deprecati (ora esiste un altro modo per fare la stessa cosa.)

E' possibile specificare ``addAction=True`` e ``delAction=True`` per scatenare gli eventi standard (modifica del record in una recordDialog). In questo caso, i record vengono aggiornati nel datastore (i.e. vengono trattati come logicamente facenti parte del record della tabella master, e le modifiche verranno applicate al salvataggio del record master).

Con il metodo ``iv.gridEditor()`` si possono definire gli widgets utilizzati per l'editing delle righe. (Gli widgets di gridEditor vengono riutilizzati, spostandoli nel DOM della pagina, man mano che ci si muove fra le righe.)

Componenti per operare sul datastore
====================================

``data()``:
	memorizza un valore nel datastore
	
``dataFormula()``:
	Calcola una cella del datastore a partire da altri valori (come in un foglio elettronico)

``dataController()``:
	Esegue del codice JS, legandolo ad un evento nel datastore (tramite un resolver).

I parametri di dataController o dataFormula diventano dichiarzioni di variabili locali, utilizzabili nella formula o nel codice JS stesso.

Operazioni remote
*****************

``dataRecord()``:
	**TODO**: da approfondire - credo serva per memorizzare un record di database nel datastore

``dataRemote()``:
	Imposta un resolver nel datastore. All'accesso a questo elemento nel datastore, verrà chiamato codice Python (definito in una funzione con prefisso ``rpc_``) dovrà restituire una bag.

``dataRpc()``:
	come sopra, dataRpc è la funzione di basso livello su cui si basano le funzionalità precedenti. Può essere usata per fare chiamate a codice python (scatenandole passando dei resolver come parametri).
	E' possibile specificare codice JS da chiamare prima della chiamata (con il parametro ``onCalling='codice JS'``) oppure con i risultati ricevuti dal server (``onresult='codice JS'``).

I parametri di queste funzioni che non iniziano con "_" vengono passati al server e sono quindi disponibili al codice Python chiamato.

Gli entry point nella pagina web chiamati da queste funzioni hanno il prefisso ``rpc_``.

**NOTA:** Si può usare ``page.externalUrl(...)`` per avere l'URL di una chiamata RPC (utile per passare gli URL di caricamento/salvataggio XML al documento PDF nel progetto *elezioni*).

Le funzioni possono restituire:

* una bag
* una tupla (bag, dizionario) -- il dizionario contiene gli attributi/metadati della bag, visibili nell'explorer del datastore facendo click tenendo premuto SHIFT

C'è inoltre un'API per effettuare modifiche al datastore nelle chiamate RPC.

FormBuilder
===========

Componente per semplificare la creazione delle forms.

Utilizzando il metodo ``field``, si possono definire i campi specificando semplicemente il nome. Il widget corretto verrà costruito in base al tipo di campo del database. Il metodo ``field`` accetta il parametro ``autospan=N``, corrispondente a ``colspan=N`` più ``width='100%'``.

Triggers
========

Triggers definiti sulla pagina
******************************

E' possibile definire metodi python a livello di pagina web che vengono chiamati quando i record di una data tabella vengono caricati o salvati. I nomi dei metodi devono seguire questa sintassi::

	on<Operazione>
	on<Operazione>_<Nome Package>_<Nome Tabella>

dove *Operazione* è ``Loading``, ``Saving`` oppure ``Saved``.

Questo è implementato a livello di layer rpc/web.

Triggers sulla tabella
**********************

A livello di tabella, sono analogamente disponibili gli eventi ``Inserting``/``Inserted``, ``Updating``/``Updated`` e ``Deleting``/``Deleted``.

**NOTA**: è possibile specificare se il database deve cancellare più record usando una istruzione SQL unica oppure istruzioni singole per ogni record. Sono presenti triggers differenti per i due casi.

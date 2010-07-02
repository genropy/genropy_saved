Scrivere propri componenti
==========================

.. Questa è ancora una bozza, siete i benvenuti se volete aggiungere o modificare il contenuto

Scrivere componenti in GenroPy è facile. Il framework è pensato per rendere estremamente semplice estrarre la
creazione di un componente riusabile da una pagina esistente.

E' tuttavia opportuno seguire alcune norme di comportamento che vi permetteranno di costruire componenti solidi e di facile utilizzo.

Principi per ottenere buoni componenti riusabili
************************************************

- **Documentate l'API pubblica dei vostri componenti**. Durante lo sviluppo, scrivete e mantenete la documentazione dell'API del
  vostro componente. Ricordate che questa comprende, oltre al metodo per creare il componente, anche i callbacks (compresa la loro
  signature e i relativi parametri), la struttura di eventuali bags (o altri oggetti complessi) usate o prodotte dal componente, gli
  elementi nel datastore ed il loro ruolo, il ciclo di vita del componente (per quelli checambiano comportamento nel tempo o segnalano
  eventi, es. le finestre di dialogo).

- **Non rendere i componenti più complessi del necessario**. Non cercate di immaginare e soddisfare tutti i casi in cui il vostro
  componente verrà utilizzato, ciò lo renderà solo inutilmente complesso rendendone difficile l'adozione. Piuttosto, costruire una
  buona API pubblica che permetta di interagirvi e - quando se ne presenta l'opportunità - scrivete un altro componente che coopera (o
  ingloba) il primo per soddisfare nuovi scenari.

- **Verificate subito la validità dei parametri**. Il vostro componente dovrebbe sempre verificare che i
  parametri che riceve siano del tipo corretto e altri obblighi che vogliate imporre sull'utilizzatore del
  vostro componente (e.s. che il parametro _fired inizi con un tegolino "^").

  In Python è d'uso non controllare il tipo dei parametri ricevuti, si adotta il *duck typing*: se cammina come
  un papero, fa quack come un papero, allora è un papero (o qualcosa che vuole passare per tale e il chiamante
  sa cosa sta facendo). Per i componenti però questo non funziona così bene: potrebbero venire impiegati molto
  lontano da dove viene inserito il componente, spesso anche in una chiamata remota a distanza di tempo. In
  questi casi, diventa molto difficile capire dove si trovano gli errori.

- **Se usate callbacks, assicuratevi che siano opzionali**. Il componente deve funzionare anche se i callback
  sono vuoti (sola istruzione "pass") o, meglio ancora, non presenti. In questo modo, il programmatore è libero
  di commentare il codice durante il debug, senza causare errori aggiuntivi. Inoltre, rende possibile imparare
  l'API del vostro componente in modo graduale.

  Se il callback è necessario per il funzionamento del componente, adottate un buon comportamento di default.
  Ad esempio, se il callback vi fornisce i dati da mostrare a video, quando non è presente mostrare una vista
  vuota. Se il callback è assolutamente, decisamente, inesorabilmente necessario per il funzionamento, qualora
  mancasse assicuratevi di segnalarlo con un errore (come per ogni altro parametro obbligatorio).

  Se il componente deve restituirvi alcuni valori, il sistema migliore è passare degli opportuni oggetti
  modificabili nei parametri e pre-impostarli ai corretti valori di default. E' meglio utilizzare classi
  specifiche definite per il componente piuttosto che bags, in questo modo è possibile documentare i metodi e
  gli attributi delle classi e durante il debug questa documentazione sarà disponibile anche in WebError.
  Naturalmente, se i dati che attendete sono effettivamente amorfi, usare le bag è la cosa giusta da fare.

- **Non utilizzare la pagina o altri oggetti globali per passare parametri**. Evitate di utilizzare ``self``,
  cioé l'oggetto pagina, per passare parametri da e verso il componente oppure all'interno del componente
  stesso. La pagina è un namespace pubblico ed è anche piuttosto affollato, inoltre utilizzare un oggetto
  globale per passare parametri rende estremamente difficile la documentazione ed estremamente facili gli
  errori e le sviste.

  Se il vostro componente deve mantenere un suo stato, utilizzate un oggetto definito ad-hoc. Se questo oggetto
  viene utilizzato anche dai callbacks, assicuratevi che sia in una classe documentata.

  Se i callback vengono utilizzati in rpc o remote, il programmatore che usa il vostro compnente non potrà
  utilizzare una closure per mantenere il proprio stato. In questi casi, assicuratevi di dare loro la
  possibilità di passare dati aggiuntivi ai callbacks tramite resolvers e aggiungere una proprietà
  ``user_data`` all'oggetto che mantiene lo stato del vostro componente, in modo che i programmatori possano
  attaccarvi i propri dati. Trattate il contenuto di ``user_data`` come un dato opaco, senza fare alcuna
  supposizione sul tipo di dato memorizzato dall'utente del vostro componente.

- **Provate il vostro componente in una pagina vuota**, con callbacks inesistenti o vuoti. In questo modo
  potrete verificare se tutte le dipendenze (``py_requires``, ``css_requires``, etc.) sono correttamente
  dichiarate e se il componente gestisce correttamente la mancanza di callbacks.
.. _struct:

======
struct
======

    *Last page update*: |today|
    
    TODO
    
    * :ref:`struct_intro`
    
.. _struct_intro:

introduction
============

    The struct is a :ref:`bag` that handles the creation of the :ref:`grids <grid>`.
    
    The class tat handles the construction of the struct is the TODO class.
    
    
    CLIPBOARD::
    
      Definition: La struct è definita ad hoc per fare il modello visivo di una griglia.
      Una struct è una bag che puoi settare con i famosi metodi di struct
      Quindi se vedi il GridStruct è una classe che eredita da structures il quale
      eredita da bag
      
      TUTTI I METODI DEL gnrwebstruct fanno una CHILD alla fine!!!! La parte vera e propria di
      costruzione dell'oggetto HTML viene fatta lato javascript! (attraverso il sourceNode!)
      
      allora la griglia è un widget complesso
      che ha bisogno di una descrizione di ciò che deve visualizzare
      per fare questo "modello" cosa usiamo?
      una bag che descrive come viene fatta ogni singola riga di griglia
      quindi la griglia ha dei dati
      li deve visualizzare in qualche modo
      e la strutturazione dei dati viene fatta tramite le struct
      quando definisci una struct tipicamente
      vai a dire cella per cella dove deve prendere i dati
      quindi se in una riga di bag ci sono
      nome, cognome, annonascita
      tu avrai tre celle
      che saranno nome, cognome, anno, nascita,
      però i dati hanno un tipo
      cioè una data vuoi vederla come data
      ad esempio allora devi aggiungere alla cella il dtype
      MA se i dati fanno riferimento ad una table
      allora puoi usare fieldcell invece di cell
      il quale ti va a mettere la caption e il dtype
      presi direttamente dal model.
      Quindi il fieldcell NON è un widget chiaro?
      a dirla tutta nemmeno field è un widget,
      perché è un metodo che ti torna poi il widget
      
    * spiegare il metodo child(): la child di fatto è una setItem
    
        ::
        
            pane.div() == pane.setItem('xxx',None,tag='div') == pane.child(tag='div',**kwargs)
    
    * Example::
    
        def unitStruct(self):
            struct = self.newGridStruct('cdxbase.row')
            r = struct.view().rows()
            r.fieldcell(...)
            r.fieldcell(...)
            r.fieldcell(...)
            
    * Example::
    
        r = struct.child('view').child('rows',classes='df_grid',cellClasses='df_cells',headerClasses='df_headers')
        r.child('cell',field='procedure',width='9em',name='Procedure')
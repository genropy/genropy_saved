.. _genro_struct:

======
struct
======

    *Last page update*: |today|
    
    add???
    
    * Definition: La struct è definita ad hoc per fare il modello visivo di una griglia.
      Una struct è una bag che puoi settare con i famosi metodi di struct
      Quindi se vedi il GridStruct è una classe che eredita da structures il quale
      eredita da bag
      
      TUTTI I METODI DEL gnrwebstruct fanno una CHILD alla fine!!!! La parte vera e propria di
      costruzione dell'oggetto HTML viene fatta lato javascript! (attraverso il sourceNode!)
      
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
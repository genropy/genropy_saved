.. _genro_struct:

======
struct
======

    add???
    
    * Definition: La struct è definita ad hoc per fare il modello visivo di una griglia.
      Una struct è una bag che puoi settare con i famosi metodi di struct
      Quindi se vedi il GridStruct è una classe che eredita da structures il quale eredita da bag
    
    * Example::
    
        def structUnita(self):
            struct = self.newGridStruct('cdxbase.tabella_millesimale_riga')
            r = struct.view().rows(classes='df_grid', cellClasses='df_cells', headerClasses='df_headers')
            r.fieldcell('@unita_immobiliare_id.nome',name=u'Unità',width='12em')
            r.fieldcell('@unita_immobiliare_id.tipo',name='Tipo',width='15em')
            r.fieldcell('valore',name='Valore',width='10em')
            return struct
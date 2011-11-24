.. _includedgrid:

============
includedGrid
============

    *Last page update*: |today|
    
    * :ref:`includedgrid_def`
    * :ref:`includedgrid_descr`
    
.. _includedgrid_def:

definition
==========

    .. method:: includedGrid(self,parentBC,nodeId=None,frameCode=None,datapath=None,struct=None,table=None,pbl_classes=True,storepath=None,label=None,caption=None,filterOn=None,editorEnabled=None,canSort=True,dropCodes=None,add_kwargs=None,del_kwargs=None,upd_kwargs=None,print_kwargs=None,export_kwargs=None,tools_kwargs=None,top_kwargs=None,datamode=None,**kwargs)
    
    The :ref:`includedgrid` is a :ref:`grid` that allows the inline editing. So, the insertion
    or the modify of records is handled inside the grid
    
    **Parameters**: 
                    
                    * **parentBC**: the root parent :ref:`bordercontainer`
                    * **nodeId**: the includedGrid's :ref:`nodeid`
                    * **frameCode**: it is the includedGrid's :ref:`nodeid`. You have to define it OR the *nodeId* attribute
                    * **datapath**: allow to create a hierarchy of your data’s addresses into the datastore.
                      For more information, check the :ref:`datapath` and the :ref:`datastore` pages
                    * **struct**: the name of the method that defines the :ref:`struct`
                    * **table**: the :ref:`database table <table>`
                    * **pbl_classes**: boolean. The :ref:`pbl_classes` attribute
                    * **storepath**: TODO
                    * **label**: TODO
                    * **caption**: TODO
                    * **filterOn**: TODO
                    * **editorEnabled**: TODO
                    * **canSort**: boolean. TODO
                    * **dropCodes**: TODO
                    * **add_kwargs**: TODO
                    * **del_kwargs**: TODO
                    * **upd_kwargs**: TODO
                    * **print_kwargs**: TODO
                    * **export_kwargs**: TODO
                    * **tools_kwargs**: TODO
                    * **top_kwargs**: TODO
                    * **datamode**: TODO
    
.. _includedgrid_descr:

description
===========

    CLIPBOARD::
    
        lavora come se fosse la visualizzazione di una Bag; nella rappresentazione griglia
        vedi tutte le righe di una Bag, quando editi (dialog oppure inline) (l'editing inline
        è solo della includedGrid). gridEditor serve a modificare la includedGrid.
        
        il "datapath" dell'includedGrid serve solo come retrocompatibilità con l'includedView,
        quindi come path per i dati nell'includedGrid bisogna usare lo "storepath"
        
        lo storepath può puntare alla Bag (aggiungere anche il datamode='bag'), oppure si può
        puntare ad un path chiocciolinato
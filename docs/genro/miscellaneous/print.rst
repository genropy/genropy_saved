.. _print:

=====
Print
=====
    
    *Last page update*: |today|
    
.. _print_intro:

introduction
============

    In this page we learn about how to make a print in a :ref:`project`.
    
    In GenroPy a print is handled as a *resource script* of the :ref:`tables <table>`. So,
    they can be easily personalized for every application.
    
    The prints can be handled through two files:
    
    * one file for the settings of the print (:ref:`print_settings`)
    * one file for the layout properties of the print (:ref:`print_layout`)
    
.. _print_settings:

print settings file
===================

    **File location**
    
        The location of the print settings file must follow this path::
        
            projectName/packages/packageName/resources/tables/tableName/print/fileName
            
        where:
        
        * ``projectName`` is the name of the :ref:`project`
        * ``packages`` is the :ref:`packages_index` folder
        * ``packageName`` is the name of the package
        * ``resources`` is the :ref:`public_resources` folder
        * ``tables`` is the :ref:`resources_tables` folder
        * ``tableName`` is the name of the :ref:`table` to which the print is linked
        * ``fileName`` is the name of the print settings file: there is any convention about it
        
        This is a graphical map of the location of the print settings file into a :ref:`project`:
        
        .. image:: ../_images/print_settings_file.png
        
.. _print_settings_example:

print settings file - example
-----------------------------
    
    ::
    
        # -*- coding: UTF-8 -*-
        
        from gnr.web.batch.btcprint import BaseResourcePrint
        
        caption = 'Performances Print'
        tags = 'user' add??? correct???
        description = 'Print performances of selected doctors'
        
        class Main(BaseResourcePrint):
            batch_prefix = 'st_prest'
            batch_title = 'Performances Print' # 'Stampa prestazioni'
            batch_cancellable = True
            batch_delay = 0.5
            html_res = 'html_builder/medico_prestazioni'
            #templates = 'base'
            mail_address='@anagrafica_id.email'

            def table_script_parameters_pane(self,pane,**kwargs):
                fb = pane.formbuilder(cols=2)
                self.periodCombo(fb,lbl='!!Periodo',period_store='.period')
                fb.div(value='^.period.period_string', _class='period',font_size='.9em',font_style='italic')
                fb.dataFormula(".period_input", "'questo mese'")
                fb.checkbox(value='^.hideTemplate',label='!!Hide headers')
                
    For more information on the periodCombo check the :ref:`periodcombo` page
    
.. _print_layout:
    
print layout file
=================

    add???
    
.. _print_clipboard:

clipboard
=========
    
    CLIPBOARD::
    
        Layout, righe e celle
        =====================
        
        Per posizionare le cose, abbiamo a disposizione tre oggetti:
        
            * **layout**. Possono contenere soltanto righe.
            * **row**. Possono contenere soltanto celle. Le righe hanno l'altezza, se non viene
            specificata (o se è zero) la riga è elastica.
            * **celle**. Possono contenere layout. Le celle hanno la larghezza. Due celle attaccate
            autocollassano i bordi (rimane un bordo solo).
            
        Le lunghezze sono sempre specificate in millimetri (mm). Vedi :mod:`gnr.core.gnrhtml`
        per ulteriori dettagli.
        
        Attributi e callbacks
        =====================
        
        Il foglio è diviso in varie parti che hanno corrispondenti callbacks:
        
        (attributo, callback)
        
        attributo page_header, callback pageHeader -- header della pagina (es. per carta intestata)
        page_footer, callback pageFooter -- footer della pagina (es. per carta intestata)
        callback docHeader -- intestazione del documento
        callback docFooter -- footer del documento
        callback prepareRow -- chiamato per ogni riga del corpo
        
        Il ``pageHeader``/``pageFooter`` è solitamente riservato alla carta intestata o al template,
        ``docHeader``/``docFooter`` viene usato per la testata/footer. Ad esempio, in una stampa fattura,
        l'intestazione va nel ``docHeader`` mentre le righe nel corpo.
        
        ``prepareRow`` viene chiamata in automatico per ogni riga. Ha una sintassi tipo field.
        
        Il componente prende i dati da una tabella, ma se invece si vogliono passare dati con altro
        sistema si può ridefinire il metodo ``loadRecord``. 
        
        Invocazione della stampa
        ========================
        
        La stampa può essere invocata in vari modi: si può mettere un bottone in una standardtable
        (c'è un callback apposta), stampa tutte le righe selezionate. Il componente ``serverPrint()``
        mostra una finestra di dialogo per la stampa (in cui è possibile aggiungere ulteriori parametri,
        con un callback) e poi prepara il batch di stampa.
        
        Esempio::
        
            def bottomPane_stampaPrestazioni(self,pane):
                pane.button(fire="#stampaprestazione.open",label='Stampa prestazioni')
                self.serverPrint(pane,name='stampaprestazione',table_resource='html_res/medico_prestazioni',
                                parameters_cb=self.cb_period,docName='prestazioni_medici',thermoParams=True)
        
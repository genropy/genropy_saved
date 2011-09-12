.. _print:

=====
print
=====
    
    *Last page update*: |today|
    
    * :ref:`print_intro`
    * :ref:`print_settings`:
    
        * :ref:`print_settings_webpage_variables`
        * :ref:`print_settings_location`
        * :ref:`example <print_settings_example>`
        
    * :ref:`print_layout`:
    
        * :ref:`print_layout_webpage_variables`
        * :ref:`print_layout_location`
        * :ref:`example <print_layout_example>`
        
    * :ref:`print_gui`:
    
        * :ref:`print_webpage`
        * :ref:`print_setting_dialog`
        
        
.. _print_intro:

introduction
============

    In this page we learn about how to make a print in a :ref:`project`.
    
    In GenroPy a print is handled as a *resource script* of the :ref:`tables <table>`. So,
    they can be easily personalized for every application.
    
    The prints can be handled through two files:
    
    * one file for the settings of the print (:ref:`print_settings`)
    * one file for the layout properties of the print (:ref:`print_layout`)
    
    When you have created these two files, you have to create in a :ref:`webpages_webpages`
    a GUI that allows the user to start a print. If you use the :ref:`th`, this process
    is auto handled by the component. For more information on how to create a print in a
    webpage, check the :ref:`print_webpage` section
    
.. _print_settings:

print settings file
===================

.. _print_settings_webpage_variables:

webpage variables
-----------------

    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize your print setting page. Let's see all of them:
    
    * *html_res*: MANDATORY. Specify the location path of the :ref:`print_layout`.
      The path you specify starts automatically from::
      
        projectName/packages/packageName/resources/tables/tableName/
        
      **Example**:
      
        if you write::
        
          html_res='html_builder/doctor_performances'
          
        then the location path of your print layout file must be::
        
           projectName/packages/packageName/resources/tables/tableName/html_builder/doctor_performances
           
        where ``html_builder`` is a folder created by you and ``doctor_performances`` is the name of
        your print layout file.
        
    * *dialog_height*: specify the height of the :ref:`print_setting_dialog`
    * *dialog_width*: specify the width of the :ref:`print_setting_dialog`
    * *dialog_height_no_par*: add???
    * *batch_prefix*: a string with a prefix for the name of the batch
      
      **Example**::
      
        batch_prefix = 'st_prest'
        
    batch_title = 'Performances Print' # 'Stampa prestazioni'
    batch_cancellable = True
    batch_delay = 0.5
    html_res = 'html_builder/medico_prestazioni'
    #templates = 'base'
    mail_address='@anagrafica_id.email'
    
.. _print_settings_location:

file location
-------------
    
    The location of the print settings file must follow this path::
    
        projectName/packages/packageName/resources/tables/tableName/print/fileName
        
    where:
    
    * ``projectName`` is the name of the :ref:`project`
    * ``packages`` is the :ref:`packages_index` folder
    * ``packageName`` is the name of the package
    * ``resources`` is the :ref:`public_resources` folder
    * ``tables`` is the :ref:`resources_tables` folder
    * ``tableName`` is the name of the :ref:`table` to which the print is linked
    * ``fileName`` is the name you choose for your print settings file:
      there is any convention about it
    
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

.. _print_layout_webpage_variables:

webpage variables
-----------------

    add???

.. _print_layout_location:

file location
-------------

    add???
    
.. _print_layout_example:
    
print layout file - example
---------------------------

    add???
    
.. _print_gui:

GUI
===

.. _print_webpage:

user GUI to start a print
=========================

    .. note:: if you use the :ref:`th` component you have also a print management system.
              So, you don't need to create any GUI that allows user to start a print.
              Continue the reading of this section if you are not using the TableHandler
    
    To let the user starts a print from a :ref:`webpages_webpages`, you have to create 
    a :ref:`button` using the :ref:`action` attribute that performs a :ref:`publish`.
    
    Create your button remembering that:
    
    * the first attribute is the button label
    * the *action* attribute must call a PUBLISH that follows this syntax::
    
        action = 'PUBLISH tablehandler_run_script="print", "fileName"'
        
    where:
    
    * "print" is the :ref:`tables_print` folder (so this is a default, you will have always
      "print" as parameter)
    * ``fileName`` is the name of your :ref:`print setting file <print_settings>` (without its extension)
    
    **Example**:
    
        If you created a print setting file called "printing_performance", then your button could be::
        
            class GnrCustomWebPage(object):
                def main(self, root, **kwargs):
                    pane = contentPane(height='300px', datapath='my_pane')
                    pane.button('New print',action='PUBLISH tablehandler_run_script="print","printing_performance";')
                    
.. _print_setting_dialog:

print setting dialog
--------------------

    This dialog is the GUI of the :ref:`print setting file <print_settings>`.
    
    add???
    
.. _print_clipboard:

clipboard
=========
    
    .. note:: my clipboard...
    
    ::
    
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
        
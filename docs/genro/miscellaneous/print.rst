.. _print:

=====
print
=====
    
    *Last page update*: |today|
    
    * :ref:`print_intro`
    * :ref:`print_settings`:
    
        * :ref:`print_settings_import`
        * :ref:`print_settings_main`
        * :ref:`print_settings_webpage_variables`
        * the :ref:`print_settings_table_script_parameters_pane` method
        * :ref:`print_settings_onrecordexit`
        * :ref:`print_settings_webpage`
        * :ref:`print_setting_dialog`
        * :ref:`print_setting_dialog_print_region`
        * :ref:`example <print_settings_example>`
        * :ref:`print_settings_location`
        
    * :ref:`print_layout`:
    
        * :ref:`print_layout_import`
        * :ref:`print_layout_webpage_variables`
        * :ref:`print_layout_location`
        * :ref:`example <print_layout_example>`
        
.. _print_intro:

introduction
============

    In this page we learn about how to make a print in a :ref:`project`.
    
    In GenroPy a print is handled as a *resource script* of the :ref:`tables <table>`. So,
    it can be easily personalized for every application.
    
    The prints can be handled through two files:
    
    * one file for the settings of the print (:ref:`print_settings`)
    * one file for the layout properties of the print (:ref:`print_layout`)
    
    When you have created these two files, you have to create in a :ref:`webpages_webpages`
    a GUI that allows the user to start a print. If you use the :ref:`th`, this process
    is auto handled by the component. For more information on how to create a print in a
    webpage, check the :ref:`print_settings_webpage` section
    
.. _print_settings:

print settings file
===================

    The print settings file allows to specify the print settings.
    
    In order to use it, you have to:
    
    * :ref:`print_settings_import` the correct module
    * create the :ref:`print_settings_main`
    
    In the Main class you have to:
    
    * add some :ref:`print_settings_webpage_variables`
    * create the :ref:`print_settings_table_script_parameters_pane` method (it handles the
      :ref:`print_setting_dialog` GUI)
      
    When you created it, you have to:
    
    * create a GUI to let the user starts the print (:ref:`print_settings_webpage`)
      
.. _print_settings_import:

import
------

    To use the print setting file you have to import::
    
        from gnr.web.batch.btcprint import BaseResourcePrint
        
    .. _print_settings_main:

Main class
----------

    The Main class inherits from the :class:`BaseResourcePrint
    <gnr.web.batch.btcprint.BaseResourcePrint>` class, so write::
    
        class Main(BaseResourcePrint):
        
    .. _print_settings_webpage_variables:

webpage variables
-----------------

    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize your Main class. Let's see all of them:
    
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
        
    * *batch_cancellable*: add???
    * *batch_delay*: a string with the time milliseconds start delay
    * *batch_immediate*: add???. Default value is ``False``
    * *batch_prefix*: a string with a prefix for the batch name
      
      **Example**::
      
        batch_prefix = 'st_prest'
        
    * *batch_title*: a string with the :ref:`print_setting_dialog` title
    * *dialog_height*: a string with the :ref:`print_setting_dialog` height
    * *dialog_height_no_par*: add???
    * *dialog_width*: a string with the :ref:`print_setting_dialog` width
    * *mail_address*: add???
    * *mail_tags*: specify the authorization level to send mail. More information
      on :ref:`print_setting_dialog_print_region` section
    * *templates*: add???
    
.. _print_settings_table_script_parameters_pane:

``table_script_parameters_pane``
--------------------------------

    .. method:: table_script_parameters_pane(self, pane, **kwargs)
                
                **Parameters: pane** - it represents a :ref:`contentpane` through
                which you can attach your :ref:`webpage elements <webpage_elements_index>`
    
    This ``table_script_parameters_pane`` is an hook method.
    
    Through this method you can add some additional parameters of your batch. In particular,
    you can modify the "second region" of the :ref:`print_setting_dialog` (in the next image,
    the region is pointed by the number 2). The print setting dialog is the dialog that
    represents the :ref:`print setting file <print_settings>` in your :ref:`webpages_webpages`:
    
    *In the image, the print setting dialog. The point 2 is the pane handled by the*
    *``table_script_parameters_pane`` method*
        
    .. image:: ../_images/print/print_settings_dialog_2.png
    
    **Example**: let's see the code relative to the previous image::
    
        def table_script_parameters_pane(self, pane, **kwargs):
            fb = pane.formbuilder(cols=2)
            self.periodCombo(fb,lbl='!!Period',period_store='.period')
            fb.div(value='^.period.period_string', font_size='.9em',font_style='italic')
            fb.checkbox(value='^.hideTemplate',label='!!Hide headers')
            
    We used the periodCombo in the example; for more information about it check the
    :ref:`periodcombo` page
    
.. _print_settings_onrecordexit:

onRecordExit
------------

    .. automethod:: gnr.web.batch.btcprint.BaseResourcePrint.onRecordExit
    
.. _print_settings_webpage:

webpage - start a print
-----------------------

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

    The print setting dialog is the dialog that represents the :ref:`print setting file <print_settings>`
    in your :ref:`webpages_webpages`:
    
    .. image:: ../_images/print/print_settings_dialog.png
    
    It is divided in five regions:
    
    * *region 1 - title region*: it includes the window title, configurable through the ``batch_title``
      :ref:`webpage variable <print_settings_webpage_variables>`
    * *region 2 - customizable region*: it includes a :ref:`print_settings_table_script_parameters_pane`
      hook method
    * *region 3 - print region*: it includes a :meth:`table_script_option_pane
      <gnr.web.batch.btcprint.BaseResourcePrint.table_script_option_pane>` method
    * *region 4 - notes region*: it includes a :meth:`table_script_options_client_print
      <gnr.web.batch.btcprint.BaseResourcePrint.table_script_options_client_print>` method
    * *region 5 - bottom region*: it includes a bottom pane with the ``Cancel`` (cancels
      the dialog) and ``Confirm`` (starts the batch) buttons
      
    We have already described most of the regions (follow the relative links). The only one that needs more
    explanations is the print region:
    
.. _print_setting_dialog_print_region:

print setting dialog - print region
-----------------------------------

    In the print regions you can swap up to 4 frames through a :ref:`radiobutton group <radiobutton>`.
    The 4 frames are:
    
    #. **PDF download**:
    
       .. image:: ../_images/print/print_pdf_download.png
       
       From this pane user can choose a name for the saved file and can choose through a :ref:`checkbox`
       to save the file in a zip format.
       
    #. **Server print**:
    
       .. image:: ../_images/print/print_server_print.png
       
       From this pane user can choose the printer, the paper type and the tray.
       
    #. **PDF by mail**:
    
       .. image:: ../_images/print/print_pdf_by_mail.png
       
       .. note:: this pane is accessible only by users that have some administration privileges.
                 By default only users with 'admin' privileges can access to this (more information
                 on the :ref:`auth` page). You can change this default modifying the *mail_tags*
                 :ref:`print_settings_webpage_variables`
                 
       From this pane user can send the PDF by email.
       
    #. **Deliver mails**:
    
       .. image:: ../_images/print/print_deliver_mails.png
       
       From this pane user can deliver emails.
       
       add???
       
.. _print_settings_example:

print settings file - example
-----------------------------
    
    Let's see an example page of a :ref:`print_settings`::
    
        # -*- coding: UTF-8 -*-
        
        from gnr.web.batch.btcprint import BaseResourcePrint
        
        class Main(BaseResourcePrint):
            batch_prefix = 'st_prest'
            batch_title = 'Performances Print'
            batch_cancellable = True
            batch_delay = 0.5
            html_res = 'html_builder/performances_print'
            
            def table_script_parameters_pane(self, pane, **kwargs):
                fb = pane.formbuilder(cols=2)
                self.periodCombo(fb,lbl='!!Period',period_store='.period')
                fb.div(value='^.period.period_string', font_size='.9em',font_style='italic')
                fb.checkbox(value='^.hideTemplate',label='!!Hide headers')
                
            def onRecordExit(self, record=None):
                print record
                
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
    
    .. image:: ../_images/print/print_settings_file.png
    
.. _print_layout:
    
print layout file
=================

.. _print_layout_import:

import
------

    add???

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
        
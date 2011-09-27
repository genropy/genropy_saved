.. _print_layout:

=================
print layout file
=================

    **First steps**:
    
    * :ref:`print_layout_intro`
    * :ref:`print_layout_location`
    
    **Features**:
    
    * :ref:`print_layout_features`
    * :ref:`print_layout_zones`
    
    **Creation of the file**:
    
    * :ref:`print_layout_import`
    * :ref:`print_layout_main`:
    
        * :ref:`print_layout_main_webpages_variables`
        * :ref:`print_layout_main_methods`:
        
            * hook methods: :ref:`layout_docheader`, :ref:`layout_docfooter`,
              :ref:`layout_pageheader`, :ref:`layout_pagefooter`
            * layout elements: :ref:`layout_element`, :ref:`layout_row`,
              :ref:`layout_cell`
              
    **Examples**:
    
    * :ref:`example <print_layout_example>`
    
    **Library reference**:
    
    * :ref:`layout_library`
    
.. _print_layout_intro:

introduction
============

    The print layout file allows to specify the layout of a print
    
    * In the :ref:`print_layout_location` section we describe the specific location
      of the print layout file
      
    Once you created the file you have to:
    
    * import the correct module - :ref:`print_layout_import` section
    * create the Main class - :ref:`print_layout_main` section
    
    Inside the Main class you may customize your layout through:
    
    * some variables - :ref:`print_layout_main_webpages_variables` section
    * some methods - :ref:`Main class methods <print_layout_main_methods>` section
    
.. _print_layout_location:

file location
=============

    The location of the print layout file must follow a standard path followed
    by a custom path::
    
        projectName/packages/packageName/resources/tables/tableName/customPath
        
    where:
    
    * ``projectName`` is the name of the :ref:`project`
    * ``packages`` is the :ref:`packages_index` folder
    * ``packageName`` is the name of the package
    * ``resources`` is the :ref:`public_resources` folder
    * ``tables`` is the :ref:`resources_tables` folder
    * ``tableName`` is the name of the :ref:`table` related to the print
    * ``customPath`` is the path you choose for your print layout file through the
      :ref:`"html_res" webpage variable <print_html_res>` of the :ref:`print_settings_main`
      of the :ref:`print_settings` (there is any convention about the name you have to use)
      
        **customPath syntax**::
        
            anyFolderYouWant/fileNameOfThePrintSettingsFile
            
        **Example**:
        
        if you have a project called ``base``, a package called ``invoice``,
        a ``doctor`` table and in your :ref:`print_settings`
        ``html_res = 'html_builder/my_layout'``, then the path of the print layout file is::
        
            base/packages/invoice/resources/tables/doctor/html_builder/my_layout
            
        where "html_builder" is a folder, "my_layout" is the file name of the print layout file.
        
    This is a graphical map of the location of the print layout file into a :ref:`project`:
    
        *In this image the print layout file is called "custom_file";*
        *html_res = 'custom_folder/custom_file'*
    
    .. image:: ../../_images/print/print_layout_file.png
    
.. _print_layout_features:

layout page - features
======================

    add???
    
    LE STAMPE SI POSSONO FARE O IN MODALITA' SINGOLO RECORD, O IN MODALITA'
    TESTATA RIGHE (la TESTATA è chiamata DOC): documentare con immagini
    
.. _print_layout_zones:
    
layout print zones
==================

    add???
    
.. _print_layout_pagedocgrid:

page, doc, grid
===============
    
    add???
    
    add??? an image with the graphical differences between doc - page - grid
    
.. _print_layout_page:

page
----

    add???
    
.. _print_layout_doc:

doc
---

    add???
    
.. _print_layout_grid:

grid
----

    add???
    
.. _print_layout_footer_height:
    
footer height
-------------

    add???
    
.. _print_layout_header_height:

header height
-------------

    add???
    
.. _print_layout_import:

import
======

    In order to use the layout functionalities you have to import in your print layout file
    the :class:`TableScriptToHtml <gnr.web.gnrbaseclasses.TableScriptToHtml>` class::
    
        from gnr.web.gnrbaseclasses import TableScriptToHtml
        
    Then we have to create the Main class:
        
.. _print_layout_main:

Main class
==========

    The Main class inherits from the :class:`TableScriptToHtml
    <gnr.web.gnrbaseclasses.TableScriptToHtml>` class, so write::
    
        class Main(TableScriptToHtml):
        
    In the Main class you have to add some webpage variables:
    
.. _print_layout_main_webpages_variables:

Main class webpage variables
============================

    .. note:: the unit of measurement of all the numerical variables are in millimeters
              (e.g: ``print_width = 200`` means 200 millimeters)
              
    With the term ``webpages variables`` we mean that there are some defined variables
    belonging to the two parent classes (the ``BagToHtml`` class and the ``TableScriptToHtml``
    class) of the Main class that allow you to customize your print layout.
    
    We list here all these variables, specifying their parent class; if you need
    informations about them, click on their name to go on their description section.
    
    List of the webpage variables of the :class:`BagToHtml <gnr.core.gnrbaghtml.BagToHtml>` class:
    
    * :ref:`bagtohtml_copies_per_page`
    * :ref:`bagtohtml_copy_extra_height`
    * :ref:`bagtohtml_css_requires`
    * :ref:`bagtohtml_currencyformat`
    * :ref:`bagtohtml_doc_header_height`
    * :ref:`bagtohtml_doc_footer_height`
    * :ref:`bagtohtml_encoding`
    * :ref:`bagtohtml_grid_header_height`
    * :ref:`bagtohtml_grid_footer_height`
    * :ref:`bagtohtml_grid_col_widths`
    * :ref:`bagtohtml_grid_row_height`
    * :ref:`bagtohtml_page_debug`
    * :ref:`bagtohtml_page_footer_height`
    * :ref:`bagtohtml_page_header_height`
    * :ref:`bagtohtml_page_height`
    * :ref:`bagtohtml_page_leftbar_width`
    * :ref:`bagtohtml_page_rightbar_width`
    * :ref:`bagtohtml_page_margin_bottom`
    * :ref:`bagtohtml_page_margin_left`
    * :ref:`bagtohtml_page_margin_right`
    * :ref:`bagtohtml_page_margin_top`
    * :ref:`bagtohtml_page_width`
    * :ref:`bagtohtml_print_button`
    * :ref:`bagtohtml_row_mode`
    * :ref:`bagtohtml_rows_path`
    * :ref:`bagtohtml_starting_page_number`
    * :ref:`bagtohtml_templates`
    
    List of the webpage variables of the :class:`TableScriptToHtml
    <gnr.web.gnrbaseclasses.TableScriptToHtml>` class:
    
    * :ref:`tablescripttohtml_rows_table`
    * :ref:`tablescripttohtml_virtual_columns`
    
css_requires
------------
    
    Allow to import :ref:`css` files. For more information, check the
    :ref:`webpages_css_requires` section
    
.. _print_layout_main_methods:
    
build the layout - Main class methods
=====================================

    In this section we describe all the layout hook methods and all the elements that allow
    you to personalize the print.
    
    They are:
    
    * :ref:`layout_definestandardstyles`: allow to add???
    * :ref:`layout_docheader`: allow to add???
    * :ref:`layout_docfooter`: allow to add???
    * :ref:`layout_pageheader`: allow to add???
    * :ref:`layout_pagefooter`: allow to add???
    
    Inside these methods, you can create the layout through the following three methods:
    
    * the :ref:`layout method <layout_element>`: allow to return a layout element
    * the :ref:`row method <layout_row>`: allow to return a row element 
    * the :ref:`cell method <layout_cell>`: allow to return a cell element
    
.. _layout_definestandardstyles:

defineStandardStyles
--------------------

    .. automethod:: gnr.core.gnrbaghtml.BagToHtml.defineStandardStyles
    
    add???
    
.. _layout_docheader:

docHeader
---------

    .. automethod:: gnr.core.gnrbaghtml.BagToHtml.docHeader
    
    add???
    
.. _layout_docfooter:

docFooter
---------

    .. automethod:: gnr.core.gnrbaghtml.BagToHtml.docFooter
    
    add???
    
.. _layout_pageheader:

pageHeader
----------

    .. automethod:: gnr.core.gnrbaghtml.BagToHtml.pageHeader
    
    add???
    
.. _layout_pagefooter:

pageFooter
----------

    .. automethod:: gnr.core.gnrbaghtml.BagToHtml.pageFooter
    
    add???
    
.. _layout_element:
    
layout
------

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.layout
    
    add???
    
.. _layout_row:
    
row
---

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.row
    
    add???
    
.. _layout_cell:
    
cell
----

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.cell
    
    add???
    
.. _print_layout_example:
    
print layout file - example
===========================

    Let's see an example page of a :ref:`print_layout`::
    
        #!/usr/bin/env pythonw
        # -*- coding: UTF-8 -*-
        
        from gnr.web.gnrbaseclasses import TableScriptToHtml
        
        class Main(TableScriptToHtml):
            maintable = 'polimed.medico'
            rows_table = 'polimed.prestazione'
            rows_path = 'rows'
            row_mode='attribute'
            page_header_height = 0
            page_footer_height = 0
            doc_header_height = 10
            doc_footer_height = 10
            grid_header_height = 6.2
            grid_footer_height = 0
            grid_col_widths=[17,12,0,0,20,15,15,20]
            grid_col_headers = 'Data,Ora,Paziente,Prestazione,Convenzione,Importo,Costo,Fattura'
            grid_row_height=5.3
            
            def docHeader(self,header):
                layout = header.layout(name='header',um='mm',
                                       lbl_class='smallCaption',
                                       top=1,bottom=1,left=1,right=1,
                                       lbl_height=3,
                                       border_width=.3,
                                       border_color='gray',
                                       style='line-height:6mm;text-align:left;text-indent:2mm;')        
                row=layout.row(height=10)
                row.cell("%s %s" %(self.field('@anagrafica_id.nome'), self.field('@anagrafica_id.cognome')),lbl='Prestazioni di')
                row.cell(self.toText(self.getData('period.from')), lbl='Dal',width=30,content_class='aligned_right')
                row.cell(self.toText(self.getData('period.to')), lbl='al', width=30,content_class='aligned_right')
                row.cell(self.pageCounter(), lbl='Pagina', width=12,content_class='aligned_right')
                
            def docFooter(self, footer,lastPage=None):
                if not lastPage:
                    return
                layout = footer.layout(name='footerL',um='mm',border_color='gray',
                                           lbl_class='smallCaption',
                                          top=1,bottom=1,left=80,right=1,
                                          lbl_height=3,border_width=0.3,
                                          content_class='aligned_right')
                row=layout.row(height=0)
                lastPage = lastPage or False
                if lastPage:
                    totals_dict = {}
                    totals_dict['importo'],totals_dict['costo'] = self.getData('rows').sum('#a.importo,#a.costo')

                    row.cell(self.toText(totals_dict['importo'],format=self.currencyFormat),lbl='Totale importo')
                    row.cell(self.toText(totals_dict['costo'],format=self.currencyFormat),lbl='Totale costo')
                else:
                    row.cell()
                    
            def gridLayout(self,body):
                return body.layout(name='rowsL',um='mm',border_color='gray',
                                    top=1,bottom=1,left=1,right=1,
                                    border_width=.3,lbl_class='caption',
                                    style='line-height:5mm;text-align:left;font-size:7.5pt')
                                    
            def mainLayout(self,page):
                style = """font-family:"Lucida Grande", Lucida, Verdana, sans-serif;
                            text-align:left;
                            line-height:5mm;
                            font-size:9pt;
                            """
                return page.layout(name='pageLayout',width=190,
                                    height=self.page_height,
                                    um='mm',top=0,
                                    left=5,border_width=0,
                                    lbl_height=4,lbl_class='caption',
                                    style=style)
                                    
            def prepareRow(self,row):
                # this callback prepare the row of the maingrid
                style_cell = 'text-indent:2mm;border-bottom-style:dotted;'
                self.rowCell('data',style=style_cell)
                self.rowCell('ora',format='HH:mm', style=style_cell)
                self.rowCell('paziente', style=style_cell)
                self.rowCell('prestazione', style=style_cell)
                self.rowCell('convenzione_codice', style=style_cell)
                self.rowCell('importo',format=self.currencyFormat, style=style_cell,content_class='aligned_right')
                self.rowCell('costo',format=self.currencyFormat, style=style_cell,content_class='aligned_right')
                self.rowCell('fattura', style=style_cell,content_class='aligned_right')
                
            def onRecordLoaded(self):
                where = '$data >= :data_inizio AND $data<= :data_fine AND medico_id=:m_id'
                columns ="""$medico,$data,$ora,$paziente,$prestazione,
                            @convenzione_id.codice AS convenzione_codice,
                            $importo,$costo,@fattura_id.numero AS fattura"""
                query = self.db.table(self.rows_table).query(columns=columns, where=where, 
                                                                     data_inizio=self.getData('period.from'),
                                                                     data_fine=self.getData('period.to'),
                                                                     m_id=self.record['id'])
                selection = query.selection()
                if not selection:
                    return False
                self.setData('rows',selection.output('grid'))
                
            def outputDocName(self, ext=''):
                medico = self.getData('record.@anagrafica_id.ragione_sociale')
                mlist = medico.split(' ')
                medico = ''.join(mlist)
                return '%s.%s' %(medico.lower(),ext)
                
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
            * **celle**. Possono contenere UN SOLO layout. Le celle hanno la larghezza.
            Due celle attaccate autocollassano i bordi (rimane un bordo solo).
            
        Le lunghezze sono sempre specificate in millimetri (mm). Vedi :mod:`gnr.core.gnrhtml` per
        ulteriori dettagli
        
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
        
        Il componente prende i dati da una tabella, ma se invece si vogliono passare dati con
        un altro sistema si può ridefinire il metodo ``loadRecord``
        
.. _layout_library:
                
print layout file - library reference
=====================================

    For the complete library reference, check:
    
    * the :class:`TableScriptToHtml <gnr.web.gnrbaseclasses.TableScriptToHtml>` class
    * the :class:`BagToHtml <gnr.core.gnrbaghtml.BagToHtml>` class
    
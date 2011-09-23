.. _print_layout:

=================
print layout file
=================

    * :ref:`print_layout_intro`
    * :ref:`print_layout_location`
    * :ref:`print_layout_features`
    * :ref:`print_layout_import`
    * :ref:`print_layout_main`
    * :ref:`print_layout_webpage_variables`
    * :ref:`layout_building`:
    
        * hook methods: :ref:`layout_docheader`, :ref:`layout_docfooter`,
          :ref:`layout_pageheader`, :ref:`layout_pagefooter`
        * layout elements: :ref:`layout_element`, :ref:`layout_row`,
          :ref:`layout_cell`
          
    * :ref:`example <print_layout_example>`
    
.. _print_layout_intro:

introduction
============

    The print layout file allows to specify the print layout
    
    * In the :ref:`file location section <print_layout_location>` we describe
      the specific location of the print settings file
    
    Once you created the file you have to:
    
    * :ref:`print_layout_import` the correct module
    * create the :ref:`print_layout_main`
    
    In the Main class you have to:
    
    * add some :ref:`print_layout_webpage_variables`
    
    ::
    
        * create the BOH methods (they handle the print)
        
.. _print_layout_location:

file location
=============

    The location of the print layout file must follow a standard path followed by a
    path you define in the *html_res* :ref:`print_settings_webpage_variables`::
    
        projectName/packages/packageName/resources/tables/tableName/customPath
        
    where:
    
    * ``projectName`` is the name of the :ref:`project`
    * ``packages`` is the :ref:`packages_index` folder
    * ``packageName`` is the name of the package
    * ``resources`` is the :ref:`public_resources` folder
    * ``tables`` is the :ref:`resources_tables` folder
    * ``tableName`` is the name of the :ref:`table` to which the print is linked
    * ``customPath`` is the path you choose for your print layout file through the
      :ref:`"html_res" webpage variable <print_html_res>` of the :ref:`print_settings_main`
      of the :ref:`print_settings` (there is any convention about it)
      
        **Example**: if you have a project called ``base``, a package called ``invoice``,
        a ``doctor`` table and in your :ref:`print_settings`
        ``html_res = 'html_builder/my_layout'``, then the path of the print layout file is::
        
            base/packages/invoice/resources/tables/doctor/html_builder/my_layout
            
        where "html_builder" is a folder, "my_layout" is the file name of the print layout file.
        
    This is a graphical map of the location of the print layout file into a :ref:`project`:
    
        *In this image the print layout file is called "custom_file";*
        *"html_res = 'custom_folder/custom_file'"*
    
    .. image:: ../../_images/print/print_layout_file.png
    
.. _print_layout_features:

layout page - features
======================

    add???
    
    LE STAMPE SI POSSONO FARE O IN MODALITA' SINGOLO RECORD, O IN MODALITA'
    TESTATA RIGHE (la TESTATA è chiamata DOC): documentare con immagini
    
    .. image:: BOH add??? an image with the graphical differences between doc - page - grid

.. _print_layout_import:

import
======

    To use the print layout file you have to import::
    
        from gnr.web.gnrbaseclasses import TableScriptToHtml
        
.. _print_layout_main:

Main class
==========

    The Main class inherits from the :class:`TableScriptToHtml
    <gnr.web.gnrbaseclasses.TableScriptToHtml>` class, so write::
    
        class Main(TableScriptToHtml):
        
    In the Main class you have to add some webpage variables:
    
.. _print_layout_webpage_variables:

webpage variables
=================

    .. note:: the unit of measurement of all these variables are in millimeters
              (e.g: ``print_width = 200`` means 200 millimeters)
              
    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize the layout. They belong to the :ref:`print_layout_main`.
    Let's see all of them:
    
    * :ref:`layout_copies_per_page`
    * :ref:`layout_copy_extra_height`
    * CSS style: :ref:`layout_css_requires`
    * debug tools: :ref:`layout_page_debug`
    * encoding and numerical formats: :ref:`layout_encoding`, :ref:`layout_currencyformat`
    * header and footer heights:
    
        * document: :ref:`layout_doc_header_height`, :ref:`layout_doc_footer_height`
        * grid: :ref:`layout_grid_header_height`, :ref:`layout_grid_footer_height`
        * page: :ref:`layout_page_header_height`, :ref:`layout_page_footer_height`
        
    * grid: :ref:`layout_grid_col_widths`, :ref:`layout_grid_row_height`
    * page bars: :ref:`layout_page_leftbar_width`, :ref:`layout_page_rightbar_width`
    * page dimensions: :ref:`layout_page_height`, :ref:`layout_page_width`
    * page margins: :ref:`layout_page_margin_top`, :ref:`layout_page_margin_left`,
      :ref:`layout_page_margin_right`, :ref:`layout_page_margin_bottom`
    * :ref:`layout_print_button`
    * rows: :ref:`layout_row_mode`, :ref:`layout_rows_path`
    * :ref:`layout_starting_page_number`
    * :ref:`layout_templates`
    
.. _layout_copies_per_page:

copies_per_page
---------------

    add???
    
.. _layout_copy_extra_height:

copy_extra_height
-----------------

    add???
    
.. _layout_css_requires:

css_requires
------------
    
    Allow to import :ref:`css` files. For more information, check the
    :ref:`webpages_css_requires` section
    
.. _layout_currencyformat:

currencyFormat
--------------

    Allow to specify the :ref:`table_format` of the numerical columns of the print
    
.. _layout_doc_footer_height:

doc_footer_height
-----------------

    add???
    
.. _layout_doc_header_height:

doc_header_height
-----------------

    add???
    
.. _layout_encoding:

encoding
--------

    Specify the encoding. By default it is::
    
        encoding = 'utf-8'
        
.. _layout_grid_col_widths:

grid_col_widths
---------------

    add???
    
.. _layout_grid_footer_height:

grid_footer_height
------------------

    add???
    
.. _layout_grid_header_height:

grid_header_height
------------------

    add???
    
.. _layout_grid_row_height:

grid_row_height
---------------

    add???
    
.. _layout_page_debug:

page_debug
----------

    add???
    
.. _layout_page_footer_height:

page_footer_height
------------------

    add???
    
.. _layout_page_header_height:

page_header_height
------------------

    add???
    
.. _layout_page_height:

page_height
-----------

    Set the print page height
    
.. _layout_page_leftbar_width:

page_leftbar_width
------------------

    add???
    
.. _layout_page_rightbar_width:

page_rightbar_width
-------------------

    add???
    
.. _layout_page_margin_bottom:

page_margin_bottom
------------------

    add???
    
.. _layout_page_margin_left:

page_margin_left
----------------

    add???
    
.. _layout_page_margin_right:

page_margin_right
-----------------

    add???
    
.. _layout_page_margin_top:

page_margin_top
---------------

    add???
    
.. _layout_page_width:

page_width
----------

    Set the print page width
    
.. _layout_print_button:

print_button
------------

    add???
    
.. _layout_row_mode:

row_mode
--------

    add???
    
.. _layout_rows_path:

rows_path
---------

    add???
    
.. _layout_starting_page_number:

starting_page_number
--------------------

    Define the starting page number
    
.. _layout_templates:

templates
---------

    A string with the names of the :ref:`html templates <htmltemplate>` separated by a comma.
    More information in the :ref:`add???` section of the :ref:`htmltemplate` page
    
.. _layout_building:
    
build the layout
================

    In this section we describe all the layout hook methods and all the elements that allow
    you to personalize the print.
    
    They are:
    
    * :ref:`layout_definestandardstyles`: allow to add???
    * :ref:`layout_docheader`: allow to add???
    * :ref:`layout_docfooter`: allow to add???
    * :ref:`layout_pageheader`: allow to add???
    * :ref:`layout_pagefooter`: allow to add???
    
    Inside these methods, you can create the layout through the following three methods:
    
    * the :ref:`layout_element`: allow to add???
    * the :ref:`layout_row`: allow to add???
    * the :ref:`layout_cell`: allow to add???
    
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
    
layout element
--------------

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.layout
    
    add???
    
.. _layout_row:
    
row element
-----------

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.row
    
    add???
    
.. _layout_cell:
    
cell element
------------

    .. automethod:: gnr.core.gnrhtml.GnrHtmlSrc.cell
    
    add???
    
.. _print_layout_onrecordexit:

onRecordExit
============

    .. automethod:: gnr.web.batch.btcprint.BaseResourcePrint.onRecordExit
    
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
        
        Il componente prende i dati da una tabella, ma se invece si vogliono passare dati con altro
        sistema si può ridefinire il metodo ``loadRecord``

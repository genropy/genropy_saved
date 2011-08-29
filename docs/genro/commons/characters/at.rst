.. _at_char:

=============
"@" character
=============

    *Last page update*: |today|
    
    * :ref:`at_intro`
    * :ref:`at_usage`
    * :ref:`at_examples`
    
.. _at_intro:

introduction
============
    
    You can build :ref:`relations` to create links between database tables.
    
    The "at" character (``@``) is the character used in Genro to start:
    
    * a :ref:`relation`
    * an :ref:`inverse_relation`
    * a :ref:`relation_path`
    
.. _at_usage:

list objects
============
    
    We list here all the elements that support the "@" character:
    
    * div (html)
    * :ref:`field`
    * :ref:`fieldcell`
    * add??? Other widgets, objects...
    
.. _at_examples:

examples
========

    **example**::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                pane = root.contentPane(margin='5px')    
                fb = pane.formbuilder(cols=2,border_spacing='6px',fld_width='15em',lbl_color='teal')
                
                add??? translate in english! correct it!
                
                fb.field('@anagrafica_id.nome',lbl='!!Name',validate_case='c')
                fb.field('@anagrafica_id.cognome',lbl='!!Surname',validate_case='c')
                fb.field('@anagrafica_id.email',lbl='!!Personal email',validate_email=True,
                          validate_email_error='!!Formato email non corretto')
                fb.field('@anagrafica_id.telefono',lbl='!!Personal phone')
                fb.field('@anagrafica_id.codice_fiscale',lbl='!!Personal tax code',validate_case='u')
                fb.field('@anagrafica_id.partita_iva',lbl='!!Personal VAT')
                fb.field('@anagrafica_id.fax',lbl='!!Personal fax')
                fb.field('interno')
                fb.field('azienda_id',lbl='!!Company name')
                fb.button('Show company data',action='genro.wdgById("info_azienda").show()',
                          visible='^aux.mostra_azienda')
                fb.field('ruolo',tag='combobox',lbl='Personal company role',colspan=2,
                          values='employee, freelancer, manager, owner')
                fb.field('@anagrafica_id.note',lbl='!!Notes', tag='simpletextarea', colspan=2, width='100%')
                
                dlg = pane.dialog(nodeId='info_azienda',title='COMPANY DATA')
                fb = dlg.formbuilder(cols=2,lbl_color='teal',margin='6px',fld_width='12em')
                fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='Phone')
                fb.div('^.@azienda_id.@anagrafica_id.email', lbl='Email')
                fb.div('^.@azienda_id.@anagrafica_id.indirizzo', lbl='Address')
                fb.div('^.@azienda_id.@anagrafica_id.cap', lbl='Postcode')
                fb.div('^.@azienda_id.@anagrafica_id.localita', lbl='Location')
                fb.div('^.@azienda_id.tipologia', lbl='Type')
                fb.div('^.@azienda_id.@anagrafica_id.partita_iva', lbl='VAT')
                fb.div('^.@azienda_id.@anagrafica_id.fax', lbl='Fax')
                fb.div('^.@azienda_id.@anagrafica_id.www', lbl='Web site')
                fb.button('Close',width='6em',action='genro.wdgById("info_azienda").hide()')
    
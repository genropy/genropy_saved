.. _print_settings:

===================
print settings file
===================

    *Last page update*: |today|
    
    * :ref:`print_settings_intro`
    * :ref:`print_settings_import`
    * :ref:`print_settings_main`
    * :ref:`print_settings_webpage_variables`
    * :ref:`the table_script_parameters_pane method
      <print_settings_table_script_parameters_pane>`
    * :ref:`print_settings_onrecordexit`
    * :ref:`print_settings_webpage`
    * :ref:`print_setting_dialog`
    * :ref:`print_setting_dialog_print_region`
    * :ref:`print_settings_location`
    * :ref:`example <print_settings_example>`
    
.. _print_settings_intro:
    
introduction
============

    The print settings file allows to specify the print settings. In particular,
    if you need to create some defined zone for your print, you have to use the
    :ref:`htmltemplate` (explained in the next page) that you can set in the
    print settings file through the :ref:`print_templates` webpage variable.
    
    In order to use it, you have to:
    
    * :ref:`print_settings_import` the correct module
    * create the :ref:`print_settings_main`
    
    In the Main class you have to:
    
    * add some :ref:`print_settings_webpage_variables`
    * create the :ref:`print_settings_table_script_parameters_pane` method (it handles the
      :ref:`print_setting_dialog` GUI)
      
    There is a specific location for the print settings file:
    
    * :ref:`print_settings_location`
    
    When you created it, you have to:
    
    * create a GUI to let the user starts the print (:ref:`print_settings_webpage`)
    
.. _print_settings_import:

import
======

    To use the print setting file you have to import::
    
        from gnr.web.batch.btcprint import BaseResourcePrint
        
    .. _print_settings_main:

Main class
==========

    The Main class inherits from the :class:`BaseResourcePrint
    <gnr.web.batch.btcprint.BaseResourcePrint>` class, so write::
    
        class Main(BaseResourcePrint):
        
    In the Main class you have to add some webpage variables:
    
.. _print_settings_webpage_variables:

webpage variables
=================

    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize your Main class. They are:
    
    * :ref:`print_html_res` (this is the only mandatory variable)
    * :ref:`print_batch_cancellable`
    * :ref:`print_batch_delay`
    * :ref:`print_batch_immediate`
    * :ref:`print_batch_prefix`
    * :ref:`print_batch_title`
    * :ref:`print_dialog_height`
    * :ref:`print_dialog_height_no_par`
    * :ref:`print_dialog_width`
    * :ref:`print_mail_address`
    * :ref:`print_mail_tags`
    * :ref:`print_templates`
    
.. _print_html_res:
    
html_res
--------
    
    MANDATORY. Specify the location path of the :ref:`print_layout`.
    The path you specify starts automatically from::
    
        projectName/packages/packageName/resources/tables/tableName/
        
    **Example**:
    
      if you write::
      
        html_res='html_builder/doctor_performances'
        
      then the location path of your print layout file must be::
      
         projectName/packages/packageName/resources/tables/tableName/html_builder/doctor_performances
         
      where ``html_builder`` is a folder created by you and ``doctor_performances``
      is the name of your print layout file.
      
.. _print_batch_cancellable:

batch_cancellable
-----------------

    add???
    
.. _print_batch_delay:

batch_delay
-----------
    
    A string with the time milliseconds start delay
    
.. _print_batch_immediate:

batch_immediate
---------------

    add???. Default value is ``False``
    
.. _print_batch_prefix:

batch_prefix
------------
    
    A string with a prefix for the batch name
      
      **Example**::
      
        batch_prefix = 'st_prest'
        
.. _print_batch_title:

batch_title
-----------
        
    A string with the :ref:`print_setting_dialog` title
    
.. _print_dialog_height:

dialog_height
-------------

    A string with the :ref:`print_setting_dialog` height
    
.. _print_dialog_height_no_par:

dialog_height_no_par
--------------------
    
    add???
    
.. _print_dialog_width:

dialog_width
------------

    A string with the :ref:`print_setting_dialog` width
    
.. _print_mail_address:

mail_address
------------
    
    Allow to send emails to the corresponding people that owns the data you want to
    print. For example, if you create a print with all the invoices of 10 doctors,
    you can choose to send an email to them with their relative invoices.
    
    The syntax is::
    
        mail_address = 'fieldName'
        
    where `fieldName` is the name of the field that contains the emails
    in the model :ref:`table`
    
.. _print_mail_tags:

mail_tags
---------

    Specify the authorization level to send emails. If the user has the same authorization
    level of the *mail_tags*, then he can use the :ref:`print_pdf_by_mail` and the
    :ref:`print_deliver_mails` panes in the :ref:`print_setting_dialog` : more information
    on :ref:`print_setting_dialog_print_region` section
    
.. _print_templates:

templates
---------
    
    A string with the names of the :ref:`html templates <htmltemplate>` separated by a comma.
    More information in the :ref:`add???` section of the :ref:`htmltemplate` page
    
.. _print_settings_table_script_parameters_pane:

``table_script_parameters_pane``
================================

    .. method:: table_script_parameters_pane(self, pane, **kwargs)
                
                **Parameters: pane** - it represents a :ref:`contentpane` through
                which you can attach your :ref:`webpage_elements_index`
    
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
============

    .. automethod:: gnr.web.batch.btcprint.BaseResourcePrint.onRecordExit
    
.. _print_settings_webpage:

webpage - start a print
=======================

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
====================

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
      
    We have already described most of the regions (follow the relative links).
    The only one that needs more explanations is the print region:
    
.. _print_setting_dialog_print_region:

print setting dialog - print region
===================================

    In the print regions you can swap up to 4 frames through a :ref:`radiobutton group
    <radiobutton>`:
    
    .. image:: ../_images/print/print_dialog_radiobuttons.png
    
    The 4 frames are:
    
    * :ref:`print_pdf`
    * :ref:`print_server_print`
    * :ref:`print_pdf_by_mail`
    * :ref:`print_deliver_mails`
    
    In particular, the third and the fourth frame can be used if the user has the same
    :ref:`authorization level <auth>` defined in the :ref:`print_mail_tags` webpage variable.
    
.. _print_pdf:
    
PDF
---

    .. image:: ../_images/print/print_pdf.png
    
    From this pane user can choose a name for the saved file and can choose through
    a :ref:`checkbox` to save the file in a zip format.
    
.. _print_server_print:

Server print
------------

    .. image:: ../_images/print/print_server_print.png
    
    From this pane user can choose the printer, the paper type and the tray.
    
.. _print_pdf_by_mail:

PDF by mail
-----------

    .. image:: ../_images/print/print_pdf_by_mail.png
    
    .. note:: this pane is accessible only by users that have required administration privileges.
              By default only users with 'admin' privileges can access to this (more information
              on authorizations management in the :ref:`auth` page). You can change the mail
              authorization level modifying the :ref:`mail_tags webpage variable <print_mail_tags>`.
              
    From this pane user can send the PDF by email.
    
.. _print_deliver_mails:

Deliver mails
-------------
    
    .. image:: ../_images/print/print_deliver_mails.png
    
    .. note:: this pane is accessible only by users that have required administration privileges.
              By default only users with 'admin' privileges can access to this (more information
              on authorizations management in the :ref:`auth` page). You can change the mail
              authorization level modifying the :ref:`mail_tags webpage variable <print_mail_tags>`.
              
    From this pane you can send emails to the same fields of the query used to get data in the
    database. This is made automatically (for this reason the ``TO`` field is hidden: the ``TO``
    recipient is filled with the emails of the query fields (add??? Explain how, explain better...)
    
.. _print_settings_location:

file location
=============
    
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
    
.. _print_settings_example:

print settings file - example
=============================
    
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
                
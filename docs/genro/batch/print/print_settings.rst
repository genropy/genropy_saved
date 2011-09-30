.. _print_settings:

===================
print settings file
===================

    *Last page update*: |today|
    
    **First steps**:
    
    * :ref:`print_settings_intro`
    * :ref:`print_settings_location`
    
    **File creation**:
    
    :ref:`print_settings_creation`:
    
    * :ref:`print_settings_import`
    * :ref:`print_settings_main`:
    
        * :ref:`print_settings_webpage_variables`
        * :ref:`main_class_methods`:
        
            * :ref:`table_script_parameters_pane() <print_settings_table_script_parameters_pane>`
            * :ref:`onRecordExit() <print_settings_onrecordexit>`
            
    **GUI**:
    
    * :ref:`print_settings_webpage`
    * :ref:`print_setting_dialog`:
    
        * :ref:`print_setting_dialog_title`
        * :ref:`print_setting_dialog_custom`
        * :ref:`print_setting_dialog_print`
        * :ref:`print_setting_dialog_notes`
        * :ref:`print_setting_dialog_bottom`
        
    **Examples**:
    
    * :ref:`print_settings_example`
    
    **Library reference**:
    
    * :ref:`settings_library`
    
.. _print_settings_intro:
    
introduction
============

    The print settings file allows to specify the settings of your print.
    
    * In the :ref:`print_settings_location` section we describe the specific location
      of the print settings file
      
    Once you created the file you have to:
    
    * import the correct module - :ref:`print_settings_import` section
    * create the Main class - :ref:`print_settings_main` section
    
    Inside the Main class you may customize your print through:
    
    * some variables - :ref:`print_settings_webpage_variables` section
    * some methods - :ref:`main_class_methods` section
    
    At last you have to:
    
    * create a GUI to let the user starts the print - :ref:`print_settings_webpage`
      section
      
    .. note:: if you need to create a letterhead in your print, you have to use also
              the :ref:`htmltemplate`. You can set it through the :ref:`"templates"
              webpage variable <baseresourceprint_templates>` of the print settings file
              
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
    * ``fileName`` is the name you choose for your print settings file
      (there is any convention about it)
    
    This is a graphical map of the location of the print settings file into a :ref:`project`:
    
    .. image:: ../../_images/print/print_settings_file.png
    
.. _print_settings_creation:
    
Creation of the file
====================
    
.. _print_settings_import:

import
------

    In order to use the settings functionalities you have to import in your print settings
    file the :class:`BaseResourcePrint <gnr.web.batch.btcprint.BaseResourcePrint>` class::
    
        from gnr.web.batch.btcprint import BaseResourcePrint
        
    Then we have to create the Main class:
    
.. _print_settings_main:

Main class
----------

    The Main class inherits from the :class:`BaseResourcePrint
    <gnr.web.batch.btcprint.BaseResourcePrint>` class, so write::
    
        class Main(BaseResourcePrint):
        
    In the Main class you have to add some webpage variables and some methods
    that allow to customize the settings file:
    
.. _print_settings_webpage_variables:

Main class webpage variables
----------------------------

    .. note:: the unit of measurement of all the numerical variables are in millimeters
              (e.g: ``print_width = 200`` means 200 millimeters)
              
    With the term ``webpages variables`` we mean that there are some defined variables
    belonging to the two parent classes (the ``BaseResourcePrint`` class and the
    ``BaseResourceBatch`` class) of the Main class that allow you to customize your
    print settings.
    
    We list here all these variables with a *short description about them*, specifying
    their parent class; if you need a more complete description, click on their name to
    go on their description section.
    
    List of the webpage variables of the :class:`BaseResourceBatch
    <gnr.web.batch.btcbase.BaseResourceBatch>` class:
    
    +------------------------------------------+---------------------------------------------------------+
    |  Name                                    |     Description                                         |
    +==========================================+=========================================================+
    | :ref:`batch_cancellable`                 |  add???                                                 |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_delay`                       |  the time milliseconds start delay batch                |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_note`                        |  add a note to the batch                                |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_prefix`                      |  the batch prefix                                       |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_steps`                       |  add???                                                 |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_thermo_lines`                |  add???                                                 |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`batch_title`                       |  the batch title                                        |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`base_dialog_height`                |  the dialog height. Its value is overridden by the      |
    |                                          |  "dialog_height" of the ``BaseResourcePrint`` class     |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`base_dialog_width`                 |  the dialog width. Its value is overridden by the       |
    |                                          |  "dialog_width" of the ``BaseResourcePrint`` class      |
    +------------------------------------------+---------------------------------------------------------+
    | :ref:`virtual_columns`                   |  add???                                                 |
    +------------------------------------------+---------------------------------------------------------+
    
    List of the webpage variables of the :class:`BaseResourcePrint
    <gnr.web.batch.btcprint.BaseResourcePrint>` class:
    
    +-----------------------------------------------+---------------------------------------------------------+
    |  Name                                         |     Description                                         |
    +===============================================+=========================================================+
    | :ref:`baseresourceprint_html_res`             |  MANDATORY. Specify the path of the :ref:`print_layout` |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_batch_immediate`      |  add???                                                 |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_dialog_height`        |  the dialog height                                      |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_dialog_height_no_par` |  add???                                                 |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_dialog_width`         |  the dialog width                                       |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_mail_address`         |  allow to send emails to the corresponding people       |
    |                                               |  that owns the data you want to print                   |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_mail_tags`            |  specify the authorization level needed by the customer |          
    |                                               |  to send emails                                         |
    +-----------------------------------------------+---------------------------------------------------------+
    | :ref:`baseresourceprint_templates`            |  specify the :ref:`html templates <htmltemplate>` names |
    +-----------------------------------------------+---------------------------------------------------------+
    
.. _main_class_methods:

Main class methods
------------------

    There are many methods you can use in the Main class. For a complete list, check
    the :ref:`settings_library`
    
    We describe here only the most relevant methods to perform a correct functioning
    of the print settings file:
    
    * the :ref:`table script parameters pane <print_settings_table_script_parameters_pane>`
      method
    * the :ref:`onRecordExit <print_settings_onrecordexit>` method
    
.. _print_settings_table_script_parameters_pane:

Main class method: table script parameters pane
-----------------------------------------------

    .. method:: table_script_parameters_pane(self, pane, **kwargs)
                
                Hook method. Allow to add some user customizable parameters
                
                In particular, allow to modify the :ref:`print_setting_dialog_custom` of
                the :ref:`print_setting_dialog` (in the following image, the region pointed
                with number "2")
                
                **Parameters: pane** - it represents a :ref:`contentpane` through
                which you can attach your :ref:`webpage_elements_index`
                
    *In the image, the print setting dialog. The point 2 is the "custom region",*
    *handled by the ``table_script_parameters_pane`` method*
        
    .. image:: ../../_images/print/print_settings_dialog_2.png
    
    **Example**: let's see the code relative to the previous image::
    
        def table_script_parameters_pane(self, pane, **kwargs):
            fb = pane.formbuilder(cols=2)
            self.periodCombo(fb,lbl='!!Period',period_store='.period')
            fb.div(value='^.period.period_string', font_size='.9em',font_style='italic')
            fb.checkbox(value='^.hideTemplate',label='!!Hide headers')
            
    We used the periodCombo in the example; for more information about it check the
    :ref:`periodcombo` page
    
.. _print_settings_onrecordexit:

Main class method: onRecordExit
-------------------------------

    .. automethod:: gnr.web.batch.btcprint.BaseResourcePrint.onRecordExit
    
.. _print_settings_webpage:

print GUI
=========

    .. note:: if you use the :ref:`th` component you have also a print management system.
              So, you don't need to create any GUI that allows user to start a print.
              Continue the reading of this section if you are not using the TableHandler
    
    To let the user starts a print from a :ref:`webpage`, you have to create 
    a :ref:`button` using the :ref:`action_attr` attribute that performs a :ref:`publish`.
    
    Create your button remembering that:
    
    * the first attribute is the button label
    * the *action* attribute must call a PUBLISH that follows this syntax::
    
        action = 'PUBLISH tablehandler_run_script="print", "fileName"'
        
    where:
    
    * "print" is the :ref:`tables_print` folder (so this is a default, you will have always
      "print" as parameter)
    * ``fileName`` is the name of your :ref:`print setting file <print_settings>` (without its extension)
    
    **Example**:
    
        If you created a print setting file called "printing_performance", then your button would be::
        
            class GnrCustomWebPage(object):
                def main(self, root, **kwargs):
                    pane = contentPane(height='300px', datapath='my_pane')
                    pane.button('New print',action='PUBLISH tablehandler_run_script="print","printing_performance";')
    
.. _print_setting_dialog:

print setting dialog
====================

    The print setting dialog is the dialog that represents the :ref:`print setting file
    <print_settings>` in the :ref:`webpage`:
    
    .. image:: ../../_images/print/print_settings_dialog.png
    
    It is divided in five regions (the numbers follow the image numbering):
    
    * (n.1): :ref:`print_setting_dialog_title`
    * (n.2): :ref:`print_setting_dialog_custom`
    * (n.3): :ref:`print_setting_dialog_print`
    * (n.4): :ref:`print_setting_dialog_notes`
    * (n.5): :ref:`print_setting_dialog_bottom`
    
.. _print_setting_dialog_title:

title region
------------
    
    It includes the window title, configurable through the :ref:`"batch_title" webpage
    variable <batch_title>`
    
.. _print_setting_dialog_custom:

custom region
-------------
    
    It can be configured through the :ref:`table script parameters pane
    <print_settings_table_script_parameters_pane>` hook method
    
.. _print_setting_dialog_print:

print region
------------

    It can be configured thorugh the :meth:`table_script_option_pane
    <gnr.web.batch.btcprint.BaseResourcePrint.table_script_option_pane>` method
    
    In the print regions you can swap up to 4 frames through a :ref:`radiobutton group
    <radiobutton>`:
    
    .. image:: ../../_images/print/print_dialog_radiobuttons.png
    
    The 4 frames are:
    
    * :ref:`print_pdf`
    * :ref:`print_server_print`
    * :ref:`print_pdf_by_mail`
    * :ref:`print_deliver_mails`
    
    In particular, the third and the fourth frame can be used if the user has the same
    :ref:`authorization level <auth>` defined in the :ref:`baseresourceprint_mail_tags`
    webpage variable
    
.. _print_pdf:
    
PDF
---

    .. image:: ../../_images/print/print_pdf.png
    
    From this pane user can choose a name for the saved file and can choose through
    a :ref:`checkbox` to save the file in a zip format.
    
.. _print_server_print:

Server print
------------

    .. image:: ../../_images/print/print_server_print.png
    
    From this pane user can choose the printer, the paper type and the tray.
    
.. _print_pdf_by_mail:

PDF by mail
-----------

    .. image:: ../../_images/print/print_pdf_by_mail.png
    
    .. note:: this pane is accessible only by users that have required administration privileges.
              By default only users with 'admin' privileges can access to this (more information
              on authorizations management in the :ref:`auth` page). You can change the mail
              authorization level modifying the :ref:`mail_tags webpage variable
              <baseresourceprint_mail_tags>`
              
    From this pane user can send the PDF by email.
    
.. _print_deliver_mails:

Deliver mails
-------------
    
    .. image:: ../../_images/print/print_deliver_mails.png
    
    .. note:: this pane is accessible only by users that have required administration privileges.
              By default only users with 'admin' privileges can access to this (more information
              on authorizations management in the :ref:`auth` page). You can change the mail
              authorization level modifying the :ref:`mail_tags webpage variable
              <baseresourceprint_mail_tags>`
              
    From this pane you can send emails to the same fields of the query used to get data in the
    database. This is made automatically (for this reason the ``TO`` field is hidden: the ``TO``
    recipient is filled with the emails of the query fields (add??? Explain how, explain better...)
    
.. _print_setting_dialog_notes:

notes region
------------

    It includes some notes of the print. You can set a defualt value through the
    :ref:`"batch_note" webpage variable <batch_note>`
    
.. _print_setting_dialog_bottom:

bottom region
-------------

    It includes a bottom pane with the ``Cancel`` and ``Confirm`` buttons: they respectively
    allow to:
    
    * cancel the print
    * execute the print
    
.. _print_settings_example:

a simple example
================
    
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
                
.. _settings_library:
                
print settings file - library reference
=======================================

    For the complete library reference, check:
    
    * the :class:`BaseResourceBatch <gnr.web.batch.btcbase.BaseResourceBatch>` class and
      its :ref:`webpage variables <btcbase_webpage_variables>`
    * the :class:`BaseResourcePrint <gnr.web.batch.btcprint.BaseResourcePrint>` class
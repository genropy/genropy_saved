.. _library_btcprint:

=============================
:mod:`gnr.web.batch.btcprint`
=============================
    
    *Last page update*: |today|
    
    **Classes:**
    
    * :ref:`btcprint_base`
    * :ref:`baseresourceprint_webpage_variables`
    
    **Complete reference:**
    
    * :ref:`btcprint_classes`
    
.. _btcprint_base:

:class:`BaseResourcePrint`
==========================

    .. module:: gnr.web.batch.btcprint.BaseResourcePrint
    
    ========================== ==================================== =========================================
    :meth:`do`                  :meth:`result_handler`              :meth:`table_script_fboptions`           
    :meth:`get_record_caption`  :meth:`result_handler_mail_deliver` :meth:`table_script_option_pane`         
    :meth:`onRecordExit`        :meth:`result_handler_mail_pdf`     :meth:`table_script_options_mail_deliver`
    :meth:`print_record`        :meth:`result_handler_pdf`          :meth:`table_script_options_mail_deliver`
    :meth:`print_selection`     :meth:`result_handler_server_print` :meth:`table_script_options_pdf`         
    ========================== ==================================== =========================================
    
.. _baseresourceprint_webpage_variables:

BaseResourcePrint - webpage variables
=====================================

    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize the class to which they belong (in this case, the
    BaseResourcePrint class). They are:
    
    * :ref:`baseresourceprint_batch_immediate`
    * :ref:`baseresourceprint_dialog_height`
    * :ref:`baseresourceprint_dialog_height_no_par`
    * :ref:`baseresourceprint_dialog_width`
    * :ref:`baseresourceprint_html_res`
    * :ref:`baseresourceprint_mail_tags`
    * :ref:`baseresourceprint_templates`
    
    templates = '' #CONTROLLARE
    mail_tags = 'admin'
    
.. _baseresourceprint_batch_immediate:

batch_immediate
---------------

    add???. Default value is ``False``
    
.. _baseresourceprint_dialog_height:

dialog_height
-------------

    A string with the :ref:`print_setting_dialog` height. Default value is ``300px``

.. _baseresourceprint_dialog_height_no_par:

dialog_height_no_par
--------------------
    
    add???. Default value is ``245px``
    
.. _baseresourceprint_dialog_width:

dialog_width
------------

    A string with the :ref:`print_setting_dialog` width. Default value is ``460px``
    
.. _baseresourceprint_html_res:

html_res
--------

    MANDATORY. Specify the location path of the :ref:`print_layout`. The root of the path you specify is::
    
        projectName/packages/packageName/resources/tables/tableName/
        
    **Example**:
    
      if you write::
      
        html_res='html_builder/doctor_performances'
        
      then the location path of your print layout file must be::
      
         projectName/packages/packageName/resources/tables/tableName/html_builder/doctor_performances
         
      where ``html_builder`` is a folder you created and ``doctor_performances`` is the name of your
      print layout file
      
.. _baseresourceprint_mail_address:

mail_address
------------
    
    Allow to send emails to the corresponding people that owns the data you want to
    print. It is mandatory that exists a column specified for the emails. Default value
    is ``None``
    
    For example, if you create a print with the invoices of 10 doctors,
    you can choose to send an email to them with their relative invoices.
    
    The syntax is::
    
        mail_address = 'fieldName'
        
    where `fieldName` is the name of the field that contains the doctors' emails
    in the database model :ref:`table`
    
.. _baseresourceprint_mail_tags:

mail_tags
---------

    Specify the authorization level needed by the customer to send emails
    
    If the user has the same authorization level of the *mail_tags* level, then he can use
    some additional options of the :ref:`print_setting_dialog` (the :ref:`print_pdf_by_mail`
    and the :ref:`print_deliver_mails`). Default value is ``admin``
    
    For more information, check the :ref:`print_setting_dialog_print` section
    
.. _baseresourceprint_templates:

templates
---------
    
    A string with the names of the :ref:`html templates <htmltemplate>` separated by a comma.
    More information in the :ref:`add???` section of the :ref:`htmltemplate` page

.. _btcprint_classes:

:mod:`gnr.web.batch.btcprint` - The complete reference list
===========================================================

.. automodule:: gnr.web.batch.btcprint
    :members:
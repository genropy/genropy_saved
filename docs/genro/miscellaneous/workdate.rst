.. _workdate:

========
workdate
========
    
    *Last page update*: |today|
    
    * :ref:`workdate_intro`
    * :ref:`workdate_th`
    
.. _workdate_intro:
    
introduction
============
    
    The working date.
    
    * The complete string is formed by...
    
        Example::
        
            Wed Oct 12 2011 00:00:00 GMT+0200 (CEST)
            
    CLIPBOARD::
    
        (e.g: ``MM/DD/YYYY``). The date format depends on the
        value of the *locale* parameter (add??? link to "locale"...)
        
.. _workdate_th:

workdate in TableHandler
========================

    * If you use the :ref:`th` as resource of your :ref:`webpages <webpage>`, then you can access
      to the *workdate* through the following path::
    
        gnr.workdate
        
      while user can modify it directly by clicking on the workdate button of the
      :ref:`TableHandler top bar <th_gui_view_top_bar>`
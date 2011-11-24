.. _print:

=====
print
=====
    
    *Last page update*: |today|
    
    * :ref:`print_intro`
    * :ref:`print_section_index`
    
.. _print_intro:

introduction
============

    In this chapter we learn about how to make a print in a :ref:`project`.
    
    In GenroPy a print is handled as a *resource script* of the :ref:`database tables <table>`.
    So, it can be easily personalized for every application.
    
    The prints can be handled through two files:
    
    * one file for the settings of the print (:ref:`print_settings`)
    * one file for the layout properties of the print (:ref:`print_layout`)
    
    There is also the possibility to create a letterhead in your print: to do this
    you can use the :ref:`htmltemplate`
    
    When you have created these two files, you have to create a GUI that allows the user to
    start a print. If you use the :ref:`th`, this process is auto handled by the component.
    For more information check the :ref:`print_settings_webpage` section
    
.. _print_section_index:

section index
=============
    
.. toctree::
    :maxdepth: 1
    :numbered:
    
    print_settings
    print_layout
    htmltemplate
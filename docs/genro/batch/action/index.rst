.. _action:

======
action
======

    *Last page update*: |today|
    
    * :ref:`action_intro`
    * :ref:`action_start`
    * :ref:`action_section_index`
    
.. _action_intro:

introduction
============

    add???
    
.. _action_start:

start an action
===============

    .. note:: if you use the :ref:`th` component you have also a "batch start" management
              system. So, you don't need to create any button that allows to start a batch.
              Continue the reading of this section if you are not using the TableHandler
              
    To start a batch from a :ref:`webpage`, you may create a :ref:`button` using the
    :ref:`action_attr` attribute that performs a :ref:`publish`.
    
    Create your button remembering that:
    
    * the first attribute is the button label
    * the *action* attribute must call a PUBLISH that follows this syntax::
    
        action = 'PUBLISH tablehandler_run_script="action", "fileName"'
    
    **Example**:
    
        add???
    
.. _action_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    
    action_batch
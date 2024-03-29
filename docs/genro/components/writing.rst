.. _components_writing:

===================
writing a component
===================
    
    *Last page update*: |today|
    
    * :ref:`writing_good_component`
    * :ref:`component_tutorial`
    
    Writing a component with GenroPy is easy: the framework allow to create a component
    in a simple way and allow to extract it from a page for an external usage

.. _writing_good_component:

how to create a good component
==============================

    If you want to create a good component you have to follow some useful tips:
    
    * **Document your public API:** please document your public API and keep updated the documentation.
      Remember also to keep updated:
      
        * the :ref:`cr`.
        * the documentation of all the callback functions (with their signatures and parameters).
        * The Bags or other complex objects used in your component.
        * The :ref:`datastore` elements and their functionality.
        * Its life cicle - that is, if your component changes its behavior over time, if it suggests an
          event (like a window dialog).
        
    * **Simple is better.** Creating a simple component is the key for a great component.
    * **Wrong parameter!** Your controller should have a "parameters validator", so that all the parameters
      that it receives will be checked [#]_.
    * **Use optional callback functions.** The component have to work even without callback functions.
      With this device a programmer is able to comment code lines during debugging, without causing
      further errors. Also, you can allow the user to learn progressively your component.

        If you have to use a mandatory callback, please introduce a good default behavior. For example,
        if a callback gives you some data to show on the screen, makes as default an empty view.
        
    * **Default parameters:** give default parameters for the mandatory parameters. It is better using
      specific classes for a component rather than Bags, so you can document all the class methods and
      attributes and during the debug you can use the documentation with WebError.
      
        Naturally, if you have some less-type data, you can use a :ref:`bag`.
        
    * **Use ``self`` sparingly.** Please avoid to use ``self`` to pass some parameters to (from) the
      controller (or even within the same component): the public namespace is already crowded. Moreover,
      raise the error probability.
      
        If the component has to mantain a condition, use a well defined and documented object.
        
        If you use some callbacks in a rpc or in a remote process, please allow the programmer to pass
        some additional data through some Bag's :ref:`resolvers <bag_resolver>` and allow him to add an
        ``user_data`` property to the object who control the controller status (so a programmer can
        attach its data). Deal the ``user_data`` content as a type-less content.
        
    * **Test your component in a blank page.** In this way you can verify if all the dependencies (like
      :ref:`webpages_py_requires`, :ref:`css_requires`, etc.) are correctly declared and you can
      verify the correct management of a lack of callbacks.
      
.. _component_tutorial:

tutorial: creation of a component
=================================

    TODO
      
**Footnotes:**

.. [#] Usually Python doesn't check the parameter's type, using the *duck typing* mode (if it walks as a duck and makes quack as a duck, so it is a duck). For a component it is not recommended to use the *duck typing* mode, because in case of an error it will be very difficult to find the key to the problem.

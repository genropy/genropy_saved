.. _packages_menu:

============
``menu.xml``
============

    * :ref:`menu_intro`
    * :ref:`menu_features`:
    
        * :ref:`features_basepath`
        * :ref:`features_tags`
        * :ref:`features_icons`
    
.. _menu_intro:

Introduction
============
    
    This XML file allows to create a menu for your project's :ref:`webpages_webpages`\s.
    
    If you have autocreated it [#]_, you will find this code::
        
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
        </GenRoBag>
    
    All you have to do is to fill the :ref:`genro_bag_intro` called ``<GenRoBag>`` with tags.
    Every :ref:`webpages_webpages` of your project has to fill a single tag. The syntax is::
    
        < tagName label='labelName' file='fileName' />
        
    Where:
    
    * ``tagName`` is the name of the tag (it is not important)
    * ``label=''`` includes the name of the menu voice
    * ``file=''`` includes the name of the related :ref:`webpages_webpages` file, without
      their extension (``.py``)
    
    Let's see an example::
    
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <companies label="Companies" file="companies"/>
            <staff label="Staff" file="staff"/>
            <contacts label="Contacts" file="contacts"/>
        </GenRoBag>
        
    This is the graphical result:
    
    .. image:: ../../images/structure/menu.png
    
    In this example you have only one folder, and ``Agenda`` is the name of your package.
    
.. _menu_features:

menu attributes
===============
    
.. _features_basepath:
    
basepath
--------

    **Definition**:
    
    The *basepath* is a tag attribute that allows to define the path of your webpages
    into the menu. It is required when you have more than one folder into the
    :ref:`packages_webpages` folder.
    
    **Syntax**::
    
        basepath="/packageName/webpageFolderName"
        
    Where:
    
    * ``packageName`` is the name of your package
    * ``webpageFolderName`` is the name of the webpage folder that contain your webpages
      
    **Example**:
    
    if you have a project called ``office`` with the following two ``webpages`` folders:
    
    * A folder called ``agenda`` with three webpages:
    
        * ``companies.py``
        * ``staff.py``
        * ``contacts.py``
        
    * A folder called "calendar" with two webpages:
    
        * ``recurrences.py``
        * ``admin.py``
    
    Then you will have to write::
    
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <agenda label='Agenda' basepath="/office/agenda" >
                <companies label="Companies" file="companies"/>
                <staff label="Staff" file="staff"/>
                <contacts label="Contacts" file="contacts"/>
            </agenda>
            <calendar label='Calendar' basepath="/office/calendar" >
                <recurrences label='Recurrences' file="recurrences"/>
                <administration label='Administration' file="admin"/>
            </calendar>
        </GenRoBag>
        
.. _features_tags:

tags
----

    If you have defined the :ref:`genro_permits`(add???) of your :ref:`webpages_webpages`,
    you can modify the menu view depending on the user permits: for doing this, you have
    to use the *tags* attribute.
    
    **Syntax**::
    
        tags="nameOfPermit"
        
    where ``nameOfPermit`` is the name of the permit, defined in the add???. For more
    information, please check the add??? documentation page.
    
    **Example**:
    
    We refers now to the example of the :ref:`features_basepath` section.
    
    If you want that the webpage called ``admin.py`` is viewed only by the users with 
    "admin" permits, you have to add the attribute ``tags="admin"`` to the
    <administration> tag and you have to add the ``tags="user"`` to the folder that
    includes the <administration> tag::
    
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <agenda label='Agenda' basepath="/office/agenda" >
                ...
            </agenda>
            <calendar label='Calendar' basepath="/office/calendar"
                      tags="staff"> <!-- "staff": allow every user to see this folder -->
                <recurrences label='Recurrences' file="recurrences"/>
                <administration label='Administration' file="admin"
                      tags="admin"/> <!-- "admin": only admin user will see this menu line -->
            </calendar>
        </GenRoBag>
    
.. _features_icons:
    
menu icons
----------
    
    add??? you can use the outcodes to add icons to your menu

**Footnotes**:

.. [#] To autocreate it, follows the instruction of the :ref:`packages_autofill` section.
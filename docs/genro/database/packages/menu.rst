.. _packages_menu:

============
``menu.xml``
============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/packages/menu.png
    
    * :ref:`menu_intro`
    * :ref:`menu_features`:
    
        * :ref:`features_basepath`
        * :ref:`features_tags`
        * :ref:`features_icons`
        
    * :ref:`menu_th`
    
.. _menu_intro:

Introduction
============
    
    This XML file allows to create a menu for your project's :ref:`webpages <webpages_webpages>`.
    
    If you have autocreated it (following the instructions of the :ref:`packages_autofill`
    section) you will find this code::
        
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
        </GenRoBag>
    
    All you have to do is to fill the :ref:`bag_intro` called ``<GenRoBag>`` with tags.
    Every :ref:`webpages_webpages` of your project has to fill a single tag. The syntax is::
    
        <tagName label='labelName' file='packageName/fileName' />
        
    Where:
    
    * ``tagName`` is the name of the tag (it doesn't appear on menu view)
    * ``label=''`` includes a string with the name of the menu voice
    * ``file=''`` includes a string with the name of the package in which the webpage is defined
      followed by the name of the related :ref:`webpages_webpages` file (without its ``.py``
      extension)
    
    .. note:: you can omit the ``packageName`` if the ``menu.xml`` is included in the same
              package folder of the webpages you're including in it.
    
    Let's see an example:
    
        **Example:**
        
        if you have a project with a package called ``office`` that includes three webpages
        called ``companies.py``, ``staff.py`` and ``contacts.py``:
        
        .. image:: ../../_images/projects/menu_example_1.png
        
        then your menu will be::
        
            <?xml version="1.0" encoding="UTF-8"?>
            <GenRoBag>
                <companies label="Companies" file="office/companies"/>
                <staff label="Staff" file="office/staff"/>
                <contacts label="Contacts" file="office/contacts"/>
            </GenRoBag>
            
        For what we have said in the previous note, you could also have written::
        
            <?xml version="1.0" encoding="UTF-8"?>
            <GenRoBag>
                <companies label="Companies" file="companies"/>
                <staff label="Staff" file="staff"/>
                <contacts label="Contacts" file="contacts"/>
            </GenRoBag>
            
        omitting the package name (``office``).
    
    There are many addictional attributes to improve your menu. In the next section we'll
    see them.
    
.. _menu_features:

menu attributes
===============
    
.. _features_basepath:
    
basepath
--------

    **Definition**:
    
    The *basepath* is a tag attribute that allows to define the path of your webpages
    into the menu *when they are grouped in folders*.
    
    **Syntax**::
    
        basepath="/packageName/webpageFolderName"
        
    Where:
    
    * ``packageName`` is the name of your package
    * ``webpageFolderName`` is the name of the webpage folder that contains your webpages
      
    **Example**:
    
    if you have a project called ``office`` with the following structure:
    
    .. image:: ../../_images/projects/menu_example_2.png
    
    so, in the :ref:`packages_webpages` folder you have:
    
    * A folder called ``agenda`` with three webpages:
    
        * ``companies.py``
        * ``staff.py``
        * ``contacts.py``
        
    * A folder called ``calendar`` with two webpages:
    
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
                <management label='Management' file="management"/>
            </calendar>
        </GenRoBag>
        
.. _features_tags:

tags
----

    If you have defined the permits [#]_ of your :ref:`webpages_webpages`, you can keep private
    some webpages according to the type of authorization. For example, you can create some pages
    visible only to developers and some pages visible only to the administrator.
    
    To do this, you have to use the *tags* attribute.
    
    **Syntax**::
    
        tags="authorizationTag"
        
    where ``authorizationTag`` is a string with the name of the permit, defined in the
    :ref:`instanceconfig_authentication` of the :ref:`instances_instanceconfig` file.
    For more information, please check the relative documentation page.
    
    **Example**:
    
    We refers now to the example of the :ref:`features_basepath` section.
    
    If you want that the webpage called ``management.py`` is viewed only by the users with
    "admin" permits, you have to add the attribute ``tags="admin"`` to the
    <management> tag and you have to add the ``tags="user"`` to the folder that
    includes the <management> tag::
    
        <?xml version="1.0" encoding="UTF-8"?>
        <GenRoBag>
            <agenda label='Agenda' basepath="/office/agenda" >
                ...
            </agenda>
            <calendar label='Calendar' basepath="/office/calendar" tags="user"> <!-- tags="staff": allow every
                                                                                     user to see this folder      -->
                <recurrences label='Recurrences' file="recurrences"/>
                <management label='Management' file="management" tags="admin"/> <!-- tags="admin": only admin
                                                                                     user will see this menu line -->
            </calendar>
        </GenRoBag>
        
    .. _features_icons:
    
menu icons
----------
    
    add??? you can use the outcodes to add icons to your menu

.. _menu_th:

menu lines for resource page of a TableHandler
==============================================

    If you have created some :ref:`resource pages <th_resource_page>`, then the tag line in the menu
    is a little different from the one for the normal webpages.
    
    In particular, the syntax of the tag is::
    
        <tagName label='labelName' table='packageName.fileName' />
        
    Where:
    
    * ``tagName`` is the name of the tag (it doesn't appear on menu view)
    * ``label=''`` includes a string with the name of the menu voice
    * ``table=''`` includes a string with the name of the package in which the resource
      page is defined followed by the name of the related resource page file
      (without its ``th_`` prefix and its ``.py`` extension)
      
        **Example:**
        
        Let's suppose to have a project called ``office`` with inside a package
        called ``office``.
        
        This package has two resource pages called ``th_development.py`` and
        ``th_management.py``:
        
        .. image:: ../../_images/projects/menu_example_3.png
        
        and three webpages called ``companies_page.py``, ``contacts_page.py``
        and ``staff_page.py``:
        
        .. image:: ../../_images/projects/menu_example_4.png
        
        then your menu can be::
        
            <?xml version="1.0" encoding="UTF-8"?>
            <GenRoBag>
                <development label="Development" table="office.development"/>
                <staff label="Staff" file="office/staff_page"/>
                <management label="Management" table="office.management"/>
                <companies label="Companies" file="office/companies_page"/>
                <contacts label="Contacts" file="office/contacts_page"/>
            </GenRoBag>
        
    .. note:: please notice the different split character (besides the attribute
              name) for a resource pages respect to a normal webpages:
              
              * normal webpage:
              
                * attribute name = file
                * split character = ``/`` (slash)
                
                Example::
                
                    <staff label="Staff" file="office/staff_page"/>
                
              * resource webpage:
              
                * attribute name = table
                * split character = ``.`` (dot)
                
                Example::
                
                    <staff label="Staff" table="office.staff"/>
                
**Footnotes**:

.. [#] You handle the permits through the :ref:`instanceconfig_authentication` tag of the :ref:`instances_instanceconfig` file
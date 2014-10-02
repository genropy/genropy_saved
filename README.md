Genropy
=======

Genropy framework. To complete the installation:
	
	sudo pip install paver
	
inside the folder **gnrpy** 

	sudo paver develop
	
for making the environment configuration 

	python initgenropy.py

Configuration files
===================
Configuration files are: 

	~/.gnr/environment.xml
	~/.gnr/instanceconfig/default.xml
	~/.gnr/siteconfig/default.xmli
	
**Projects**

	vi ~/.gnr/environment.xml

Inside *environment.xml* you can link the directories for your projects. The *initgenropy script creates an environment.xml that has 2 slots for projects one named 'genropy' that links 
genropy standard projects and packages (eg: gnrcore) and 'custom' for your projects.

	<projects>
		<genropy path="/home/genro/genropy/projects"/>
		<custom path="/home/genro/genropy_projects"/>
	</projects>

**Default for instances**

	vi ~/.gnr/instanceconfig/default.xml

Inside this file you can set all default parameters for every application instances of your installation. You can also set your default login as developer

	<authentication>
		<xml_auth defaultTags="user,xml">
			<admin pwd="......." tags="_DEV_,admin,user"/>
		</xml_auth>
	</authentication>

**Default for sites**

	vi ~/.gnr/instanceconfig/default.xml
	
Inside this file you can set all default parameters for every application site of your installation


First project: Hello world
=========================
The command *gnrmkproject* is the standard way to create a new project: 

	gnrmkproject --help

Normally you create a project and (with the option -P) also a main package.
You can also add one or more standard packages for the project with the option -A (eg: -A gnrcore:sys, gnrcore:adm)

With the special option --helloworld you can create your first project:

    gnrmkproject custom.myhelloworld -P mypackage -a  --helloworld
    
In this way a project **myhelloworld** is been created inside the **custom** folder of projects ("/home/genro/genropy_projects" in the standard environment.xml configuration), with a package **mypackage**, with instance and site configurations (-a option) and a simple example page inside the webpages folder of the main package.


Sandbox
=======
Sandbox is the application for learning Genropy framework. (Currently avaliable only in italian)

Inside folder genropy_projects 

	git clone https://github.com/genropy/sandbox.git

Genropy webapplications needs a daemon

Run inside another terminal

	gnrdaemon

Now we are ready for running **sandbox** website

	gnrwsgiserve sandbox
	
If you want to edit tutorial files through the application itself run **gnrwsgiserve** with **remote_edit** option

	gnrwsgiserve sandbox --remote_edit
	



License
=======

The code is licensed under the LGPL license::
    
    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.
    
    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Lesser General Public License for more details.
    
    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

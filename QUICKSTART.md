Dependencies
===========

**Python**

Being a Python Web framework, GenroPy requires Python. It works with Python  2.7. Python includes a lightweight database called SQLite so you won’t need to set up a database just yet.

Get Python at http://www.python.org. If you’re running Linux or Mac OS X, you probably already have it installed.

You can verify that Python is installed by typing python from your shell; you should see something like:

	Python 2.6.6 (r266:84292, Dec 26 2010, 22:31:48)
	[GCC 4.4.5] on linux2
	Type "help", "copyright", "credits" or "license" for 	more information.
	>>>

**Install Python Tools**
We need setuptools and pip

	sudo apt-get install python-setuptools
	sudo easy_install pip
	
**Databases**
Genropy's Sandbox project works with Sqlite. Anyway 
we strongly recommend to install and use PostgreSQL
http://www.postgresql.org/ for advanced works.


Genropy
=======
Now we are ready to install Genropy

To complete the installation:
	
	sudo pip install paver
	
inside the folder **gnrpy** 

	sudo paver develop
	
for making the environment configuration 

	python initgenropy.py

Configuration files are: 

	~/.gnr/environment.xml
	~/.gnr/instanceconfig/default.xml
	~/.gnr/siteconfig/default.xml

Change your development user by editing **~/.gnr/instanceconfig/default.xml**


Visit [www.genropy.org](http://www.genropy.org) for more information


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

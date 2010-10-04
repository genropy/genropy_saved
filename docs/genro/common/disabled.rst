==========
 Disabled
==========

Index
*****

	- Description_
	
	- Validity_
	
	- Default_
	
	- Examples_
	
		- "disabled" on a formbuilder_
		- "disabled" on a standardTable_

.. _Description:

**Description:**

	If True, user can't write in the object.

.. _Validity:

**Validity:** 

	It works on every form widget.

.. _Default:

**Default value:**

	False.

.. _Examples:

**Examples:**

.. _formbuilder:

	**"disabled" on a formbuilder**

	In the following example you can see the effect of the "disabled" attribute applied to the formbuilder: with checkbox you activate "disabled" attribute::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=root.formbuilder(datapath='test1',cols=3,fld_width='100%',width='100%',disabled='^disab')
				fb.checkbox(value='^disab',label='disable form')
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				fb.numberTextbox(value='^.age',lbl="Age")
				fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
				fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
				fb.textbox(value='^.job.profession',lbl='Job')
				fb.textbox(value='^.job.company_name',lbl='Company name')

	Let's see a demo:
     
	#NISO add online demo!
	
.. _standardTable:

	**"disabled" on a standardTable**
	
	In a standard table the "disabled" ??? continuare!! (spiegare del lucchetto)
	
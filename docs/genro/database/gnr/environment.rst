.. _gnr_environment:

===================
``environment.xml``
===================

	The ``environment.xml`` allow to define the root for your :ref:`genro_structure_mainproject` folders, that are:
	
	* the :ref:`genro_instances_index` folder
	* the :ref:`genro_packages_index` folder
	* the :ref:`genro_resources_index` folder
	* the :ref:`genro_sites_index` folder
	
	::

		<?xml version="1.0" encoding="UTF-8"?>
		<GenRoBag>
			<environment>
				<gnrhome value='~/sviluppo/genro' />
			</environment>
			<projects>
				<tutorial path="$GNRHOME/tutorial/projects" />
				<genro path="$GNRHOME/projects" />
				<miei path='~/sviluppo/progetti_miei' />
				<softwell path='~/sviluppo/softwell/projects' />
				<goodsoftware path="~/sviluppo/goodsoftware/projects" site_template='goodsoftware' />
				<progetti_softwell path="~/sviluppo/softwell"/>
			</projects>
			<packages>
				<genro path="$GNRHOME/packages"/>
				<legacy path="$GNRHOME/legacy_packages"/>
				<softwell path="~/sviluppo/softwell/packages"/>
			</packages>
			<static>'
				<js>
					<dojo_11 path="$GNRHOME/dojo_libs/dojo_11" cdn=""/>
					<dojo_15 path="$GNRHOME/dojo_libs/dojo_15" cdn=""/>
					<gnr_11 path="$GNRHOME/gnrjs/gnr_d11"/>
					<gnr_15 path="$GNRHOME/gnrjs/gnr_d11"/>
				</js>
			</static>
			<resources >
				<genro path="$GNRHOME/resources/"/>
				<goodsoftware path="~/sviluppo/goodsoftware/resources"/>
			</resources>
		</GenRoBag>
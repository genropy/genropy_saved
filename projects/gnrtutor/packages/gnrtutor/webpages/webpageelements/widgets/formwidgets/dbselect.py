# -*- coding: UTF-8 -*-
"""dbSelect"""

from tutorlib import example

class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"



    @example(code=1,height=350,description='Basic dbSelect')
    def dbSelect_1(self, pane):
        fb = pane.formbuilder(cols=3)
        fb.div("""In this test you can see the basic funcionalities of the dbSelect attribute:
                  the "dbtable" attribute allows to search from a database table, saving the
                  ID of the chosen record.""", colspan=3)
                  
        fb.div('saved in \"test/test_1_db/id\"')
        fb.dbSelect(dbtable='gnrtutor.person', value='^.id', limit=10)
        fb.div("""dbSelect default attributes: limit=10,
                                               hasDownArrow=False,
                                               ignoreCase=True""")
                                               
        fb.div('saved in \"test/test_1_db/id2\"')
        fb.dbSelect(dbtable='gnrtutor.person', value='^.id2', hasDownArrow=True)
        fb.div("""The hasDownArrow=True override the limit=10,
                  and let the user see all the entries""")



    def doc_dbSelect_1(self, pane):
        """
"""
    @example(code=2,height=350,description='\"auxColumns\" attribute')
    def dbSelect_2(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.div('With \"auxColumns\" attribute you let user see more columns during selection')
        fb.dbSelect(dbtable='showcase.person', value='^.person_id', hasDownArrow=True,
                    auxColumns='$nationality,$b_year')

    def doc_dbSelect_2(self, pane):
        """
"""

    @example(code=3,height=350,description='\"selected\" attribute')
    def dbSelect_3(self, pane):
        """\"selected\" attribute"""
        fb = pane.formbuilder()
        fb.div("""If you want to keep in the datastore some attributes of the chosen record
                  (in addition to the ID), you have to use the "selected" attribute""",colspan=3)
        fb.div("""In this example you get the column \"name\" and the column \"b_year\" and set
                  their value in a custom path. In particular we put the content of the
                  \"nationality\" column in \"test/test_3_selected/nationality\" and the
                  content of the \"b_year\" column in \"test/test_3_selected/year\". You can
                  see them in datastore (ctrl+shift+D), but you can see them even in the
                  two \"readOnly\" fields""",colspan=3)
        fb.dbSelect(lbl='Artist', dbtable='showcase.person', value='^.id',
                    selected_nationality='.nationality', selected_b_year='.year')
        fb.textbox(lbl='nationality', value='^.nationality', readOnly=True)
        fb.textbox(lbl='birth year', value='^.year', readOnly=True)

    def doc_dbSelect_3(self, pane):
        """
"""

    @example(code=4,height=350,description='\"condition\" attribute')
    def dbSelect_4(self, pane):
        fb = pane.formbuilder()
        fb.div("""If you have two or more database tables in relation,
                  you can allow the user to choose a record with a first "dbSelect"... """)
        fb.dbSelect(dbtable='showcase.person', value='^.person_id', lbl='Artist',
                    selected_name='.name', selected_b_year='.b_year')
        fb.div("""... and then you can make the user choose an attribute relative to the
                first record selected through a second dbSelect:""")
        fb.dbSelect(dbtable='showcase.person_music', value='^.music_id', lbl='Music',
                    condition='$person_id=:pid', condition_pid='=.person_id',
                    alternatePkey='music_id')

    def doc_dbSelect_4(self, pane):
        """
"""

    @example(code=5,height=350,description='\"columns\" attribute')
    def dbSelect_5(self, pane):
        fb = pane.formbuilder()
        fb.div("""The \"columns\" attribute allows user to search respect to all the fields
                  you specify in it. In this example we specify both \"name\" and \"nationality\",
                  so try to look for an actor respect its name or its nationality (you can try
                  \"Czech\", \"German\" or \"Austrian\", for example)""")
        fb.dbSelect(dbtable='showcase.person', value='^.value',
                    columns='$name,$nationality', auxColumns='$name,$nationality,$b_year,$d_year')

    def doc_dbSelect_5(self, pane):
        """
"""

    @example(code=6,height=350,description='\"hiddenColumns\" attribute')
    def dbSelect_6(self, pane):
        fb = pane.formbuilder()
        fb.div("""...""")
        fb.dbSelect(dbtable='showcase.person', value='^.value1',
                    columns='$name,$nationality', auxColumns='$name,$nationality')

    def doc_dbSelect_6(self, pane):
        """
"""
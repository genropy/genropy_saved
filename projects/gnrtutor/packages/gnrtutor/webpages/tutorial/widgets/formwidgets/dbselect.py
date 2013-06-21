# -*- coding: UTF-8 -*-
"""dbSelect"""

from tutorlib import example

class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"



    @example(code=1,height=150,description='Basic dbSelect')
    def dbSelect_1(self, pane):
        fb = pane.formbuilder(cols=1)
        fb.dbSelect(dbtable='imdb.role_type', value='^.role_type', lbl='Role',hasDownArrow=True)
        fb.dbSelect(dbtable='imdb.role_type', value='^.role_type', lbl='Role',hasDownArrow=True)


    def doc_dbSelect_1(self, pane):
        """
"""
    @example(code=2,height=350,description='\"auxColumns\" attribute')
    def dbSelect_2(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.div('With \"auxColumns\" attribute you let user see more columns during selection')
        fb.dbSelect(dbtable='gnrtutor.person', value='^.person_id', hasDownArrow=True,
                    auxColumns='$nationality,$birth_year')

    def doc_dbSelect_2(self, pane):
        """
"""

    @example(code=3,height=350,description='\"selected\" attribute')
    def dbSelect_3(self, pane):
        """\"selected\" attribute"""
        fb = pane.formbuilder()
        fb.div("""If you want to keep in the datastore some attributes of the chosen record
                  (in addition to the ID), you have to use the "selected" attribute""",colspan=3)
        fb.div("""In this example you get the column \"name\" and the column \"birth_year\" and set
                  their value in a custom path. In particular we put the content of the
                  \"nationality\" column in \"test/test_3_selected/nationality\" and the
                  content of the \"birth_year\" column in \"test/test_3_selected/year\". You can
                  see them in datastore (ctrl+shift+D), but you can see them even in the
                  two \"readOnly\" fields""",colspan=3)
        fb.dbSelect(lbl='Artist', dbtable='gnrtutor.person', value='^.id',
                    selected_nationality='.nationality', selected_birth_year='.year')
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
        fb.dbSelect(dbtable='gnrtutor.person', value='^.person_id', lbl='Artist',
                    selected_name='.name', selected_birth_year='.birth_year')
        fb.div("""... and then you can make the user choose an attribute relative to the
                first record selected through a second dbSelect:""")
        fb.dbSelect(dbtable='gnrtutor.person_music', value='^.music_id', lbl='Music',
                    condition='$person_id=:pid', condition_pid='=.person_id',
                    alternatePkey='music_id')

    def doc_dbSelect_4(self, pane):
        """This example shows the implementation of the condition attribute.
The 'where' condition is assigned to the condition attribute. In order to pass the parameters with
their values, we use the condition_myvar='datastorevalue' syntax.  This way we can use 'myvar' in the
contition statement.
"""

    @example(code=5,height=350,description='\"columns\" attribute')
    def dbSelect_5(self, pane):
        fb = pane.formbuilder()
        fb.div("""The \"columns\" attribute allows user to search respect to all the fields
                  you specify in it. In this example we specify both \"name\" and \"nationality\",
                  so try to look for an actor respect its name or its nationality (you can try
                  \"Czech\", \"German\" or \"Austrian\", for example)""")
        fb.dbSelect(dbtable='gnrtutor.person', value='^.value',
                    columns='$name_full,$nationality', auxColumns='$name_full,$nationality,$birth_year,$death_year')

    def doc_dbSelect_5(self, pane):
        """The \"columns\" attribute allows user to search respect to all the fields
you specify in it. In this example we specify both \"name\" and \"nationality\",
so try to look for an actor respect its name or its nationality (you can try
\"Czech\", \"German\" or \"Austrian\", for example)
"""
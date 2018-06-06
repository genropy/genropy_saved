# encoding: utf-8
def config(root,application=None):
    test15 = root.branch(u"!!Tests", tags="_DEV_",)
    test15.branch("Components", pkg="test15",dir='components')
    test15.branch("Dojo" ,pkg="test15",dir='dojo')
    test15.branch("Gnrwdg", pkg="test15",dir='gnrwdg')
    test15.branch("Dev tools", pkg="test15",dir='devtools')
    test15.branch("Tools", pkg="test15",dir='tools')
class GnrCustomWebPage(object):
    css_theme = 'textmate'
    
    def main_root(self, root, bpath='', **kwargs):
        self.createCss(root)
        root.data('gnr.windowTite', 'Dtatabase Structure')
        root.dataRemote('_dev.dbstruct', 'app.dbStructure')
        bc = root.borderContainer(height='100%', font_family='monaco')
        self.topPane(bc.contentPane(region='top', _class='tm_top'))
        tc = bc.tabContainer(region='center', margin='6px', background_color='white', font_size='.9em')
        for pkg in self.db.packages.values():
            self.packagePane(tc.borderContainer(title=pkg.name,
                                                datapath='packages.%s' % pkg.name), pkg)

    def topPane(self, pane):
        top = pane.div()
        top.div('Genropy', font_size='1.7em', color='white', margin='10px')

    def packagePane(self, bc, pkg):
        center = bc.contentPane(region='center', splitter=True, background_color='white')
        for table in pkg['tables'].values():
            center.dataRemote('.tree.%s' % table.name, 'relationExplorer', table=table.fullname, dosort=False)
        center.tree(storepath='.tree', persist=False,
                    inspect='shift', #labelAttribute='label',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
                    onDrag=self.onDrag(),
                    draggable=True,
                    dragClass='draggedItem',
                    onChecked=True,
                    selected_fieldpath='.selpath',
                    getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                    getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")


    def createCss(self, pane):
        pane.css('.tm_top', 'background-color:#801f78;')
        pane.css('#mainWindow', 'background-color:white;')
        pane.css('.tundra .dijitTreeContent', 'padding-top:0;min-height:17px;')
        pane.css('.tundra .dijitTreeExpando', 'height:16px;')

    def onDrag(self):
        return """var modifiers=dragInfo.modifiers;
                  var mode= (modifiers=='Shift') ? 'r.fieldcell':(modifiers=='Meta') ? 'fb.field':''
                  var children=treeItem.getValue()
                  if(!children){
                      var fieldpath=treeItem.attr.fieldpath;
                      dragValues['text/plain']=mode?mode+'("'+fieldpath+'")':fieldpath;
                      return
                  }
                   var cb;
                    cb=function(n){
                        var fieldpath=n.attr.fieldpath
                        return '        '+(mode?mode+'("'+fieldpath+'")':fieldpath);
                   };
                   result=[];
                   result.push('')
                   children.forEach(function(n){if (n.attr.checked){result.push(cb(n));}},'static');
                   result.push('')
                   dragValues['text/plain']= result.join(_lf); 
               """
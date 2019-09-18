# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import gzip
import shutil
from StringIO import StringIO
import pickle

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag, DirectoryResolver


class _StartupDataSaver(BaseComponent):
    "PRIVATE COMPONENT USED BY StartupDataManager"

    @struct_method
    def sd_startupDataSaver(self, parent, **kwargs):
        frame = parent.bagGrid(frameCode='sdata_saver', addrow=False, delrow=False,
                               storepath='.store',
                               struct=self.sd_table_saver_struct, **kwargs)

        bar = frame.top.bar.replaceSlots('#', '2,fb,10,savebtn,*,searchOn,5')
        fb = bar.fb.formbuilder(cols=2)
        if len(self.db.dbstores):
            fb.filteringSelect(value='^.current_storename',
                               lbl='!!Store', values=','.join(sorted(self.db.dbstores)))
        fb.filteringSelect(value='^.current_package',
                           lbl='Package',
                           values=','.join(self.application.packages.keys()))
        buildpars = []
        if self.isDeveloper():
            buildpars.append(dict(name='replace_default_startup',
                                  label='Replace default startup', tag='checkbox'))
        buildpars.append(dict(name='buildname', lbl='Name'))
        bar.savebtn.slotButton('!!Build startupdata',
                               ask=dict(title='Creating startup data',
                                        fields=buildpars),
                               _lockScreen=True,
                               action="""PUBLISH sd_buildStartupData = {replace_default_startup:replace_default_startup,buildname:buildname};""")
        frame.dataRpc('.store', self.sd_getStartupDataTables,
                      current_package='^.current_package',
                      current_storename='^.current_storename',
                      _if='current_package', _else='return new gnr.GnrBag()',
                      _onResult='FIRE .count_records')
        frame.dataRpc(None, self.sd_countRecords,
                      current_package='=.current_package',
                      current_storename='=.current_storename', _fired='^.count_records')
        frame.dataRpc(None, self.sd_buildStartupData, current_storename='=.current_storename',
                      current_package='=.current_package',
                      subscribe_sd_buildStartupData=True,
                      _onResult='PUBLISH sd_startupDataBuilt')
        frame.dataController("""
            store.getNodeByValue('_pkey',tblid).getValue().setItem('record_count',count);
        """, subscribe_sd_countRecords=True, store='=.store')

    def sd_table_saver_struct(self, struct):
        r = struct.view().rows()
        r.cell('tblid', hidden=True)
        r.cell('tblname', width='10em', name='!!Table')
        r.cell('record_count', calculated=True, width='6em',
               name='!!Count', dtype='L', format='#,###')
        r.cell('multidb', width='5em', name='!!Multidb')

    @public_method
    def sd_getStartupDataTables(self, current_package=None, **kwargs):
        result = Bag()
        tables = self.db.package(current_package).tables
        for i, tblid in enumerate(sorted(tables.keys())):
            tblobj = tables[tblid]
            tblattr = tblobj.attributes
            r = Bag()
            r['_pkey'] = tblobj.fullname
            r['tblname'] = tblobj.name
            r['multidb'] = tblattr.get('multidb')
            r['record_count'] = None
            result.setItem('r_%i' % i, r)
        return result

    @public_method
    def sd_countRecords(self, current_package=None, current_storename=None):
        with self.db.tempEnv(storename=current_storename or self.db.rootstore):
            tables = self.db.package(current_package).tables
            for tblobj in tables.values():
                tblid = tblobj.fullname
                self.clientPublish('sd_countRecords',
                                   tblid=tblid, count=tblobj.dbtable.countRecords())

    @public_method
    def sd_buildStartupData(self, current_package=None, current_storename=None,
                            buildname=None, replace_default_startup=None):
        basepath = None
        if not replace_default_startup:
            basepath = self.sd_getStartupDataFolder('datasets')
            buildname = buildname or (
                'from_%s' % current_storename if current_storename else 'ds_%i' % len(os.listdir(basepath)))
            folderpath = os.path.join(basepath, buildname)
            if not os.path.isdir(folderpath):
                os.makedirs(folderpath)
        with self.db.tempEnv(storename=current_storename or self.db.rootstore):
            self.db.package(current_package).createStartupData(
                os.path.join(folderpath, current_package))


class _StartupDataDbTemplates(BaseComponent):
    "PRIVATE COMPONENT USED BY StartupDataManager"

    @struct_method
    def sd_startupDataDbTemplates(self, parent, frameCode=None, **kwargs):
        bc = parent.borderContainer(**kwargs)
        self.sd_treeStartupSource(bc.framePane(region='left', width='500px',
                                               border_right='1px solid silver',
                                               splitter=True))
        self.sd_gridPreviewSource(bc.roundedGroup(
            title='Startup package content', region='center'))

    def sd_gridPreviewSource(self, pane):
        grid = pane.quickGrid('^.startup_preview')
        pane.dataRpc('.startup_preview', self.sd_getStartupPreview, bagpath='^.preview_path',
                     _if='bagpath', _else='return new gnr.GnrBag()')

    def sd_gridCurrentDbtemplates(self, frame):
        bc = frame.center.borderContainer()
        frame.dataRpc('.current_dbtemplates', self.sd_listDbTemplates, _onStart=True,
                      _fired='^.reload_current_dbtemplates')

        frame.dataRpc(None, self.sd_loadDbTemplate,
                      subscribe_sd_loadDbTemplate=True,_lockScreen=True)
        bottom = frame.bottom.slotToolbar('*,bottomUploader,*')
        bottom.bottomUploader.dropUploader(label='Upload',
                                           uploadPath=self.sd_startupdata_root(
                                               'dbtemplates'),
                                           onResult='FIRE .reload_current_dbtemplates')
        g = bc.contentPane(region='center').quickGrid('^.current_dbtemplates')
        g.column('caption', name='Template', width='100%')
        g.column('fileurl', name='Download', width='5em', format='download')
        g.column('run', name="Run", calculated=True, width='3em',
                 cellClasses='cellbutton',
                 format_buttonclass='run buttonIcon',
                 format_isbutton=True, format_onclick="""var row = this.widget.rowByIndex($1.rowIndex);
                                                      genro.publish('sd_loadDbTemplate', {filepath:row.filepath}); 
                                                      """,
                 _tags='_DEV_')

    def sd_treeStartupSource(self, frame):
        bar = frame.bottom.slotToolbar('*,saveDbTemplate,5')
        bc = frame.center.borderContainer()
        frame.dataRpc('.sources', self.sd_getStartupSource,
                      _onStart=True, subscribe_sd_startupDataBuilt=True,
                      _onCalling='SET .preview_path = null;')
        frame.dataRpc(None, self.sd_saveDbTemplate,
                      subscribe_sd_saveDbTemplate=True,
                      db_template_source='=.db_template_source',
                      _onResult='FIRE .reload_current_dbtemplates')

        self.sd_gridCurrentDbtemplates(bc.roundedGroupFrame(
            title='Current dbtemplates', region='top', height='200px'))

        bc.contentPane(region='center', overflow='auto').div(margin='5px').tree(storepath='.sources', _class='fieldsTree', hideValues=True,
                                                                                selected_abs_path='.preview_path',
                                                                                labelAttribute='file_name',
                                                                                selectedLabelClass='selectedTreeNode',
                                                                                onChecked="""return startupdata_manager.startupPackageChecked(this,node);""",
                                                                                margin='2px')
        grid = bc.roundedGroupFrame(title='!!New Template recipe', region='bottom',
                                    height='200px').quickGrid('^.db_template_source')

        grid.column('package', name='Package', width='7em')
        grid.column('filepath', name='Filepath', width='20em')

        bar.saveDbTemplate.slotButton('!!Save db template',
                                      action='PUBLISH sd_saveDbTemplate = {"template_name":template_name}',
                                      ask=dict(title='Save configuration as dbtemplate', fields=[dict(name='template_name',
                                                                                                      lbl='Name')]))

    @public_method
    def sd_getStartupSource(self):
        result = Bag()
        default_startups = Bag()
        result.setItem('_default_', default_startups,
                       caption='Standard startup data')

        for pkgid, pkgobj in self.application.packages.items():
            bagpath = os.path.join(
                self.db.application.packages[pkgid].packageFolder, 'startup_data')
            bagpath = '%s.gz' % bagpath
            if not os.path.isfile(bagpath):
                continue
            default_startups.setItem(
                pkgid, None, caption=pkgid, abs_path=bagpath, pkgid=pkgid, file_name=pkgid)
        sroot = self.sd_getStartupDataFolder('datasets')
        if os.path.exists(sroot):
            for folder in os.listdir(sroot):
                if not os.path.isdir(os.path.join(sroot, folder)):
                    continue
                result.setItem(folder, DirectoryResolver(
                    os.path.join(sroot, folder)), caption=folder)
        return result

    @public_method
    def sd_getStartupPreview(self, bagpath=None):
        data = None
        bagpath, ext = os.path.splitext(bagpath)
        if not os.path.isfile('%s.pik' % bagpath):
            if not os.path.exists('%s.gz' % bagpath):
                return
            with gzip.open('%s.gz' % bagpath, 'rb') as gzfile:
                pk = StringIO(gzfile.read())
                data = pickle.load(pk)
        else:
            data = Bag('%s.pik' % bagpath)
        result = Bag()
        for i, t in enumerate(data['tables']):
            row = Bag()
            row['table'] = t
            row['count'] = len(data[t])
            result['r_%s' % i] = row
        return result

    @public_method
    def sd_saveDbTemplate(self, db_template_source=None, template_name=None, **kwargs):
        tplpath = os.path.join(self.sd_getStartupDataFolder(
            'dbtemplates'), '%s.zip' % template_name)
        file_list = [(spath, '%s.gz' % pkg) for spath,
                     pkg in db_template_source.digest('#a.filepath,#a.package')]
        self.site.zipFiles(file_list=file_list, zipPath=tplpath)
        startup_data_root = self.sd_startupdata_root()
        dlurl = self.site.getStaticUrl(
            startup_data_root, 'dbtemplates', '%s.zip' % template_name, nocache=True)


class StartupDataManager(BaseComponent):
    js_requires = "startupdata_manager/startupdata_manager"
    py_requires = """gnrcomponents/framegrid:FrameGrid,
                   startupdata_manager/startupdata_manager:_StartupDataSaver,
                   startupdata_manager/startupdata_manager:_StartupDataDbTemplates"""

    def sd_getStartupDataFolder(self, *args):
        return self.site.getStaticPath(self.sd_startupdata_root(), *args, autocreate=True)

    def sd_startupdata_root(self, *args):
        return os.path.join(self.db.package('sys').attributes.get('startup_data_root') or 'site:startup_data', *args)

    @public_method
    def sd_listDbTemplates(self):
        result = Bag()
        startup_data_root = self.sd_startupdata_root()
        folderpath = self.sd_getStartupDataFolder('dbtemplates')
        for i, f in enumerate(os.listdir(folderpath)):
            filename, ext = os.path.splitext(f)
            if ext == '.zip':
                result.setItem('r_%i' % i, None, caption=filename,
                               filepath=os.path.join(folderpath, f),
                               fileurl=self.site.getStaticUrl(startup_data_root, 'dbtemplates', f))
        return result

    @public_method
    def sd_loadDbTemplate(self, filepath=None):
        extractpath = filepath.replace('.zip', '')
        if not os.path.isdir(filepath):
            from zipfile import ZipFile
            myzip = ZipFile(filepath, 'r')
            myzip.extractall(extractpath)
        prefrecord = self.db.table('adm.preference').loadPreference()
        if not prefrecord['__ins_ts']:
            self.db.table('adm.preference').insert(prefrecord)
            self.db.commit()
        for f in os.listdir(extractpath):
            pkg,ext = os.path.splitext(f)
            if pkg in self.db.packages:
                self.db.package(pkg).loadStartupData(
                    os.path.join(extractpath, pkg))
        shutil.rmtree(extractpath)
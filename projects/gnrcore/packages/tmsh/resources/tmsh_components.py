from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method

class TimeRuleView(BaseComponent):
    def th_struct(self,struct):
        r=struct.view().rows()
        self.paramentricView(r,deny_column=True)

    def paramentricView(self,r, deny_column = False):

        r.fieldcell('_row_count',name='Ord.', counter=True,width='3em')
        r.fieldcell('on_mo', width='22px', name='!![en]Mo') 
        r.fieldcell('on_tu', width='22px', name='!![en]Tu')
        r.fieldcell('on_we', width='22px', name='!![en]We')
        r.fieldcell('on_th', width='22px', name='!![en]Th')
        r.fieldcell('on_fr', width='22px', name='!![en]Fr')
        r.fieldcell('on_sa', width='22px', name='!![en]Sa')
        r.fieldcell('on_su', width='22px', name='!![en]Su')
        r.fieldcell('valid_from', width='6em', name='!![en]From')
        r.fieldcell('valid_to', width='6em', name='!![en]To')
        r.fieldcell('am_start_time', width='6em', name='!![en]In')
        r.fieldcell('am_end_time', width='6em', name='!![en]Out')
        r.fieldcell('pm_start_time', width='6em', name='!![en]In')
        r.fieldcell('pm_end_time', width='6em', name='!![en]Out')
        r.fieldcell('frequency_name', name='Freq', width='100%')
        if deny_column:
            r.fieldcell('deny', name='!!Deny',width='5em')

class ViewFromResource(TimeRuleView):
    def th_struct(self,struct):
        r = struct.view().rows()
        self.paramentricView(r, deny_column=True)
        


class TimeRuleForm(BaseComponent):

    def th_form(self, form):
        pane = form.record
        form.store.handler('save',waitingStatus=True)
        self.parametricForm(pane)

    def weekdaysForm(self,pane):
        pane.div('!!Weekdays',_class='pbl_roundedGroupLabel')
        pane.div('Weekdays the timerule applies',margin_left='1em',_class='gnrfieldlabel',margin_bottom='3px',
                                         text_decoration='underline',font_style='italic')

        fb = pane.formbuilder(cols=2,border_spacing='5px',width='100px')
        fb.field('on_mo',lbl='', label='!![en]Monday',label_class='gnrfieldlabel')
        fb.field('on_sa',lbl='', label='!![en]Saturday',label_class='gnrfieldlabel')
        fb.field('on_tu',lbl='', label='!![en]Tuesday',label_class='gnrfieldlabel')
        fb.field('on_su',lbl='', label='!![en]Sunday',label_class='gnrfieldlabel')
        fb.field('on_we',lbl='', label='!![en]Wednesday',label_class='gnrfieldlabel',colspan=2)
        fb.field('on_th',lbl='', label='!![en]Thursday',label_class='gnrfieldlabel',colspan=2)
        fb.field('on_fr',lbl='', label='!![en]Friday',label_class='gnrfieldlabel',colspan=2)
        fb.field('month_frequency', lbl='!!Freq.',
                  values='a:Any,1:First,2:Second,3:Third,4:Fourth,l:Last,w2:Every 2 weeks,w3:Every 3 weeks,w4:Every 4 weeks',
                  tag='filteringSelect',tooltip='Frequency in the month',colspan=2)

    def parametricForm(self,pane, is_exception=False):
        bc = pane.borderContainer()
        if not is_exception:
            self.weekdaysForm(bc.contentPane(region='right',_class='pbl_roundedGroup',margin='2px'))
        pane = bc.contentPane(region='center', _class='pbl_roundedGroup',margin='2px')

        pane.div('!![en]Rule description',_class='pbl_roundedGroupLabel')
        fb = pane.div(margin='5px').formbuilder(cols=2,border_spacing='5px',width='97%',fld_width='100%',lbl_width='6em')
        fb.field('deny', lbl='',label='!![en]Apply as deny rule', colspan=2,label_class='gnrfieldlabel')

        if is_exception:
            fb.field('valid_from',lbl='!![en]Date',colspan=2,validate_notnull=True)
        else:
            fb.field('valid_from', lbl='!![en]Valid From')
            fb.field('valid_to', lbl='!![en]Valid Until')


        fb.field('am_start_time', lbl='!![en]Start time 1',popup=False)
        fb.field('am_end_time', lbl='!![en]End time 1',popup=False)

        fb.field('pm_start_time',lbl='!![en]Start time 2',row_hidden='^.deny',popup=False)
        fb.field('pm_end_time', lbl='!![en]End time 2',popup=False)

        fb.simpleTextArea(value='^.notes',height='2.5em', lbl='!![en]Notes',colspan=2,lbl_vertical_align='top')

   #@public_method 
   #def th_onSaved(self,record,resultAttr):
   #    start_date = self.workdate-timedelta(30)
   #    start_date = date(start_date.year,start_date.month,1)
   #    end_date = date(start_date.year+1,start_date.month,1)
   #    self.db.table('tmsh.timerule').generateSlots(timerule_id=record['id'],start_date=start_date,
   #                                                         end_date = end_date)

    def th_options(self):
        tpl = '!![en]Time Rule $rule_order'
        newtpl = '!![en]New Time Rule'
        return dict(newTitleTemplate=newtpl,titleTemplate=tpl,dialog_height='280px',
                                dialog_width='600px')


class FormFromResource(TimeRuleForm):
    def th_form(self, form):
        pane = form.record
        form.store.handler('save',waitingStatus=True)
        self.parametricForm(pane)


class ExceptionForm(TimeRuleForm):
    def th_form(self, form):
        pane = form.record
        form.store.handler('save',waitingStatus=True)

        self.parametricForm(pane,is_exception = True)
        
    def th_order(self):
        return 'valid_from'


class ExceptionView(TimeRuleView):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True,hidden=True)
        r.fieldcell('valid_from', width='15em', name='!!Date',format_date='full')
        r.fieldcell('am_start_time', width='5.7em', name='!!In')
        r.fieldcell('am_end_time', width='5.7em', name='!!Out')
        r.fieldcell('pm_start_time', width='5.7em', name='!!In')
        r.fieldcell('pm_end_time', width='5.7em', name='!!Out')
        r.fieldcell('deny', name='!!Deny')
    

class TimeRuleEditor(BaseComponent):
    
    @struct_method
    def tmsh_timeRuleEditorDialog(self,pane,title=None,datapath=None,**kwargs):
        dlg = pane.dialog(title=title or '!![en]Time rules',parentRatio=.9,
                            datapath=datapath,closable=True,noModal=True)
        bc = dlg.borderContainer()
        top = bc.contentPane(region='top', height='50%')
        bottom = bc.contentPane(region='center')
        timerules_th = top.dialogTableHandler(relation='@tmsh_timerules',
                                formResource='tmsh_components:FormFromResource',
                                viewResource='tmsh_components:ViewFromResource',
                                condition='$is_exception IS NOT TRUE',
                                dialog_parentRatio=.9,
                                dialog_title='[en]Time rules',
                                margin='2px',pbl_classes=True) # 540px
        timerules_th.form.store.handler('load',default_rule_order ='=#FORM/parent.view.store?totalrows')
        timerules_th.view.grid.attributes.update(multiSelect=False,selfDragRows=True)
        exception_th = bottom.dialogTableHandler(relation='@tmsh_timerules',
                               datapath='.exceptions',
                               formResource='tmsh_components:ExceptionForm',
                                viewResource='tmsh_components:ExceptionView',
                               condition='$is_exception IS TRUE',
                               dialog_height='280px',
                               dialog_width='600px', # 540px
                               dialog_title='!![en]Exceptions',
                               title='!![en]Exceptions',
                               margin='2px',pbl_classes=True)
        exception_th.view.grid.attributes.update(multiSelect=False,selfDragRows=True)
        exception_th.form.store.handler('load',default_is_exception=True,
                                        default_rule_order ='=#FORM/parent.view.store?totalrows')
        return dlg

    @struct_method
    def tmsh_timeRuleEditorButton(self,pane,title=None,datapath=None,**kwargs):
        dlg = pane.timeRuleEditorDialog(title=title,datapath=datapath or '#FORM.timerule_editor',**kwargs)
        pane.button(label=title or '!![en]Edit Time rules',action='_dlg.show()',
                    _dlg=dlg.js_widget,parentForm=True)

        
class FullCalendar(BaseComponent):
    py_requires = 'th/th_lib'
    @extract_kwargs(condition=True)
    @struct_method
    def tmsh_timesheetStore(self,parent,relation=None,table=None,storepath=None,
                                condition=None,condition_kwargs=None,liveUpdate='*',**kwargs):
        if not storepath:
            storepath = parent.attributes.get('storepath')
        if relation:
            table,condition,fkeyfield = self._th_relationExpand(parent,relation=relation,condition=condition,
                        condition_kwargs=condition_kwargs,original_kwargs=kwargs)
        self.subscribeTable(table,True,subscribeMode=liveUpdate)
        rpcNode = parent.dataRpc(storepath,self.tmsh_getTimesheetEvents,table=table,
                    condition=condition,**condition_kwargs)
        parent.onDbChanges("""rpcNode.fireNode()""",rpcNode=rpcNode,table=table)

    @public_method
    def tmsh_getTimesheetEvents(self,table=None,condition=None,**kwargs):
        return self.db.table(table).fc_events(where=condition,**kwargs)
        

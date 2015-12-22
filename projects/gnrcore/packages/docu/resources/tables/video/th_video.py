#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('url')
        r.fieldcell('player_url')
        r.fieldcell('hosted_by')
        r.fieldcell('external_id')
        r.fieldcell('title')
        r.fieldcell('description')
        r.fieldcell('thumbnail_small')
        r.fieldcell('thumbnail_medium')
        r.fieldcell('thumbnail_large')
        r.fieldcell('duration')
        r.fieldcell('video_width')
        r.fieldcell('video_height')
        r.fieldcell('video_tags')

    def th_order(self):
        return 'url'

    def th_query(self):
        return dict(column='url', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        tc = form.center.tabContainer(margin='2px')
        info = tc.contentPane(title='Video Info',datapath='.record')
        fb = info.contentPane(region='top').div(margin_right='20px').formbuilder(cols=2, border_spacing='4px',fld_width='100%',colswidth='auto',width='100%')
        fb.field('title',colspan=2)
        fb.field('description',colspan=2)
        fb.field('url',colspan=2)
        fb.field('player_url',colspan=2)
        fb.field('hosted_by')
        fb.field('external_id')
        fb.field('thumbnail_small')
        fb.field('thumbnail_medium')
        fb.field('thumbnail_large')
        fb.field('duration')
        fb.field('video_width')
        fb.field('video_height')
        fb.field('video_tags',cols=2)
        self.videoCues(tc.borderContainer(title='Video Cues'))

    def videoCues(self,bc):
        thcues = bc.contentPane(region='right',width='40%',splitter=True).borderTableHandler(relation='@cues',
                                                                                    viewResource='ViewFromVideo',
                                                                                    formResource='FormFromVideo',
                                                                                    addrow=False)

        frame = bc.framePane(region='center')
        frame.dataController("SET .url=baseurl;",baseurl='^#FORM.record.url',
                            selected_cue_start='=.cue_start',
                            selected_cue_end='=.cue_end')

        
        video = frame.center.contentPane(overflow='hidden').video(src='^.url',height='100%',width='100%',
                                                                border=0,controls=True,nodeId='preview_video',
                                                                currentTime='^.currentTime')
        bar = frame.bottom.slotToolbar('2,play,stop,fbcurrtime,10,startcue,*')
        
        bar.play.slotButton(label='Play',action='_video.play()',_video=video.js_domNode)
        bar.stop.slotButton(label='Pause',action='_video.pause()',_video=video.js_domNode)
        fb = bar.fbcurrtime.formbuilder(cols=1,border_spacing='3px')
        fb.numberTextBox(value='^.currentTime',lbl='Time',format='###.00')
        bar.startcue.slotButton(label="==_start_time?'Make cue':'Start cue';",
                                _start_time='^.start_time',
                                action="""
                                if(_start_time){
                                    _video.pause();
                                    var end_time = _currentTime;
                                    SET .start_time=null;
                                    genro.publish('add_cue',{start_time:_start_time,end_time:end_time})
                                }else{
                                    SET .start_time = _currentTime;
                                }
                                """,_currentTime='=.currentTime',_video=video.js_domNode)
        thcues.view.dataController("""
            var wdg = [{lbl:'Name',value:'^.name'}];
            if(kinds.split(',').indexOf(kind)<0){
                kind = null;
                wdg.push({wdg:'filteringSelect',values:kinds,lbl:'Kind',value:'^.kind'});
            }
            var kw = {};
            kw.widget = wdg;
            kw.action = function(value){
                genro.serverCall(rpcmethod,{start_time:start_time,end_time:end_time,name:value.getItem('name'),
                                              kind:(kind || value.getItem('kind')),video_id:video_id});
            }
            genro.dlg.prompt('Add cue',kw)
            """,subscribe_add_cue=True,rpcmethod=self.addVideoCue,kind='=.sections.kind.current',
            kinds='metadata,chapters,captions,descriptions,subtitles',video_id='=#FORM.record.id')

    @public_method
    def addVideoCue(self,name=None,video_id=None,start_time=None,end_time=None,kind=None,**kwargs):
        self.db.table('docu.video_track_cue').insert(dict(video_id=video_id,name=name,kind=kind,start_time=start_time,end_time=end_time))
        self.db.commit()

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

dojo.declare('gnr.TimesheetViewerController',null,{
    constructor:function(sourceNode,kw){
        //this.data = data;
        
        this.date_start = kw.date_start;
        this.date_end = kw.date_end;
        this.work_start = kw.work_start ||0;
        this.work_end = kw.work_end || 24;
        this.day_duration = (this.work_end-this.work_start)*60;
        this.frameCode = kw.frameCode;
        this.rounded=4;
        this.changedDays = {};
        this.channel_width=20;
        this.sourceNode = sourceNode;
        this.slotFiller = objectPop(kw,'slotFiller');
        this.slot_duration = kw.slot_duration;
        this.minute_height = kw.minute_height || 1.3;

        this.max_slots = (this.work_end*60 - this.work_start*60)/this.slot_duration;

        if (this.slotFiller){
            if(this['slotFiller_'+this.slotFiller]){
                this.slotFiller = this['slotFiller_'+this.slotFiller];
            }else{
                this.slotFiller = funcCreate(this.slotFiller,'cellNode,date,dataNode',this);
            }
           
        }else{
            this.slotFiller = this.slotFiller_default;
        }
        var that = this;
        for(var k in kw){
            this[k] = kw[k];
        }
    },

    setData:function(data){
        var dataAttr = data.getParentNode().attr;
        this.data = data;
        this.channels = dataAttr.channels;
        this.colors = dataAttr.colors;
        
        if(this.colors){
            var bc = genro.getFrameNode(this.frameCode);
            var bottom = genro.getFrameNode(this.frameCode,'bottom');
            if(!bottom){
                return;
            }
            bottom = bottom.getValue();
            bottom.popNode('captions');
            var box = bottom._('div','captions',{position:'absolute',top:'2px',bottom:'2px',right:'50px'});
            var colors = this.colors;
            var fb = genro.dev.formbuilder(box,this.channels.length,{border_spacing:'5px'});

            this.channels.forEach(function(channel){
                fb.addField('div',{height:'20px',width:'20px',background:colors[channel],lbl:channel,lbl_padding_left:'50px'});
            });
        }
    },

    cal_sourceNode:function(){
        return genro.nodeById(this.frameCode+'_month_viewer');
    },

    day_sourceNode:function(){
        return genro.nodeById(this.frameCode+'_day_viewer');
    },


    setSizes:function(){        
        this.minutes_start = 0;
        this.tot_h = this.work_end-this.work_start; //24;
        this.m_hy_top = 20;
        this.m_hy_bottom = 10;
        this.m_header_h = 20;
        if(!this.cal_sourceNode()){
            return;
        }
        var calDomNode = this.cal_sourceNode().widget.domNode;
        this.m_dy = Math.floor((calDomNode.clientHeight-this.m_header_h-2)/6);
        this.m_dx = Math.floor((calDomNode.clientWidth-10)/7);
        this.m_sy = (this.m_dy-this.m_hy_top-this.m_hy_bottom)/(this.tot_h*60);
    },

    showMonthly:function(){
        this.setSizes();
        var cal_sourceNode = this.cal_sourceNode();
        if(!cal_sourceNode){
            return;
        }
        cal_sourceNode.freeze().clearValue();
        var currmonth = cal_sourceNode.getRelativeData('.selectedMonth');
        cal_sourceNode.setRelativeData('.selectedMonth',null);
        this.monthlyLayout(cal_sourceNode,this.data);
        cal_sourceNode.unfreeze();
        var that = this;
        this.month_redraw = {};
        setTimeout(function(){
            var date = that.sourceNode.getRelativeData('.selectedDate');
            cal_sourceNode.setRelativeData('.selectedMonth',currmonth);
            if(date){
                that.selectCalendarDate(date);
            }
        },1);
    },

    refresh:function(){
        this.setSizes();
        var currmonth,date,currPageName,firstDay;
        //var tc = sourceNode._('StackContainer',{position:'absolute',top:'2px',bottom:'2px',right:'2px',left:'2px',tabPosition:'left-h'});
        date = this.date_start;
        var calnode = this.cal_sourceNode();
        if(!calnode){
            return;
        }
        var sc = calnode.getValue();
        this.month_redraw = {};
        var selectedMonth= calnode.getRelativeData('.selectedMonth');
        while (date<this.date_end) {
            if(currmonth!=date.getMonth()){
                currmonth = date.getMonth();
                currPageName = 'm_'+currmonth;
                firstDay = new Date(date.getFullYear(),currmonth,1);
                if(selectedMonth==currPageName){
                    this.rebuildMonthPage(firstDay);
                }else{
                    this.month_redraw[currPageName]=firstDay;
                }
            }
            date = addDaysToDate(date,1);
        }
    },

    rebuildMonthPage:function(date){
        var calnode = this.cal_sourceNode();
        var sc = calnode.getValue();
        monthtitle = genro.format(date,{selector:'date',datePattern:'MMMM'});
        monthPane = sc.getNode(monthtitle);
        this.createMonthContent(monthPane.getValue(),date);
        var selectedDate = this.sourceNode.getRelativeData('.selectedDate');
        var that = this;
        setTimeout(function(){
            that.checkDay(that.getDayCell(selectedDate).getParentNode());
        },1);
    },

    monthlyLayout:function(sourceNode,data){
        var monthPane,currmonth,dayPane,date;
        //var tc = sourceNode._('StackContainer',{position:'absolute',top:'2px',bottom:'2px',right:'2px',left:'2px',tabPosition:'left-h'});
        var that = this;
        
        date = this.date_start;
        while (date<this.date_end) {
            if(currmonth!=date.getMonth()){
                currmonth = date.getMonth();
                monthPane = that.createMonth(sourceNode,date);
            }
            date = addDaysToDate(date,1);
        }


        //data.forEach(function(n){
        //    date = n.attr.day;
        //    if(currmonth!=date.getMonth()){
        //        currmonth = date.getMonth();
        //        monthPane = that.createMonth(sourceNode,date);
        //    }
        //    that.fillDay(that.getDayCell(date,monthPane),n.attr.slots,date);
        //});
    },

    createMonth:function(tc,date){
        var currmonth= date.getMonth();
        date = new Date(date.getFullYear(),currmonth,1);
        var title = genro.format(date,{selector:'date',datePattern:'MMMM'})
        var pane = tc._('ContentPane',title,{'title':title,pageName:'m_'+currmonth});
        pane.popNode('monthcontent');
        this.createMonthContent(pane,date);
    },
    
    createMonthContent:function(pane,date){
        var top,left,daypane,coords;
        var currmonth= date.getMonth();
        pane = pane._('div','monthcontent',{width:7*this.m_dx+'px',height:5*this.m_dy+'px',position:'relative',margin:'2px'});
        var week_rel_number;
        var pastDate;
        var headers=[];
        var that = this;
        var offset = 10;
        for (var i=0; i < 7; i++) {
            top = (i==0)?0:this.m_header_h+ (i-1)*this.m_dy;
            for (var k=0; k < 7; k++) {
                left = k*this.m_dx
                if(i==0){
                    headers.push(pane._('div','wd_'+k,{'position':'absolute',top:'1px',left:left+2+'px',
                                                    text_align:'center',background:'gray',color:'white',rounded:that.rounded,
                                                    width:this.m_dx-4+'px',height:this.m_header_h-2+'px',_class:'header_wd'}));
                                                    
                    continue;
                }
                week_rel_number = i-1;
                if (date.getMonth()==currmonth){
                    coords = this.getDayCoords(date);
                    if(week_rel_number==coords[0] && k==coords[1]){
                        if(!headers[k].getParentNode().attr.innerHTML){
                            if(headers[k].getParentNode().domNode){
                                headers[k].getParentNode().domNode.innerHTML = genro.format(date,{selector:'date',datePattern:'EEEE'});
                            }
                           headers[k].getParentNode().attr.innerHTML = genro.format(date,{selector:'date',datePattern:'EEEE'});
                        }
                        pastDate = date<genro.getData('gnr.workdate');
                        daypane = pane._('div',week_rel_number+'_'+k,{'position':'absolute',top:top+2+'px',left:left+2+'px',
                                        width:this.m_dx-4+'px',height:this.m_dy-4+'px',_class:'dayEmpty '+(pastDate?'pastDay':''),
                                        connect_onclick:function(e){
                                                var attr = e.target.sourceNode.getInheritedAttributes()
                                                that.selectCalendarDate(new Date(attr._year,attr._month,attr._day));
                                        },connect_ondblclick:function(e){
                                            var attr = e.target.sourceNode.getInheritedAttributes()
                                            that.selectCalendarDate(new Date(attr._year,attr._month,attr._day));
                                            that.sourceNode.setRelativeData('.viewerPage','dayViewer');
                                        }
                                        ,_day:date.getDate(),_month:date.getMonth(),_year:date.getFullYear()},
                                    );
                        daypane._('div',{innerHTML:date.getDate(),'position':'absolute',top:'3px',right:'3px',font_size:'12px',_class:'tw_monthday'});
                        var colpane = daypane._('div',{position:'absolute',top:offset+'px',bottom:'0',height:this.m_dy-4-offset+'px',left:'0px',width:this.m_dx-4+'px'});
                        that.fillDay(colpane,date);
                        date = new Date(date.getFullYear(),date.getMonth(),date.getDate()+1);
                    }
                }else{
                    return pane;
                }
            };
        };
        return pane;
    },
    fillFullDay:function(date){
        var sourceNode = this.day_sourceNode();
        var prevSlotContainer = sourceNode.getValue().getNode('slotContainer');
        var prevScrollRatio;
        if(prevSlotContainer && prevSlotContainer.domNode){
            prevSlotContainer = prevSlotContainer.domNode;
            prevScrollRatio = prevSlotContainer.scrollTop/(prevSlotContainer.scrollHeight-prevSlotContainer.clientHeight);
        }
        this.fillFullDay_draw(sourceNode,date);
        if(prevScrollRatio){
            var slotContainer = sourceNode.getValue().getNode('slotContainer');
            slotContainer.domNode.scrollTop = prevScrollRatio * (slotContainer.domNode.scrollHeight - slotContainer.domNode.clientHeight);
        }
        

    },

    commonDropTargetCb:function(dropInfo,data){
        var sn = dropInfo.sourceNode;
        if(sn && sn._slot &&sn._slot.event_id){
            return false;
        }
        return true;
    },

    getDropTime:function(y){
        var offset = dojo.coords(genro.nodeById('day_viewer')._value.getNode('slotContainer.slotBox').domNode).y;
        var y = y-offset;
        var minutes = 5*Math.floor(((y/slotsviewer.scale_y)+2.5)/5);
        var totminutes = slotsviewer.work_start*60+minutes;
        var sh = Math.floor(totminutes/60);
        var sm = totminutes-sh*60;
        return [sh,sm];
    },

    freeSpaceOnDrop:function(dropInfo,data){
        var ts = slotsviewer.getDropTime(dropInfo.event.clientY-data.event_drag_delta);
        var rec = {event_id:data.rec.event_id,start_time:slotsviewer.toStrTime(ts)+'::H'};
        rec['date'] = slotsviewer.currentDay;
        slotsviewer.updateEventWhen(rec);
    },

    updateEventWhen:function(kw){
        genro.lockScreen(true,'movingEvent');
        genro.serverCall('updateEventWhen',kw,function(err){
            genro.lockScreen(false,'movingEvent');
            if(err){
                alert(err);
            }
        });
    },
    setSelectedSlot:function(sourceNode){
        if(this.selectedSlotNode){
            genro.dom.removeClass(this.selectedSlotNode,'selectedSlot');
        }
        this.selectedSlotNode = sourceNode;
        genro.dom.addClass(this.selectedSlotNode,'selectedSlot');
        
    },

    fillSlotDetail:function(cell,slot,location_col,total_locations,date){
        var s_time = slot.s_time;
        var top,height;
        s_time = (s_time[0]-this.work_start)*60+s_time[1];
        top = s_time*this.scale_y;
        height = slot.duration*this.scale_y;
        var that = this;
        var slotAttr = {'position':'absolute',top:top+'px',height:height+'px',left:'5px',cursor:'pointer',right:'5px',
                           _class:'monthly_slot',z_index:100,dropTargetCb:this.commonDropTargetCb};
        if(slot.out_of_rules){
            slotAttr['_class'] = slotAttr['_class'] + ' out_of_rules';
        }
        var event_id = slot.event_id;
        var is_activity = slot.is_activity;

        var c = cell._('div',slotAttr);
        var contentAttr = {dropTargetCb:this.commonDropTargetCb}
        if('background_color' in slot){
            contentAttr['background'] = slot['background_color']
        }
        if('color' in slot){
            contentAttr['color'] = slot['color']
        }
        contentAttr.connect_ondblclick = function(e){
            if(!(is_activity || e.shiftKey)){
                genro.publish('edit_event',{event_id:event_id || false, evt_date:date, s_time:that.toStrTime(slot.s_time)+'::H',location_id:slot.location_id,referrer_id:slot.referrer_id});
            }else{
                genro.publish('edit_activity',{event_id:event_id || false, evt_date:date, s_time:that.toStrTime(slot.s_time)+'::H',location_id:slot.location_id,activity_location:slot.location_name});
            }
            dojo.stopEvent(e);
        }
        contentAttr.connect_onclick = function(e){
            var sn = genro.dom.getBaseSourceNode(e.target);
            if(sn){
                that.setSelectedSlot(sn.getParentNode());
            }
        };
        contentAttr._class = 'slotDetail freeslot';
        contentAttr.onDrop_eventSlot = this.freeSpaceOnDrop;
        var right = dataTemplate("<div class='loc_info'>$location_name ($referrer_name)</div>",slot);
        var left = dataTemplate("<div class='evt_info'>$notes</div>",slot);
        var rec = slot._evt_rec;
        if(rec){
            contentAttr.draggable=true;
            contentAttr._class = 'slotDetail busyslot eventSlot';
            //contentAttr.pkey = rec.pkey;
            contentAttr.onDrag = function(dragValues, dragInfo){
                dragValues['eventSlot'] = {is_activity:is_activity,rec:rec,
                                          event_drag_delta:dragInfo.event.clientY-dojo.coords(dragInfo.sourceNode.domNode).y};
            }  
            if (rec.cancelled ){
                contentAttr._class = contentAttr._class+' cancelledslot';
                contentAttr['background'] = 'gray';
                contentAttr['color'] = 'white';
            }
            if(is_activity){
                right = dataTemplate("<div class='loc_info'>$location_name</div>",rec);
                left = dataTemplate("<div class='evt_info'>$type_name - $evt_description</div>",rec);
            }
            else{
                right = dataTemplate("<div class='loc_info'>$location_name ($referrer_name)</div>",rec);
                left = dataTemplate("<div class='evt_info'>$patient_contact_link ($evt_description)</div>",rec);
            }
        }

        contentAttr.innerHTML = '<div class="slot_caption">'+left+right+'</div>';
        var sn = c._('div',contentAttr).getParentNode();
        if(!rec){
             var qb = sn._('div',{_class:'quickEntryButton',connect_onclick:function(e){dojo.stopEvent(e)}})
             qb._('span',{innerHTML:'Add Events',connect_onclick:function(e){
                dojo.stopEvent(e);
                genro.publish('event_quick_entry',{evt_date:date, s_time:that.toStrTime(slot.s_time)+'::H',e_time:that.toStrTime(slot.e_time)+'::H',
                    location_id:slot.location_id,referrer_id:slot.referrer_id,location_name:slot.location_name,referrer_name:slot.referrer_name});
             }});
        }
        sn._slot = slot;
    },

    toStrTime:function(t){
        return dojo.number.format(t[0],{pattern:'00'})+':'+dojo.number.format(t[1],{pattern:'00'});
    },

    fillFullSlot:function(cell,slot,kw){
        this.fillDay();
    },

    prepareTimeGrid:function(cell,tbox,minute_height){
        var hh_y = 30*minute_height;
        for (var i = this.work_start; i< this.work_end; i++) {
            //var c = i%2==0?i/2+':00':'';
            tbox._('div',{height:_px(hh_y)})._('div',{innerHTML:i+':00',text_align:'right',padding_right:'3px',color:'#666'})
            cell._('div',{height:_px(hh_y-1),border_top:'1px solid silver',_hh:i+':0',dropTargetCb:this.commonDropTargetCb,onDrop_eventSlot:this.freeSpaceOnDrop});
            tbox._('div',{height:_px(hh_y)})._('div',{innerHTML:'',text_align:'right',padding_right:'3px',color:'#666'})
            cell._('div',{height:_px(hh_y-1),border_top:'1px dotted silver',_hh:i+':30',dropTargetCb:this.commonDropTargetCb,onDrop_eventSlot:this.freeSpaceOnDrop});
        };
        return (((this.work_end-this.work_start)*60)-2)*minute_height;
    },

    checkDay:function(cell){
        if (this.checkedDay){
            genro.dom.removeClass(this.checkedDay.domNode,'checkedDay');
        }
        this.checkedDay = cell;
        genro.dom.addClass(this.checkedDay.domNode,'checkedDay');
    },
    
    selectCalendarDate:function(date){
        var cal_sourceNode = this.cal_sourceNode();
        var period_from = cal_sourceNode.getRelativeData('slots?period_from');
        var period_to = cal_sourceNode.getRelativeData('slots?period_to');
        cal_sourceNode.setRelativeData('.selectedDate',date)
        if(date<this.date_start || date>this.date_end){
            genro.fireEvent('reloadslots',true);
            return;
        }
        this.currentDay = date;
        cal_sourceNode.setRelativeData('.selectedMonth','m_'+date.getMonth())
        this.checkDay(this.getDayCell(date).getParentNode());
        this.fillFullDay(date);
    },


    fillFullDay_draw:function(sourceNode,date){
        var dataNode = this.data.getNode(_F(date,{pattern:'yyyy_MM_dd'},'D'));
        if(!dataNode){
            return;
        }
        var minute_height = this.minute_height || 1.3;
        sourceNode.freeze().clearValue();
        var header_container = sourceNode._('div',{background:'gray',position:'absolute',top:'0',left:'0',right:'0',height:'20px'});
        var headerNodeId = this.frameCode+'_day_viewer_header';
        var time_size = 40;
        var header = header_container._('div',{background:'gray',color:'white',_class:'header_wd',nodeId:headerNodeId,
                                                position:'absolute',top:'0',left:'0',right:'0',bottom:'0','left':'40px'})
        var container = sourceNode._('div','slotContainer',{background:'whitesmoke',
                                        position:'absolute',top:'20px',
                                        left:'0',right:'0',bottom:'0',
                                        onCreated:function(){
                                            genro.dom.setEventListener(this.domNode,'scroll',function(e){
                                                var hdn = genro.nodeById(headerNodeId).domNode;
                                                hdn.style.left = (time_size-e.target.scrollLeft)+'px';
                                            });
                                        },
                                        overflow:'auto'});
       


        var tbox = container._('div',{position:'absolute',top:'-6px',left:'0',width:time_size+'px',bottom:0,z_index:20});
        var that = this;
        var action = function(sn,editActivity){
                            if(sn.attr._cal_attr){
                                that.sourceNode.publish('edit_timesheet',sn.attr._cal_attr);
                            }else if(sn.attr._slot_attr){
                                that.sourceNode.publish('edit_slot',sn.attr._slot_attr);
                            }
                        }
        
        var box = container._('div','slotBox',{position:'absolute',top:'0',left:time_size+'px',right:0,bottom:0,
                                    dropTypes:'eventSlot',
                                    connect_ondblclick:function(e){
                                        var sn = genro.dom.getBaseSourceNode(e.target);
                                        while(!(sn.attr._cal_attr || sn.attr._slot_attr)){
                                            sn = sn.getParentNode();
                                        }
                                        action(sn,e.shiftKey);
                                    }});
        var timegrid_height = this.prepareTimeGrid(box,tbox,minute_height);
        var channelbox;
        if(this.channels){
            var n_channels = this.channels.length;
            var dataVal = dataNode.getValue();
            var cellcol;
            var that = this;
            var cellwidth = 150; //Math.floor((document.body.clientWidth-200)/n_channels);
            this.channels.forEach(function(channel,idx){
                var channelNode = dataVal.getNode(channel);
                header._('div',{position:'absolute',top:'0',bottom:'0',_class:'timesheet_channel_header channel_'+channel,
                        left:(2+idx*cellwidth)+'px',width:cellwidth+'px'})._('div',{innerHTML:channel});
                cellcol = box._('div',{position:'absolute',top:'0',
                                        height:timegrid_height+'px',_class:'timesheet_channel channel_'+idx,
                                        left:(2+idx*cellwidth)+'px',width:cellwidth+'px'});
                that.slotFiller(cellcol.getParentNode(),date,channelNode,minute_height,true);
            });
        }else{
            this.slotFiller(box,date,dataNode,minute_height,true);
        }
        sourceNode.unfreeze();
        return;
    },

    fillDay:function(cell,date){
        var dataNode = this.data.getNode(_F(date,{pattern:'yyyy_MM_dd'},'D'));
        if(!dataNode){
            return;
        }
        var minute_height = parseInt(cell.getParentNode().attr.height)/this.day_duration;
        if(this.channels){
            var n_channels = this.channels.length;
            var dataVal = dataNode.getValue();
            var cellcol;
            var that = this;
            var cellwidth = Math.floor((parseInt(cell.attributes()['width'])-5)/n_channels);
            this.channels.forEach(function(channel,idx){
                cellcol = cell._('div',{position:'absolute',top:'2px',bottom:'2px',_class:'timesheet_channel channel_'+idx,
                                        left:(2+idx*cellwidth)+'px',width:cellwidth+'px'});
                that.slotFiller(cellcol.getParentNode(),date,dataVal.getNode(channel),minute_height);
            });
        }else{
            this.slotFiller(cell,date,dataNode,minute_height);
        }
    },

    slotFiller_default:function(cellNode,date,dataNode,minute_height,dayview){

    },
    minutesFromStartWork:function(t){
        return t.getMinutes()+t.getHours()*60-this.work_start*60;
    },

    timeCoords:function(t0,t1,minute_height){
        var result = {};
        var start = this.minutesFromStartWork(t0); 
        var end = this.minutesFromStartWork(t1); 
        result.top =  start*minute_height+'px';
        result.height =  (end-start)*minute_height+'px';
        return result;
    },


    slotFiller_timetable:function(cellNode,date,dataNode,minute_height,dayview){
        //console.log('cellNode',);
        var tc;
        if(!(dataNode.attr.time_start || dataNode.attr.time_end)){
            return;
        }
        tc = this.timeCoords(dataNode.attr.time_start,dataNode.attr.time_end,minute_height);
        cellNode._('div',{top:tc.top,height:tc.height,position:'absolute',
                            left:'7px',
                            _cal_attr:objectUpdate({},dataNode.attr),
                            _class:'channel_slot channel_free',background:dataNode.attr.background});
        var busy = dataNode.getValue();
        if(busy && busy.len()){
            var that = this;
            busy.forEach(function(n){
                tc = that.timeCoords(n.attr.time_start,n.attr.time_end,minute_height);
                var content = cellNode._('div',{top:tc.top,height:tc.height,position:'absolute',
                                                left:'7px',_class:'channel_slot channel_busy',
                                                color:n.attr.color,background_color:dayview?null:n.attr.background_color,
                                                _slot_attr:objectUpdate({},n.attr)});
                if(dayview){
                    var kw = objectUpdate({},n.attr);
                    var template = objectPop(kw,'template');
                    var background = n.attr.background_color;
                    var foreground = n.attr.color;
                    if(background && !foreground){
                        foreground = chroma.contrast((background),"white")>chroma.contrast((background),"#444")?"white":"#444";
                    }
                    content._('div',{innerHTML:dataTemplate(template,kw),background_color:background,color:foreground,
                                    position:'absolute',top:'2px',left:'2px',right:'2px',bottom:'0px',rounded:4});
                }
            });
        }
    },

    
    fillSlot:function(cell,slot,location_col,total_locations){
        var s_time = slot.s_time;
        var top,height;
        s_time = (s_time[0]-this.work_start)*60+s_time[1]-this.minutes_start;
        top = s_time*this.m_sy+this.m_hy_top;
        height = slot.duration*this.m_sy;
        var event_id = slot.event_id;
        var is_activity = slot.is_activity;
        var that = this;
        var width = (this.m_dx-4-4*(total_locations-1+2))/total_locations;
        var left = 4+location_col*(width+4);
        var slotAttr = {'position':'absolute',top:top+'px',height:height+'px',left:left+'px',cursor:'pointer',
                            width:width+'px',_class:'monthly_slot freeslot'};
        if(event_id){
            slotAttr._class = 'monthly_slot busyslot'
            if (slot._evt_rec.cancelled){
                slotAttr.background_color = 'gray';

            }
        }
        if('background_color' in slot){
            slotAttr['background'] = slot['background_color']
        }
        if('color' in slot){
            slotAttr['color'] = slot['color']
        }
        cell._('div',slotAttr);
    },
    
    getDayCoords:function(date){
        var weekday = date.getDay();
        weekday = weekday==0? 6:weekday-1;
        var monthday = date.getDate()-1;
        var row = Math.floor(monthday/7);
        row = (weekday - monthday%7<0)?row+1:row;
        return [row,weekday];
    },

    getDayCell:function(date,monthpane){
        var pane = monthpane || this.getMonthPane(date);
        var coords = this.getDayCoords(date);
        var dayPane = pane.getItem(coords[0]+'_'+coords[1]);
        return dayPane;
    },

    getMonthPane:function(date){
         var result =  this.cal_sourceNode()._value.getItem(genro.format(date,{selector:'date',datePattern:'MMMM'}));
         return result.getItem('#0');
    },

    rebuildDayCell:function(date,slots){
        var c = this.getDayCell(date);
        c.clear(true);
        var t = c.getParentNode();
        t._('div',{innerHTML:date.getDate(),'position':'absolute',top:'5px',right:'5px',font_size:'10px'});
        this.fillDay(c,slots,date);
        if(this.checkedDay && c.getParentNode()._id==this.checkedDay._id){
            this.fillFullDay(date); 
        }
    },

    onEventChange:function(changelist){
        var that = this;
        var changedDays = this.changedDays;
        var current_doctor_id = genro.getData('current.doctor_id');
        dojo.forEach(changelist,function(c){
            if(c.doctor_id!=current_doctor_id){
                return;
            }
            if(c.old_evt_date){
                changedDays[convertToText(c.old_evt_date)[1]] = c.old_evt_date;        
            }
            changedDays[convertToText(c.evt_date)[1]] = c.evt_date;
        });
        var that = this;
        var cal_sourceNode = this.cal_sourceNode();
        cal_sourceNode.watch('isWindowVisible',function(){
            return genro.dom.isWindowVisible();
        },function(){
            changedDays = that.changedDays;
            that.changedDays = {};
            that.fixDates(changedDays);
        });
        
    },

    fixDates:function(dates){
        if(objectNotEmpty(dates)){
            var dates = objectValues(dates);
            var dates_converted = dates.map(function(n){return asTypedTxt(n,'D')});
            var that = this;
            genro.serverCall('getDatesSlots',{dates:dates_converted},function(result){
                var daylist = ['mo','tu','we','th','fr','sa','su'];
                dates.forEach(function(day){
                    var rn = that.getDateDataNode(day,result);
                    var dn = that.getDateDataNode(day);
                    if(!dn){
                        var kw = rn?rn.attr:{};
                        kw.day = kw.day || day;
                        kw.slots = kw.slots || [];
                        kw.weekday = kw.weekday || daylist[day.getDay()];
                        dn = that.data().setItem('r_'+genro.getCounter(),null,kw);
                    }else{
                        dn.attr.slots = rn?rn.attr.slots:[];
                    }
                    that.rebuildDayCell(day,dn.attr.slots);
                });
            });
        }
    },

    getDateDataNode:function(date,bag){
        var result = null;
        bag = bag || this.data;
        bag.walk(
            function(n){
                var day = n.attr.day;
                if( day.getMonth()==date.getMonth() && day.getDate()==date.getDate() ){
                result = n;
                return false;
            }
        });
        return result;
    },

    onOver:function(e){
        var sn = genro.dom.getBaseSourceNode(e.target);
        if(sn){
            var sn = sn.attributeOwnerNode('_day');
            if(!sn){
                return;
            }
            var attr = sn.attr;
            if( (this.currentDay.getDate()==attr._day) && (this.currentDay.getMonth()==attr._month) && (this.currentDay.getFullYear()==attr._year)){
                return;
            }
            if(this.overDateAttr===attr){
                if((new Date()-this.overTS)>2000){
                    this.selectCalendarDate(new Date(attr._year,attr._month,attr._day));
                    this.overDateAttr = null;
                    this.overTS = null;
                }
                return;
            }
            this.overDateAttr = attr;
            this.overTS = new Date();
        }
    }
});
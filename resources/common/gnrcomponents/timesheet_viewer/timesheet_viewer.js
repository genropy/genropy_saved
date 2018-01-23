dojo.declare('gnr.TimesheetViewerController',null,{
    constructor:function(sourceNode,kw){
        //this.data = data;
        
        this.date_start = kw.date_start;
        this.date_end = kw.date_end;
        this.time_start = kw.time_start ||0;
        this.time_end = kw.time_end || 24;
        this.frameCode = kw.frameCode;
        this.rounded=4;
        this.changedDays = {};
        this.sourceNode = sourceNode;
        this.slotFiller = objectPop(kw,'slotFiller');
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
    },

    cal_sourceNode:function(){
        return genro.nodeById(this.frameCode+'_month_viewer');
    },

    day_sourceNode:function(){
        return genro.nodeById(this.frameCode+'_day_viewer');
    },


    setSizes:function(){
        this.scale_y = (24*0.8)/(this.work_end-this.work_start);
        
        this.minutes_start = 0;
        this.tot_h = this.work_end-this.work_start; //24;
        this.m_hy_top = 20;
        this.m_hy_bottom = 10;
        this.m_header_h = 20;
        var calDomNode = this.cal_sourceNode().widget.domNode;
        this.m_dy = Math.floor((calDomNode.clientHeight-this.m_header_h-2)/6);
        this.m_dx = Math.floor((calDomNode.clientWidth-10)/7);
        this.m_sy = (this.m_dy-this.m_hy_top-this.m_hy_bottom)/(this.tot_h*60);
        this.cal_sourceNode().setRelativeData('.scale_y',this.scale_y) ;

    },

    showMonthly:function(){
        this.setSizes();
        var cal_sourceNode = this.cal_sourceNode();
        cal_sourceNode.freeze().clearValue();
        this.monthlyLayout(cal_sourceNode,this.data);
        cal_sourceNode.unfreeze();
        var that = this;
        setTimeout(function(){
            that.selectCalendarDate(that.sourceNode.getRelativeData('.selectedDate'));
        },1);
    },

    refresh:function(){
        this.setSizes();
        var currmonth,date,currPageName,firstDay;
        //var tc = sourceNode._('StackContainer',{position:'absolute',top:'2px',bottom:'2px',right:'2px',left:'2px',tabPosition:'left-h'});
        date = this.date_start;
        var calnode = this.cal_sourceNode();
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
        headers=[]
        var that = this;
        for (var i=0; i < 7; i++) {
            top = (i==0)?0:this.m_header_h+ (i-1)*this.m_dy
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
                        daypane._('div',{innerHTML:date.getDate(),'position':'absolute',top:'5px',right:'5px',font_size:'10px'});
                        date = new Date(date.getFullYear(),date.getMonth(),date.getDate()+1);
                        that.fillDay(daypane,date);
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
        if(prevSlotContainer){
            prevSlotContainer = prevSlotContainer.domNode;
            prevScrollRatio = prevSlotContainer.scrollTop/(prevSlotContainer.scrollHeight-prevSlotContainer.clientHeight);
        }
        this.fillFullDay_draw(sourceNode,date);
        if(prevScrollRatio){
            var slotContainer = sourceNode.getValue().getNode('slotContainer');
            slotContainer.domNode.scrollTop = prevScrollRatio * (slotContainer.domNode.scrollHeight - slotContainer.domNode.clientHeight);
        }
        

    },

    fillFullDay_draw:function(sourceNode,date){
        console.log('fillFullDay_draw',sourceNode,date);
        return;
        var node = this.getDateDataNode(date);
        var slots = node?node.attr.slots:[];
        sourceNode.freeze().clearValue();
        var that = this;
        var kw,slots;
        var n_locations = 0;
        var locations = {};
        var location_names = [];
        this.location_columns = false;
        var h_height = this.location_columns?45:25;
        var header = sourceNode._('div',{background:'white',position:'absolute',top:'0',left:'0',right:'0',height:_px(h_height),background:'gray',color:'white',_class:'header_wd'});
        header._('div',{'innerHTML':genro.formatter.asText(date,{format:'full'}),text_align:'center',font_size:'11pt',color:'white',margin_top:'3px'});
        if(this.location_columns){
            dojo.forEach(slots,function(slot){
                if(!(slot.location_id in locations)){
                    locations[slot.location_id] = n_locations;
                    location_names.push(slot.location_name);
                    n_locations++;
                }
            }); 
            var header_loc = header._('table',{width:'100%',border_collapse:'collapse',border:0,margin_left:'40px',margin_top:'3px'})._('tbody')._('tr');
            var w = (500-10-10*(n_locations-1+2))/n_locations;
            location_names.forEach(function(n){
                header_loc._('td')._('div',{innerHTML:n,text_align:'center',background:'gray',color:'white',rounded:that.rounded,width:w+'px',_class:'header_wd'})
            })
        }

        var container = sourceNode._('div','slotContainer',{background:'whitesmoke',
                                        position:'absolute',top:_px(h_height),left:'0',right:'0',bottom:'0',overflow:'auto'})
        var action = function(sn,editActivity){
                            var hh = sn.attr._hh;
                            if(!hh){
                                return;
                            }
                            var st = that.toStrTime(hh.split(':'))+'::H';
                            var d = sn.getRelativeData('.selectedDate');
                            if(editActivity){
                                genro.publish('edit_activity',{event_id:false, evt_date:d, s_time:st,activity_location:null,location_id:null});
                            }else{
                                genro.publish('edit_event',{event_id:false, evt_date:d, s_time:st,location_id:null,referrer_id:null});
                            }
                        }
        var box = container._('div','slotBox',{position:'absolute',top:'10px',left:'40px',right:0,bottom:0,
                                    dropTypes:'eventSlot',
                                    connect_ondblclick:function(e){
                                        action(e.target.sourceNode,e.shiftKey);
                                    }})
        box._('tooltip',{modifiers:'Shift',validclass:'eventSlot',
                        recordTemplate:{table:'base.event',pkeyCb:function(){
                            return this._slot.event_id;
                        }}});
        var tbox = container._('div',{position:'absolute',top:'4px',left:'0',width:'40px',bottom:0});
        this.prepareTimeGrid(box,tbox,slots);  
        dojo.forEach(slots,function(slot){
            that.fillSlotDetail(box,slot,that.location_columns?locations[slot.location_id]:0,that.location_columns?n_locations:1,date);
        });
        sourceNode.unfreeze();
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

    prepareTimeGrid:function(cell,tbox,slots){
        var hh_y = 30*this.scale_y;
        for (var i = this.work_start; i< this.work_end; i++) {
            //var c = i%2==0?i/2+':00':'';
            tbox._('div',{height:_px(hh_y)})._('div',{innerHTML:i+':00',text_align:'right',padding_right:'3px',color:'#666'})
            cell._('div',{height:_px(hh_y-1),border_top:'1px solid silver',_hh:i+':0',dropTargetCb:this.commonDropTargetCb,onDrop_eventSlot:this.freeSpaceOnDrop});
            tbox._('div',{height:_px(hh_y)})._('div',{innerHTML:'',text_align:'right',padding_right:'3px',color:'#666'})
            cell._('div',{height:_px(hh_y-1),border_top:'1px dotted silver',_hh:i+':30',dropTargetCb:this.commonDropTargetCb,onDrop_eventSlot:this.freeSpaceOnDrop});
        };
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

    fillDay:function(cell,date){
        var dataNode = this.data.getNode(_F(date,{pattern:'yyyy_MM_dd'},'D'));
        if(!dataNode){
            return;
        }
        if(this.channels){
            var n_channels = this.channels.length;
            var dataVal = dataNode.getValue();
            var cellcol;
            var cellwidth = Math.floor((cell.domNode.clientWidth-5)/n_channels);
            this.channels.forEach(function(channel,idx){
                cellcol = cell._('div',{position:'absolute',top:'2px',bottom:'2px',
                                        left:(2+idx*cellwidth)+'px',width:cellwidth+'px'});
                this.slotFiller(cellcol,date,dataVal.getNode(channel));
            });
        }else{
            this.slotFiller(cell,date,dataNode);
        }
       //var storeNode = this.data.getNodeByAttr();
       //var cellAttr = cell.getParentNode().attr;
       //var that = this;
       //var locations = {};
       //var n_locations = 0;

       //dojo.forEach(slots,function(slot){
       //    if(!(slot.location_id in locations)){
       //        locations[slot.location_id] = n_locations;
       //        n_locations++;
       //    }
       //});        
       //dojo.forEach(slots,function(slot){
       //    that.fillSlot(cell,slot,locations[slot.location_id],n_locations);
       //});
    },

    slotFiller_default:function(cellNode,date,dataNode){

    },

    slotFiller_timetable:function(cellNode,date,dataNode){

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
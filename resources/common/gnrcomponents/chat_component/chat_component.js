var ct_chat_utils = {
};

ct_chat_utils.processors = {};
ct_chat_utils.replacers = {};
ct_chat_utils.addProcessor = function(command,cb){
    this.processors[command] = cb;
};

ct_chat_utils.addReplacer = function(pattern,cb){
    this.replacers[pattern] = cb;
};

ct_chat_utils.fill_title = function(roombag) {
    var user = roombag.getItem('user');
    var user_name = roombag.getItem('user_name');
    var users = roombag.getItem('users');
    var unread = roombag.getItem('unread');
    var title;
    if (users.len() == 1) {
        title = 'empty';
    } else {
        var user_name_list = users.digest('#a.user_name').sort();
        var title = dojo.filter(user_name_list,
                               function(element) {
                                   return element != user_name
                               }).join(',');
        if (unread) {
            title = title + '(' + unread + ')';
        }
    }
    roombag.setItem('title', title);
};
ct_chat_utils.key_from_users = function(users){
    var user = genro._('gnr.avatar.user');
    var user_list = users.digest('#k').sort();
    var idx = dojo.indexOf(user_list,user);
    if(idx>=0){
        user_list.splice(idx,1);
    }
    var user_list = [user].concat(user_list);
    return user_list.join('*');
};

ct_chat_utils.open_chat = function(roomId, users) {
    var user = genro._('gnr.avatar.user');
    var user_name = genro._('gnr.avatar.user_name') || user;
    var roomsNode = genro.nodeById('ct_chat_rooms');
    var user_name_list = users.digest('#a.user_name').sort();
    users.setItem(user, null, {user_name:user_name,user:user});
    var roompath = 'gnr.chat.rooms.' + roomId;
    var roombag = new gnr.GnrBag({'users':users,user_name:user_name,user:user});
    ct_chat_utils.fill_title(roombag);
    var user_room_key = ct_chat_utils.key_from_users(users);
    genro.setData(roompath, roombag,{'user_room_key':user_room_key});
    var pane = roomsNode._('ContentPane', {title:'^.title',closable:true,datapath:roompath,pageName:roomId,_class:'ct_chatpane',rounded:4,
        onClose:function() {
            genro.publish("ct_send_message", {"roomId":this.sourceNode.attr.pageName,msg:null,disconnect:true});
            var rooms = ct_chat_utils.get_rooms()
            rooms.popNode(this.sourceNode.attr.pageName);
            return true;
        }});
    var newroom = pane._('BorderContainer', {nodeId:roomId + '_room',detachable:true,height:'100%',rounded:4});
    var sourceNode = newroom.getParentNode();
    var label = newroom._('ContentPane', {region:'top',_class:'ct_chatlabel'})

    var bottom = newroom._('ContentPane', {region:'bottom',_class:'ct_chatbottom'});
    roomsNode.widget.resize();
    roomsNode.setRelativeData('.selected_room', roomId);
    var bottombox = bottom._('div', {margin:'3px',margin_right:'8px',roomId:roomId,
        onEnter:function() {
            genro.publish("ct_typed_message", {roomId:this.attr.roomId});
        }
    });
    bottombox._('textbox', {value:'^.current_msg',width:'100%',id:'ct_msgtextbox_' + roomId});
    label._('div', {innerHTML:'^.title'});
    var chatbox = newroom._('ContentPane', {region:'center'})._('div', {height:'100%',overflow:'auto'});
    var roomPageNode = genro.nodeById(roomId + '_room');
    roomPageNode.chatNode = chatbox.getParentNode().domNode;
};

ct_chat_utils.read_msg = function(msgbag) {
    var msgtxt = msgbag.getItem('msg');
    var users = msgbag.getItem('users').deepCopy();
    var from_user = msgbag.getItem('from_user');
    var in_out = msgbag.getItem('in_out');
    var ts = msgbag.getItem('ts');
    var roomId = msgbag.getItem('roomId');
    var disconnect = msgbag.getItem('disconnect');
    var roomPage,message;
    var roombag,roomNode;
    roomPage = genro.nodeById(roomId + '_room');
    if (!roomPage) {
        ct_chat_utils.open_chat(roomId, users);
        roomPage = genro.nodeById(roomId + '_room');
    }
    roomNode = genro.getDataNode('gnr.chat.rooms.' + roomId);
    if(!roomNode){
        console.log('missing roomNode')
        return;
    }
    roombag = roomNode.getValue();
    if (genro.getData('gnr.chat.selected_room') != roomId) {
        roombag.setItem('unread', roombag.getItem('unread') || 0 + 1);
    } else {
        roombag.setItem('unread', null);
    }
    genro.fireEvent('gnr.chat.calc_unread');
    var users = roombag.getItem('users')
    if (disconnect) {
        users.popNode(from_user);
    }
    ct_chat_utils.fill_title(roombag);
    roomNode.updAttributes({'user_room_key':this.key_from_users(users)});
    var chatNode = roomPage.chatNode;

    message = chatNode.lastElementChild;
    if (!message || (message.from_user != from_user)) {
        message = document.createElement('div');
        message.innerHTML = '<div class="ct_msglbl"> <div class="ct_msglbl_from">' + from_user + '</div><div class="ct_msglbl_ts">' + genro.format(ts, {time:'medium'}) + '</div></div><div class="ct_msgbody"></div>';
        dojo.addClass(message, in_out == 'in' ? 'ct_inmsg' : 'ct_outmsg');
        dojo.addClass(message, 'ct_msgblock');
        message.from_user = from_user;
        chatNode.appendChild(message);
    }
    var msgrow = document.createElement('div');
    dojo.addClass(msgrow, 'ct_msgrow');
    msgtxt = highlightLinks(msgtxt);
    msgrow.innerHTML = msgtxt;
    roombag.setItem('last_message',msgtxt);
    message.lastElementChild.appendChild(msgrow);
    chatNode.scrollTop = chatNode.scrollHeight;
};

ct_chat_utils.get_rooms=function(){
    return genro.getData('gnr.chat.rooms');
};

ct_chat_utils.select_room = function(roomOrUsers){
    var roomNode = genro.getDataNode('gnr.chat.rooms.' +roomOrUsers);
    var roomId;
    if(roomNode){
        roomId = roomOrUsers;
    }else{
        var users = this.prepare_usersbag(roomOrUsers);
        var user_room_key = this.key_from_users(users);
        var rooms = genro.getData('gnr.chat.rooms')
        if(!rooms){
            rooms = new gnr.GnrBag();
            genro.setData('gnr.chat.rooms',rooms);
        }
        var n = rooms.getNodeByAttr('user_room_key',user_room_key);
        if (!n){
            roomId= 'cr_'+new Date().getTime();
            this.open_chat(roomId,users)
        }else{
            roomId = n.label;
        }
    }
    var roomsNode = genro.nodeById('ct_chat_rooms');
    roomsNode.setRelativeData('.selected_room',roomId);
    return roomId;
};

ct_chat_utils.prepare_usersbag = function(userstring){
    var connectedUsers = genro.getData('gnr.chat.connected_users');
    var userlist = userstring.split(',');
    var n;
    var users = new gnr.GnrBag();
    dojo.forEach(userlist,function(username){
        n = connectedUsers.getNode(username);
        users.setItem(n.attr.user,null,{user_name:n.attr.user_name,user:n.attr.user});
    });
    return users;
};

ct_chat_utils.send_message = function(users,message,priority){
    var roomId = this.select_room(users);
    genro.publish("ct_send_message", {roomId:roomId,msg:message,priority:priority});
};

ct_chat_utils.processCommand = function(command,message,roomId){
    var room = genro.getData('gnr.chat.rooms.' +roomId);
    var processor = this.processors[command];
    return processor? processor.call(this,message,room):'*error: unknown command "'+command+'"';
};

ct_chat_utils.callReplacer = function(replacer,path,roomId,msg){
    var cb = this.replacers[replacer];
    var room = genro.getData('gnr.chat.rooms.' +roomId);
    if(typeof(cb)=='function'){
        return cb.call(this,room,msg);
    }else{
        return cb;
    }
};
ct_chat_utils.addReplacer('(#q)\\b',function(room,message){
    return '<i>'+room.getItem('last_message')+'</i>';
});

ct_chat_utils.addProcessor('me',function(msg,room){
    return msg?"<i>"+room.getItem('user_name')+ ' '+ msg+"</i>":false;
});



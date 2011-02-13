var ct_chat_utils = {};

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
ct_chat_utils.open_chat = function(roomId, users) {
    var user = genro._('gnr.avatar.user');
    var user_name = genro._('gnr.avatar.user_name') || user;
    var roomsNode = genro.nodeById('ct_chat_rooms');
    var user_name_list = users.digest('#a.user_name').sort();
    users.setItem(user, null, {user_name:user_name,user:user});
    var roompath = 'gnr.chat.rooms.' + roomId;
    var roombag = new gnr.GnrBag({'users':users,user_name:user_name,user:user});
    ct_chat_utils.fill_title(roombag);
    genro.setData(roompath, roombag);
    var pane = roomsNode._('ContentPane', {title:'^.title',closable:true,closable:true,datapath:roompath,pageName:roomId,_class:'ct_chatpane',
        onClose:function() {
            genro.publish("ct_send_message", {"roomId":roomId,msg:null,disconnect:true});
            return true;
        }});
    var newroom = pane._('BorderContainer', {nodeId:roomId + '_room',detachable:true,height:'100%'});
    var sourceNode = newroom.getParentNode();
    var label = newroom._('ContentPane', {region:'top',_class:'ct_chatlabel'})

    var bottom = newroom._('ContentPane', {region:'bottom',_class:'ct_chatbottom'});
    roomsNode.widget.resize();
    roomsNode.setRelativeData('.selected_room', roomId);
    var bottombox = bottom._('div', {margin:'3px',margin_right:'8px',
        onEnter:function() {
            genro.publish("ct_send_message", {roomId:roomId})
        }
    });

    bottombox._('button', {label:'!!Share the current page', width:"100%", id:'ct_msgbtn_'+roomId,
                           roomId:roomId, msg_path: roompath + '.current_msg',
                           action:'genro.setData(msg_path,window.location.href);' +
                                   'genro.publish("ct_send_message", {roomId: roomId});'});

    bottombox._('textbox', {value:'^.current_msg',width:'100%',id:'ct_msgtextbox_' + roomId});
    label._('div', {'float':'left',innerHTML:'^.title'});
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
    var roombag;
    roomPage = genro.nodeById(roomId + '_room');
    if (!roomPage) {
        ct_chat_utils.open_chat(roomId, users);
        roomPage = genro.nodeById(roomId + '_room');
    }
    roombag = genro.getData('gnr.chat.rooms.' + roomId);
    if (genro.getData('gnr.chat.selected_room') != roomId) {
        roombag.setItem('unread', roombag.getItem('unread') || 0 + 1);
    } else {
        roombag.setItem('unread', null);
    }
    genro.fireEvent('gnr.chat.calc_unread');
    if (disconnect) {
        roombag.pop('users.' + from_user);
    }
    ct_chat_utils.fill_title(roombag);
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
    msgrow.innerHTML = highlightLinks(msgtxt);
    message.lastElementChild.appendChild(msgrow);
    chatNode.scrollTop = chatNode.scrollHeight;
};


var ct_chat_utils = {};

ct_chat_utils.open_chat = function(roomId,users){
    var user = genro._('gnr.avatar.user');
    var user_name=genro._('gnr.avatar.user_name') || user;
    users.setItem(user,null,{user_name:user_name,user:user});
    var user_name_list = users.digest('#a.user_name').sort();
    var roomTitle = dojo.filter(user_name_list,function(element){return element!=user_name}).join(',');    
    var roomsNode = genro.nodeById('ct_chat_rooms');
    var newroom = roomsNode._('BorderContainer',{pageName:roomId,_class:'ct_chatpane',nodeId:roomId+'_room',title:roomTitle,
                                                 closable:true,onClosing:'genro.serverCall("ct_remove_chat",{"room":"'+roomId+'"})'});
    var label = newroom._('ContentPane',{region:'top',_class:'ct_chatlabel'})
    var bottom = newroom._('ContentPane',{region:'bottom',_class:'ct_chatbottom',datapath:'gnr.chat.rooms.'+roomId});
    bottomNode = bottom.getParentNode();
    roomsNode.widget.resize();
    roomsNode.setRelativeData('.selected_room',roomId);
    var cb = function(){
                    genro.publish("ct_send_message",{roomId:roomId,users:users,
                                                     msg:bottomNode.getRelativeData('.current_msg')});
                    bottomNode.setRelativeData('.current_msg','');
                    };
                    
    bottom = bottom._('div',{margin:'3px',margin_right:'8px',
                            'onEnter':cb})                       
    bottom._('textbox',{value:'^.current_msg',width:'100%',id:'ct_msgtextbox_'+roomId});
    label._('div',{'float':'left',innerHTML:roomTitle});
    var chatbox = newroom._('ContentPane',{region:'center'})._('div',{height:'100%',overflow:'auto'});
    var roomPageNode = genro.nodeById(roomId+'_room');
    roomPageNode.chatNode = chatbox.getParentNode().domNode;
};




ct_chat_utils.read_msg = function(msgbag,msgnode){
    var msgtxt = msgbag.getItem('msg');
    var users = msgbag.getItem('users').deepCopy();
    var attrs,room,roomPage,message;
    attrs = msgnode.attr;
    room = attrs.roomId;
    roomPage = genro.nodeById(room+'_room');
    if(!roomPage){
        ct_chat_utils.open_chat(room,users);
        roomPage = genro.nodeById(room+'_room');
    }else{
        var unread_msg_path = 'gnr.chat.rooms.'+room+'?unread_msg';
        genro.setData(unread_msg_path,genro._(unread_msg_path)+1);
    }
    var chatNode = roomPage.chatNode;
    
    message = chatNode.lastElementChild;
    if(!message||(message.from_user!=attrs['from_user'])){
        message = document.createElement('div');
        message.innerHTML = '<div class="ct_msglbl"> <div class="ct_msglbl_from">'+attrs["from_user"]+'</div><div class="ct_msglbl_ts">'+genro.format(attrs["ts"],{time:'medium'})+'</div></div><div class="ct_msgbody"></div>';
        dojo.addClass(message,attrs['in_out']=='in'?'ct_inmsg':'ct_outmsg');
        dojo.addClass(message,'ct_msgblock');
        message.from_user =  attrs['from_user'];
        chatNode.appendChild(message);
    }
    var msgrow =  document.createElement('div');
    dojo.addClass(msgrow,'ct_msgrow');
    msgrow.innerHTML = msgtxt;
    message.lastElementChild.appendChild(msgrow);
    chatNode.scrollTop = chatNode.scrollHeight;    
};


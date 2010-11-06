var ct_chat_utils = {};
ct_chat_utils.open_chat = function(user){
    var roomsNode = genro.nodeById('ct_chat_rooms');
    var roomTab =  genro.nodeById(user+'_room');
    if (!roomTab){
        roomTab = roomsNode._('ContentPane',{pageName:user,overflow:'auto',title:user,
                                        margin:'4px',background:'white',border:'1px solid gray',
                                        id:user+'_room'});
        roomsNode.widget.resize();
    }

};

ct_chat_utils.read_msg = function(msgnode,msgtxt){
    var attrs,room,roomNode,message;
    attrs = msgnode.attr;
    room = attrs.room;
    roomNode = dojo.byId(room+'_room');
    console.log(attrs["ts"]);
    if(!roomNode){
        ct_chat_utils.open_chat(room);
        roomNode = dojo.byId(room+'_room');
    }
    message = roomNode.lastElementChild;
    if(!message||(message.from_user!=attrs['from_user'])){
        message = document.createElement('div');
        message.innerHTML = '<div class="ct_msglbl"> <div class="ct_msglbl_from">'+attrs["from_user"]+'</div><div class="ct_msglbl_ts">'+genro.format(attrs["ts"],{time:'medium'})+'</div></div><div class="ct_msgbody"></div>';
        dojo.addClass(message,attrs['in_out']=='in'?'ct_inmsg':'ct_outmsg');
        dojo.addClass(message,'ct_msgblock');
        message.from_user =  attrs['from_user'];
        roomNode.appendChild(message);
    }
    var msgrow =  document.createElement('div');
    dojo.addClass(msgrow,'ct_msgrow');
    msgrow.innerHTML = msgtxt;
    message.lastElementChild.appendChild(msgrow);
    roomNode.scrollTop = roomNode.scrollHeight;
    
    
}
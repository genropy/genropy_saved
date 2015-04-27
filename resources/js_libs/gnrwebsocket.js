var gnrwebsocket = {
    create:function (url) {
        var that=this;
        this._socket= new WebSocket(url);
        this._socket.onopen=function(){
            that.onopen()
        }
        this._socket.onclose=function(){
            that.onclose()
        }
        this._socket.onmessage=function(e){
            that.onmessage(e)
        }
        this._socket.onerror=function(error){
            that.onerror(error)
        }
        
    },
    onopen:function(){
        this.send('connected',{'page_id':'genro.page_id'})
    },
    onclose:function(){
        this.send('disconnected')
    },
    onerror:function(error){
        console.log('WebSocket Error ' + error);
    },
    onmessage:function(e){
        var data=e.data;
        if (data.indexOf('<?xml')==0){
            var result=this.parseResponse(e.data);
            var command=result.getItem('command') 
            var data = result.getItem('data')
            if (command){
                var handler=this['do_'+command] || this.do_publish
            }else{
                var handler= this.do_publish
                data= data || result
            }
            handler.apply(this,[data])
        }else{
            console.log('received on websocket',data)
        }
    },
    do_alert:function(data){
        alert(data)
    },
    do_set:function(data){
        var path=data.getItem('path')
        var datanode=data.getNode('data')
        genro.setData(path,datanode)
    },
    do_publish:function(data){
        var topic=data.getItem('topic')
        if (!topic){
            topic='onWsMessage';
        }else{
            var data = data.getItem('data')
        }
        genro.publish(topic,data)
    },
    send:function(command,kw){
        var kw=kw || {};
        kw['command']=command
        kw=genro.rpc.serializeParameters(genro.src.dynamicParameters(kw));
        this._socket.send(dojo.toJson(kw))
    },
    parseResponse:function(response){
        var result = new gnr.GnrBag();
        var parser=new window.DOMParser()
        result.fromXmlDoc(parser.parseFromString(response, "text/xml")
                                            ,genro.clsdict);
        return result
    }
}

drop_uploader={
    
crlf : '\r\n',
dashdash : '--',
constructor: function(){
},
set_url: function (url){
    this.url=url;
},
new_text_param: function(name, value, boundary){
    var dashdash = this.dashdash;
    var crlf = this.crlf;
    return this.write_boundary(boundary)+'Content-Disposition: form-data; name="'+name+'"'+crlf+'Content-Type: text/plain'+crlf+crlf+value+crlf;
}, 
write_boundary: function(boundary){
    return this.dashdash+boundary+this.crlf;
},
new_file_param: function(name, file, boundary){
    var crlf = this.crlf;
    var dashdash = this.dashdash;
    builder = this.write_boundary(boundary)+'Content-Disposition: form-data; name="user_file[]"';
    if (file.fileName) builder += '; filename="' + file.fileName + '"';
    builder += crlf+'Content-Type: application/octet-stream'+crlf+crlf; 
    builder += file.getAsBinary();
    builder += crlf;
    return builder;
},
end_request: function(boundary){
    return this.dashdash+boundary+this.dashdash+this.crlf;
},
start_request: function(boundary){
    return this.dashdash+boundary+this.crlf;
},
drop_handler: function (event) {
    
    var data = event.dataTransfer;
    var files = new Array();
    /* Prevent Browser opening the dragged file. */
    console.log('drop');
    
    for (var i = 0; i < data.files.length; i++) {
        files.push(data.files[i]);
    };
    genro.setData('files',files);
    event.stopPropagation();
},
send_files: function(files){

    console.log(files);

    var boundary = '------multipartformboundary' + (new Date).getTime();
    var dashdash = '--';
    var crlf     = '\r\n';
    this.url='/';
    /* Build RFC2388 string. */
    var builder = '';//this.start_request(boundary);    
    /* For each dropped file. */
    builder += this.new_text_param('rpc','upload', boundary);
    builder += this.new_text_param('page_id',genro.page_id, boundary);
    /*add_file = dojo.hitch(this,function (file){this.new_file_param(null,file,boundary)});
    dojo.forEach(data.files,add_file);*/
    console.log(files);
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        builder +=this.new_file_param(null,file,boundary);
    }

    /* Mark end of the request. */
    builder += this.end_request(boundary);
    post_kwargs={url:this.url,
                postData:builder,
                headers:{'content-type': 'multipart/form-data; boundary=' + boundary},
                load:function(data){console.log(data);},
                error:function(data){console.log(data);}
        };
    dojo.rawXhrPost(post_kwargs);
    
    
}
};
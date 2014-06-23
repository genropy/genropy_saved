var AttachManager = {
    onDropFiles:function(sourceNode,files){
        var uploadKw =  objectExtract(sourceNode.attr,'_uploader_*',true)
        uploadKw = sourceNode.evaluateOnNode(uploadKw);
        var params = {attachment_table:sourceNode.getInheritedAttributes()['table'],maintable_id:uploadKw.fkey,
                      onUploadingMethod:uploadKw['onUploadingMethod']};
        var kw = {uploaderId:'attachmentManager',
                  onProgress:function(e){console.log('onProgress',e)},
                  onResult:function(e){console.log('onResult',e)}
                }
        var sendKw,sendParams;
        dojo.forEach(files,function(file){
            sendKw = objectUpdate({filename:file.name},kw);
            sendParams = objectUpdate({mimetype:file.type},params);
            genro.rpc.uploadMultipart_oneFile(file, sendParams, sendKw);
        });
    }
};
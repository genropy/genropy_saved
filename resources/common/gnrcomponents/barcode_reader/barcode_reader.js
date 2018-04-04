var BarcodeReader = {
    lastScanned:null,
    lastScannedTS:null,
    start:function(sourceNode,codes,destination,delay,sound){
        readers = codes?codes.split(','):[];
        readers = readers.map(function(n){return n+'_reader';});
        console.log('readers',readers);
        this.sound = sound;
        this.delay = delay || 0;
        console.log(delay);
        Quagga.init({
            inputStream : {
            name : "Live",
            type : "LiveStream",
            target: sourceNode.domNode   
            },
            decoder : {readers : readers
            }
        }, function(err) {
            if (err) {
                console.log(err);
                return;
            }
            console.log("Initialization finished. Ready to start");
            Quagga.start();
        });
        Quagga.onDetected(function(result) {
            if(result.codeResult.startInfo.error>0.3){
                return;
            }
            console.log('result',result.codeResult.code,'error',result.codeResult.startInfo.error);
            var code = result.codeResult.code;
            var ts = new Date();
            var delta = ts-BarcodeReader.lastScannedTS;
            if ((code!=BarcodeReader.lastScanned) || (delta/1000>BarcodeReader.delay)){
                if(BarcodeReader.sound){
                    genro.playSound(BarcodeReader.sound);
                }
                sourceNode.setRelativeData(destination,code);
                BarcodeReader.lastScanned = code;
                BarcodeReader.lastScannedTS = ts;
            }
        });
        
    }
};
<!-- ================  Genropy Headers ================ -->
<script type="text/javascript" src="${dojolib}" djConfig="${djConfig}"> </script>
<script type="text/javascript">dojo.registerModulePath('gnr','${gnrModulePath}');</script>
% if favicon:
     <link rel="icon" href="${favicon}" type="image/${favicon_ext}" />
% endif
% if google_fonts:
    <link href='http://fonts.googleapis.com/css?family=${google_fonts}' rel='stylesheet' type='text/css'>
% endif

% if dijitImport:
    % for single in dijitImport:
        <script type="text/javascript" gnrsrc="${single}"></script>
    % endfor
% endif

% for jsname in genroJsImport:
    <script type="text/javascript" gnrsrc="${jsname}"></script>
% endfor

% for customHeader in customHeaders:
    ${customHeader}
% endfor

% for jsname in js_requires:
        <script type="text/javascript" gnrsrc="${jsname}"></script>
% endfor

        <style type="text/css">
            % for cssname in css_dojo:
            @import url("${cssname}");  
            % endfor
        </style>
            
        % for cssmedia, cssnames  in css_genro.items():
        <style type="text/css" media="${cssmedia}">
                % for cssname in cssnames:
            @import url("${cssname}");
                % endfor
        </style>
        % endfor
        <style type="text/css">    
            % for cssname in css_requires:
            @import url("${cssname}");
            % endfor
        </style>
        
        % for cssmedia, cssnames  in css_media_requires.items():
        <style type="text/css" media="${cssmedia}">
                % for cssname in cssnames:
            @import url("${cssname}");
                % endfor
        </style>
        % endfor
        
        <script type="text/javascript">
        console.log("window.electron_process");
        console.log(window.electron_process);
        if (window.local_require){
            const fs = local_require('fs');
            const path = local_require('path');

            function mkDirByPathSync(targetDir, {isRelativeToScript = false} = {}) {
            const sep = path.sep;
            const initDir = path.isAbsolute(targetDir) ? sep : '';
            const baseDir = isRelativeToScript ? __dirname : '.';

            targetDir.split(sep).reduce(function(parentDir, childDir) {
                const curDir = path.resolve(baseDir, parentDir, childDir);
                try {
                    fs.mkdirSync(curDir);
                console.log('Directorycreated: ', curDir);
                } catch (err) {
                if (err.code !== 'EEXIST') {
                    throw err;
                    }

                console.log('Directory already exists: ', curDir);
                }

                return curDir;
                }, initDir);
            }
        }   
            console.log(window.electron_process);
            if (window.electron_process){
                console.log("sono_electron");
                console.log(window.electron_process);
            }
            loadJs = function(url, cb) {
                console.log(url);
                var e = document.createElement("script");
                
                if (window.electron_process){
                    const fs = local_require('fs');
                    const path = local_require('path');
                    const sep = path.sep;
                    console.log(url.split(sep));
                }
                e.src = url;
                e.async = false;
                e.type = "text/javascript";
                document.getElementsByTagName("head")[0].appendChild(e);
                if (cb) {
                e.onload = cb;
                }
            }
            var scripts = document.head.querySelectorAll('script[gnrsrc]');
            var pending = scripts.length-1;
            var gnrArgs = { page_id:'${page_id}',baseUrl:'${filename}', pageMode: '${pageMode or "legacy"}',\
                pageModule:'${pageModule}', domRootName:'mainWindow', startArgs: ${startArgs}, baseUrl:'${baseUrl or "/"}'}
                
            var loadGenro = function(){
                var e = document.createElement("script");
                e.text = "var genro = new gnr.GenroClient(gnrArgs);"
                e.type = "text/javascript";
                document.getElementsByTagName("head")[0].appendChild(e);
            }
            scripts.forEach(
                function(scr){
                    var url = scr.getAttribute('gnrsrc');
                    console.log(url);
                    loadJs(scr.getAttribute('gnrsrc'), function(){
                        console.log(pending);
                        if(!--pending){
                            loadGenro();
                        }
                    });
                }
            )
        </script>
        <script type="text/javascript">
            
        </script>
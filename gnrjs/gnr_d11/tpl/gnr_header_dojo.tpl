<!-- ================  Genropy Headers ================ -->
        <script type="text/javascript" src="${dojolib}"
                djConfig="${djConfig}">
		</script>

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
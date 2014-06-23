dojo.declare("gnr.PagedEditorManager", null, { 
        constructor:function(sourceNode){
            this.sourceNode = sourceNode;
            this.pages = new gnr.GnrBag();
            this.letterheads = null;
            this.disabled = true;
            this.bottom_extraspace = sourceNode.attr.bottom_extraspace || 0;
            this.editorNode = this.sourceNode.getChild('center').getChild('editor');
            var that = this;
            dojo.connect(this.editorNode.externalWidget,'gnr_onTyped',function(){
                that.setDisabled(false);
            })
        },

        previewRoot:function(){
            if(!this._previewRoot){
                this._previewRoot = this.sourceNode._value.getNodeByAttr('pe_previewRoot',true);
            }
            return this._previewRoot;
        },
        addPage:function(){
            var rn = this.previewRoot().domNode;  
            var p = document.createElement('div'); 
            var content_node;        
            if(this.letterheads){
                var letterhead_page = (rn.childElementCount==0 || this.letterheads.len()==1)? this.letterheads.getItem('page_base'):this.letterheads.getItem('page_next');
                p.innerHTML = letterhead_page;
                var p = p.children[0];
                content_node = dojo.query('div[content_node=t]',p)[0];
            }else{
                genro.dom.addClass(p,'pe_pages');
                content_node = p;
            }
            rn.appendChild(p);
            genro.dom.addClass(content_node,'pe_content')
            //content_node.setAttribute('contenteditable','true');
            return content_node;
        },
        
        setPagedText:function(pagedText){
            var pt = pagedText.match(/(<body>)((.|\n)*)(<\/body>)/);
            if(pt){
                this.previewRoot().domNode.innerHTML = pt[2];
            }
        },

        getPagedText:function(){
            var paged_text = this.previewRoot().domNode.innerHTML;
            if(!paged_text){
                return
            }
            var result = '<html> <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <style> .gnrlayout{position:absolute;} .letterhead_page{page-break-before:always;} .letterhead_page:first-child{page-break-before:avoid;}</style> </head> <body>'
            result+=paged_text;
            result+='</body> </html>';
            return result;
        },

        onContentChanged:function(value){
            if(!this.disabled){
                this.previewRoot().domNode.style.visibility ='hidden';
                var prevZoom = this.previewRoot().domNode.style.zoom ;
                this.previewRoot().domNode.style.zoom ='1';
                this.paginate(value);
                this.previewRoot().domNode.style.zoom =prevZoom;
                this.previewRoot().domNode.style.visibility ='visible';
            }
        },

        paginate:function(value){
            this.previewRoot().domNode.innerHTML = '';
            var page = this.addPage();
            var dest = document.createElement('div');
            page.appendChild(dest);
            var src = document.createElement('div'); 
            src.innerHTML = value;
            var children = src.children;
            var node;
            while(children.length){
                node = src.removeChild(children[0]);
                genro.dom.addClass(node,'pe_node');
                dest.appendChild(node);
                if((dest.clientHeight+ this.bottom_extraspace)>=page.clientHeight){
                    node = dest.removeChild(node);
                    page = this.addPage();
                    dest = document.createElement('div');
                    page.appendChild(dest);
                    dest.appendChild(node);
                }
            }
        },

        setDisabled:function(disabled){
            this.disabled = disabled===false?false:true;
        }
    }
);
dojo.declare("gnr.PagedEditorManager", null, { 
        constructor:function(sourceNode){
            this.sourceNode = sourceNode;
            this.pages = new gnr.GnrBag();
            this.letterheads = null;
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
            return content_node;
        },
        
        onContentChanged:function(value){
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
                if(dest.clientHeight>page.clientHeight){
                    node = dest.removeChild(node);
                    page = this.addPage();
                    dest = document.createElement('div');
                    page.appendChild(dest);
                    dest.appendChild(node);
                }
            }
        }
    }
);


var genropatches = {};
genropatches.forEachError = function(){
    var fe = dojo.forEach;
    dojo['forEach'] = function(arr,cb,scope){
        if(arr==null){
            if(genro.isDeveloper){
                debugger;
            }else{
                console.error('ERROR FOREACH',arguments,cb);
                return;
            } 
        }
        fe.call(dojo,arr,cb,scope);
    }
};

genropatches.setStateClass=function(){
    dojo.require('dijit.form._FormWidget');
    dijit.form._FormWidget.prototype._setStateClass_original = dijit.form._FormWidget.prototype._setStateClass;
    dijit.form._FormWidget.prototype._setStateClass = function(){
        if(this.stateNode || this.domNode){
            this._setStateClass_original();
        }
    }
}
genropatches.getDocumentWindow = function(){
    dijit.getDocumentWindow = function(doc){
    //  summary
    //  Get window object associated with document doc

    // With Safari, there is not way to retrieve the window from the document, so we must fix it.
    if(dojo.isSafari && !doc._parentWindow){
        /*
            This is a Safari specific function that fix the reference to the parent
            window from the document object.
            TODO: #5711: should the use of document below reference dojo.doc instead
            in case they're not the same?
        */
        var fix=function(win){
            win.document._parentWindow=win;
            for(var i=0; i<win.frames.length; i++){
                try{
                    fix(win.frames[i]);
                }catch(e){
                    
                }
                
            }
        }
        fix(window.top);
    }

    //In some IE versions (at least 6.0), document.parentWindow does not return a
    //reference to the real window object (maybe a copy), so we must fix it as well
    //We use IE specific execScript to attach the real window reference to
    //document._parentWindow for later use
    //TODO: #5711: should the use of document below reference dojo.doc instead in case they're not the same?
    if(dojo.isIE && window !== document.parentWindow && !doc._parentWindow){
        /*
        In IE 6, only the variable "window" can be used to connect events (others
        may be only copies).
        */
        doc.parentWindow.execScript("document._parentWindow = window;", "Javascript");
        //to prevent memory leak, unset it after use
        //another possibility is to add an onUnload handler which seems overkill to me (liucougar)
        var win = doc._parentWindow;
        doc._parentWindow = null;
        return win; //  Window
    }

    return doc._parentWindow || doc.parentWindow || doc.defaultView;    //  Window
}
}
genropatches.sendAsBinary=function(){
    if(!XMLHttpRequest.prototype.sendAsBinary){
            XMLHttpRequest.prototype.sendAsBinary = function(datastr) {
                function byteValue(x) {
                    return x.charCodeAt(0) & 0xff;
                }
                var ords = Array.prototype.map.call(datastr, byteValue);
                var ui8a = new Uint8Array(ords);
                this.send(ui8a.buffer);
            }
        }
};
genropatches.dojoToJson = function() {
    dojo.toJson = function(/*Object*/ it, /*Boolean?*/ prettyPrint, /*String?*/ _indentStr){
        if(it === undefined){
            return "null";
        }
        var objtype = typeof it;
        if(objtype == "number" || objtype == "boolean"){
            return it + "";
        }
        if(it === null){
            return "null";
        }
        if(dojo.isString(it)){ 
            return dojo._escapeString(it); 
        }
        if(it.nodeType && it.cloneNode){ // isNode
            return ""; // FIXME: would something like outerHTML be better here?
        }
        // recurse
        var recurse = arguments.callee;
        // short-circuit for objects that support "json" serialization
        // if they return "self" then just pass-through...
        var newObj;
        _indentStr = _indentStr || "";
        var nextIndent = prettyPrint ? _indentStr + dojo.toJsonIndentStr : "";
        if(typeof it.__json__ == "function"){
            newObj = it.__json__();
            if(it !== newObj){
                return recurse(newObj, prettyPrint, nextIndent);
            }
        }
        if(typeof it.json == "function"){
            newObj = it.json();
            if(it !== newObj){
                return recurse(newObj, prettyPrint, nextIndent);
            }
        }

        var sep = prettyPrint ? " " : "";
        var newLine = prettyPrint ? "\n" : "";

        // array
        if(dojo.isArray(it)){
            var res = dojo.map(it, function(obj){
                var val = recurse(obj, prettyPrint, nextIndent);
                if(typeof val != "string"){
                    val = "null";
                }
                return newLine + nextIndent + val;
            });
            return "[" + res.join("," + sep) + newLine + _indentStr + "]";
        }
        /*
        // look in the registry
        try {
            window.o = it;
            newObj = dojo.json.jsonRegistry.match(it);
            return recurse(newObj, prettyPrint, nextIndent);
        }catch(e){
            // console.debug(e);
        }
        // it's a function with no adapter, skip it
        */
        if(objtype == "function"){
            return null; // null
        }
        // generic object code path
        var output = [];
        for(var key in it){
            var keyStr;
            if(typeof key == "number"){
                keyStr = '"' + key + '"';
            }else if(typeof key == "string"){
                keyStr = dojo._escapeString(key);
            }else{
                // skip non-string or number keys
                continue;
            }
            val = recurse(it[key], prettyPrint, nextIndent);
            if(typeof val != "string"){
                // skip non-serializable values
                continue;
            }
            // FIXME: use += on Moz!!
            //   MOW NOTE: using += is a pain because you have to account for the dangling comma...
            output.push(newLine + nextIndent + keyStr + ":" + sep + val);
        }
        return "{" + output.join("," + sep) + newLine + _indentStr + "}"; // String
    }
};
genropatches.menu = function(){
    dojo.require('dijit.Menu');
    dijit.Menu.prototype._openMyself = function(/*Event*/ e){
		// summary:
		//		Internal function for opening myself when the user
		//		does a right-click or something similar

		if(this.leftClickToOpen&&e.button>0){
			return;
		}
		dojo.stopEvent(e);

		// Get coordinates.
		// if we are opening the menu with the mouse or on safari open
		// the menu at the mouse cursor
		// (Safari does not have a keyboard command to open the context menu
		// and we don't currently have a reliable way to determine
		// _contextMenuWithMouse on Safari)
		var x,y;
		if(dojo.isSafari || this._contextMenuWithMouse){
			x=e.pageX;
			y=e.pageY;
		}else{
			// otherwise open near e.target
			var coords = dojo.coords(e.target, true);
			x = coords.x + 10;
			y = coords.y + 10;
		}

		var self=this;
		var savedFocus = dijit.getFocus(this);
		function closeAndRestoreFocus(){
			// user has clicked on a menu or popup
			dijit.focus(savedFocus);
			dijit.popup.close(self);
		}
		var popupKw = {
			popup: this,
			x: x,
			y: y,
			onExecute: closeAndRestoreFocus,
			onCancel: closeAndRestoreFocus,
			orient: this.isLeftToRight() ? 'L' : 'R'
		};
		this.onOpeningPopup(popupKw);
		dijit.popup.open(popupKw);
		this.focus();

		this._onBlur = function(){
			this.inherited('_onBlur', arguments);
			// Usually the parent closes the child widget but if this is a context
			// menu then there is no parent
			dijit.popup.close(this);
			// don't try to restore focus; user has clicked another part of the screen
			// and set focus there
		}
	};
    
};
genropatches.comboBox = function() {
    dojo.require('dijit.form.ComboBox');
    dojo.declare("gnr.Gnr_ComboBoxMenu", dijit.form._ComboBoxMenu, {
        /*templateString:"<div class='dijitMenu' dojoAttachEvent='onmousedown,onmouseup,onmouseover,onmouseout' tabIndex='-1' style='overflow:\"auto\";'>"
         +"<div class='dijitMenuItem dijitMenuPreviousButton' dojoAttachPoint='previousButton'></div>"
         +"<div class='dijitMenuItem dijitMenuNextButton' dojoAttachPoint='nextButton'></div></div>",*/
        templateString: "<ul class='dijitMenu' dojoAttachEvent='onmousedown:_onMouseDown,onmouseup:_onMouseUp,onmouseout:_onMouseOut' tabIndex='-1' style='overflow:\"auto\";'>"
                + "<li class='dijitMenuItem dijitMenuPreviousButton' dojoAttachPoint='previousButton'></li>"
                + "<li class='dijitMenuItem dijitMenuNextButton' dojoAttachPoint='nextButton'></li>"
                + "</ul>",
        createOptions:function(results, dataObject, labelFunc) {
            var lfa = dataObject.store.lastFetchAttrs;
            var columns = lfa.columns.split(',');
            var headers = lfa.headers.split(',');
            var tblclass = 'multiColumnSelect' + ' ' + lfa['resultClass'];
            genro.dom.scrollableTable(this.domNode, results[0].getParentBag(), {'columns':columns,'headers':headers,'tblclass':tblclass});
            this.domNode.onmouseover = dojo.hitch(this, 'onmouseover');
            // this.nextButton.style.display='none';
            //  this.previousButton.style.display='none';
            //genro.debug("this.domNode.innerHTML=tbl.join('\n');");
        },
        tblrows:function() {
            return dojo.query('tbody tr', this.domNode);
        },

        clearResultList:function() {
            // keep the previous and next buttons of course
            while (this.domNode.childNodes.length > 2) {
                this.domNode.innerHtml = '';
            }
        },
        getItems:function() {
            return this.tblrows();
        },

        getListLength:function() {
            return this.tblrows().length;
        },

        onmouseup:function(/*Event*/ evt) {
            if (evt.target === this.domNode) {
                return;
            } else {
                var tgt = this.getHighlightedOption();
                if (tgt) {
                    this.setValue({target:tgt}, true);
                }
                ;
            }
        },

        onmouseover:function(/*Event*/ evt) {
            if (dojo.isIE > 0) {
                return;
            }
            if (evt.target === this.domNode) {
                return;
            }
            var tgt = evt.target;
            if (tgt) {
                if (tgt.getAttribute('id')) {
                    this._focusOptionNode(tgt);
                } else if (tgt.parentNode.getAttribute('id')) {
                    this._focusOptionNode(tgt.parentNode);
                }
            }
            ;

        },
        _page:function(/*Boolean*/ up) {
            return;
        },
        getHighlightedOption:function() {
            // summary:
            //  Returns the highlighted option.
            return this._highlighted_option;
        },
        _focusOptionNode:function(/*DomNode*/ node) {
            // summary:
            //  does the actual highlight
            if (this._highlighted_option != node) {
                this._blurOptionNode();
                this._highlighted_option = node;
                dojo.addClass(this._highlighted_option, "multiColumnSelectHover");
            }
        },
        _blurOptionNode:function() {
            // summary:
            //  removes highlight on highlighted option
            if (this._highlighted_option) {
                dojo.removeClass(this._highlighted_option, "multiColumnSelectHover");
                this._highlighted_option = null;
            }
        },
        _highlightNextOption:function() {
            // because each press of a button clears the menu,
            // the highlighted option sometimes becomes detached from the menu!
            // test to see if the option has a parent to see if this is the case.
            var domnode_bottom = this.domNode.getBoundingClientRect().bottom;
            var nextNode;
            var hop = this.getHighlightedOption();
            if (!this.getHighlightedOption()) {
                nextNode = this.tblrows()[0];
            } else if (hop.nextSibling && hop.style.display != "none") {
                nextNode = hop.nextSibling;
            }
            if (nextNode) {
                brect = nextNode.getBoundingClientRect();
                this._focusOptionNode(nextNode);

                if (brect.bottom > domnode_bottom) {
                    var delta = brect.bottom - brect.top;
                    var scrollTop = this.domNode.children[0].children[1].scrollTop;
                    this.domNode.children[0].children[1].scrollTop = scrollTop + 20;
                }
            }

            // scrollIntoView is called outside of _focusOptionNode because in IE putting it inside causes the menu to scroll up on mouseover
            //  dijit.scrollIntoView(this._highlighted_option);
        },

        highlightFirstOption:function() {

            // highlight the non-Previous choices option
            this._focusOptionNode(this.tblrows()[0]);
            //  dijit.scrollIntoView(this._highlighted_option);
        },

        highlightLastOption:function() {
            // highlight the noon-More choices option
            var rows = this.tblrows();
            this._focusOptionNode(rows[rows.length - 1]);
            //  dijit.scrollIntoView(this._highlighted_option);
        },

        _highlightPrevOption:function() {

            // if nothing selected, highlight last option
            // makes sense if you select Previous and try to keep scrolling up the list
            if (!this.getHighlightedOption()) {
                var rows = this.tblrows();
                this._focusOptionNode(rows[rows.length - 1]);
            } else if (this._highlighted_option.previousSibling && this._highlighted_option.previousSibling.style.display != "none") {
                this._focusOptionNode(this._highlighted_option.previousSibling);
            }
            //  dijit.scrollIntoView(this._highlighted_option);
        },

        handleKey:function(evt) {
            switch (evt.keyCode) {
                case dojo.keys.DOWN_ARROW:
                    this._highlightNextOption();
                    break;
                case dojo.keys.PAGE_DOWN:
                    this.pageDown();
                    break;
                case dojo.keys.UP_ARROW:
                    this._highlightPrevOption();
                    break;
                case dojo.keys.PAGE_UP:
                    this.pageUp();
                    break;
            }
        }
    });
};
genropatches.borderContainer = function() {
    dojo.require("dijit.layout.BorderContainer");
    dojo.require("dijit.layout._LayoutWidget");
    dojo.declare(
            "dijit.layout.BorderContainer",
//  [dijit._Widget, dijit._Container, dijit._Contained],
            dijit.layout._LayoutWidget,
    {
        // summary:
        //  Provides layout in 5 regions, a center and borders along its 4 sides.
        //
        // description:
        //  A BorderContainer is a box with a specified size (like style="width: 500px; height: 500px;"),
        //  that contains a child widget marked region="center" and optionally children widgets marked
        //  region equal to "top", "bottom", "leading", "trailing", "left" or "right".
        //  Children along the edges will be laid out according to width or height dimensions.  The remaining
        //  space is designated for the center region.
        //  The outer size must be specified on the BorderContainer node.  Width must be specified for the sides
        //  and height for the top and bottom, respectively.  No dimensions should be specified on the center;
        //  it will fill the remaining space.  Regions named "leading" and "trailing" may be used just like
        //  "left" and "right" except that they will be reversed in right-to-left environments.
        //  Optional splitters may be specified on the edge widgets only to make them resizable by the user.
        //
        // example:
        // |    <style>
        // |        html, body { height: 100%; width: 100%; }
        // |    </style>
        // |    <div dojoType="BorderContainer" design="sidebar" style="width: 100%; height: 100%">
        // |        <div dojoType="ContentPane" region="top">header text</div>
        // |        <div dojoType="ContentPane" region="right" style="width: 200px;">table of contents</div>
        // |        <div dojoType="ContentPane" region="center">client area</div>
        // |    </div>
        //
        // design: String
        //  choose which design is used for the layout: "headline" (default) where the top and bottom extend
        //  the full width of the container, or "sidebar" where the left and right sides extend from top to bottom.
        design: "headline",

        // liveSplitters: Boolean
        //  specifies whether splitters resize as you drag (true) or only upon mouseup (false)
        liveSplitters: true,

        // persist: Boolean
        //      Save splitter positions in a cookie.
        persist: false, // Boolean

        // _splitterClass: String
        //      Optional hook to override the default Splitter widget used by BorderContainer
        _splitterClass: "dijit.layout._Splitter",

        postCreate: function() {
            this.inherited(arguments);

            this._splitters = {};
            this._splitterThickness = {};
            dojo.addClass(this.domNode, "dijitBorderContainer");
        },

        startup: function() {
            if (this._started) {
                return;
            }
            dojo.forEach(this.getChildren(), function(child) {
                this._setupChild(child);
                var region = child.region;
                if (this._splitters[region]) {
                    dojo.place(this._splitters[region], child.domNode, "after");
                    this._computeSplitterThickness(region); // redundant?
                }
            }, this);
            this.inherited(arguments);
        },

        _setupChild: function(/*Widget*/child) {
            var region = child.region;
            if (region) {
//          dojo.addClass(child.domNode, "dijitBorderContainerPane");
                child.domNode.style.position = "absolute"; // bill says not to set this in CSS, since we can't keep others
                // from destroying the class list

                var ltr = this.isLeftToRight();
                if (region == "leading") {
                    region = ltr ? "left" : "right";
                }
                if (region == "trailing") {
                    region = ltr ? "right" : "left";
                }

                //FIXME: redundant?
                this["_" + region] = child.domNode;
                this["_" + region + "Widget"] = child;

                if (child.splitter && !this._splitters[region]) {
                    var _Splitter = dojo.getObject(this._splitterClass);
                    var flip = {left:'right', right:'left', top:'bottom', bottom:'top', leading:'trailing', trailing:'leading'};
                    var oppNodeList = dojo.query('[region=' + flip[child.region] + ']', this.domNode);
                    var splitter = new _Splitter({ container: this, child: child, region: region,
                        oppNode: oppNodeList[0], live: this.liveSplitters });
                    this._splitters[region] = splitter.domNode;
                }
                child.region = region;
            }
        },
        /* getRegionVisibility: function(region){
         return (this._splitterThickness[region]!=0);
         },

         showHideRegion: function(region, show){
         var regions=region.split(',');
         for (var i=0; i < regions.length; i++) {
         show = this.showHideRegion_one(regions[i],show);
         };
         return show;
         },
         showHideRegion_one: function(region, show){
         if(this._splitters[region]){
         this._computeSplitterThickness(region);
         }
         var regionNode = this['_'+region];
         if (regionNode){
         if(show=='toggle'){
         show = (this._splitterThickness[region]==0);
         }
         var disp=show? '':'none';
         var splitterNode = this._splitters[region];
         if (splitterNode){
         var tk=this._splitterThickness['_'+region] || this._splitterThickness[region];
         this._splitterThickness['_'+region]=tk;
         this._splitterThickness[region] =show? tk : 0;
         var st=dojo.style(splitterNode,'display',disp);
         }
         dojo.style(regionNode,'display',disp);
         this.layout();
         }
         return show;
         },*/

        _computeSplitterThickness: function(region) {
            var re = new RegExp("top|bottom");
            this._splitterThickness[region] =
                    dojo.marginBox(this._splitters[region])[(re.test(region) ? 'h' : 'w')];
        },

        layout: function() {
            this._layoutChildren();
        },

        addChild: function(/*Widget*/ child, /*Integer?*/ insertIndex) {
            this.inherited(arguments);
            this._setupChild(child);
            if (this._started) {
                var region = child.region;
                if (this._splitters[region]) {
                    dojo.place(this._splitters[region], child.domNode, "after");
                    this._computeSplitterThickness(region);
                }
                this._layoutChildren();
            }
        },

        removeChild: function(/*Widget*/ child) {
            var region = child.region;
            var splitter = this._splitters[region];
            if (splitter) {
                dijit.byNode(splitter).destroy();
                delete this._splitters[region];
                delete this._splitterThickness[region];
            }
            this.inherited(arguments);
            delete this["_" + region];
            delete this["_" + region + "Widget"];
            if (this._started) {
                this._layoutChildren(child.region);
            }
        },

        _layoutChildren: function(/*String?*/changedRegion) {
            var sidebarLayout = (this.design == "sidebar");
            var topHeight = 0, bottomHeight = 0, leftWidth = 0, rightWidth = 0;
            var topStyle = {}, leftStyle = {}, rightStyle = {}, bottomStyle = {},
                    centerStyle = (this._center && this._center.style) || {};

            var changedSide = /left|right/.test(changedRegion);

            var cs = dojo.getComputedStyle(this.domNode);
            var pe = dojo._getPadExtents(this.domNode, cs);
            pe.r = parseFloat(cs.paddingRight);
            pe.b = parseFloat(cs.paddingBottom);

            var layoutSides = !changedRegion || (!changedSide && !sidebarLayout);
            var layoutTopBottom = !changedRegion || (changedSide && sidebarLayout);
            if (this._top) {
                topStyle = layoutTopBottom && this._top.style;
                topHeight = dojo.marginBox(this._top).h;
            }
            if (this._left) {
                leftStyle = layoutSides && this._left.style;
                leftWidth = dojo.marginBox(this._left).w;
            }
            if (this._right) {
                rightStyle = layoutSides && this._right.style;
                rightWidth = dojo.marginBox(this._right).w;
            }
            if (this._bottom) {
                bottomStyle = layoutTopBottom && this._bottom.style;
                bottomHeight = dojo.marginBox(this._bottom).h;
            }

            var splitters = this._splitters;
            var topSplitter = splitters.top;
            var bottomSplitter = splitters.bottom;
            var leftSplitter = splitters.left;
            var rightSplitter = splitters.right;
            var splitterThickness = this._splitterThickness;
            var topSplitterThickness = splitterThickness.top || 0;
            var leftSplitterThickness = splitterThickness.left || 0;
            var rightSplitterThickness = splitterThickness.right || 0;
            var bottomSplitterThickness = splitterThickness.bottom || 0;

            // Check for race condition where CSS hasn't finished loading, so
            // the splitter width == the viewport width (#5824)
            if (leftSplitterThickness > 50 || rightSplitterThickness > 50) {
                setTimeout(dojo.hitch(this, function() {
                    for (var region in this._splitters) {
                        this._computeSplitterThickness(region);
                    }
                    this._layoutChildren();
                }), 50);
                return false;
            }

            var splitterBounds = {
                left: (sidebarLayout ? leftWidth + leftSplitterThickness : 0) + pe.l + "px",
                right: (sidebarLayout ? rightWidth + rightSplitterThickness : 0) + pe.r + "px"
            };

            if (topSplitter) {
                dojo.mixin(topSplitter.style, splitterBounds);
                topSplitter.style.top = topHeight + pe.t + "px";
            }

            if (bottomSplitter) {
                dojo.mixin(bottomSplitter.style, splitterBounds);
                bottomSplitter.style.bottom = bottomHeight + pe.b + "px";
            }

            splitterBounds = {
                top: (sidebarLayout ? 0 : topHeight + topSplitterThickness) + pe.t + "px",
                bottom: (sidebarLayout ? 0 : bottomHeight + bottomSplitterThickness) + pe.b + "px"
            };

            if (leftSplitter) {
                dojo.mixin(leftSplitter.style, splitterBounds);
                leftSplitter.style.left = leftWidth + pe.l + "px";
            }

            if (rightSplitter) {
                dojo.mixin(rightSplitter.style, splitterBounds);
                rightSplitter.style.right = rightWidth + pe.r + "px";
            }

            dojo.mixin(centerStyle, {
                top: pe.t + topHeight + topSplitterThickness + "px",
                left: pe.l + leftWidth + leftSplitterThickness + "px",
                right: pe.r + rightWidth + rightSplitterThickness + "px",
                bottom: pe.b + bottomHeight + bottomSplitterThickness + "px"
            });

            var bounds = {
                top: sidebarLayout ? pe.t + "px" : centerStyle.top,
                bottom: sidebarLayout ? pe.b + "px" : centerStyle.bottom
            };
            dojo.mixin(leftStyle, bounds);
            dojo.mixin(rightStyle, bounds);
            leftStyle.left = pe.l + "px";
            rightStyle.right = pe.r + "px";
            topStyle.top = pe.t + "px";
            bottomStyle.bottom = pe.b + "px";
            if (sidebarLayout) {
                topStyle.left = bottomStyle.left = leftWidth + (this.isLeftToRight() ? leftSplitterThickness : 0) + pe.l + "px";
                topStyle.right = bottomStyle.right = rightWidth + (this.isLeftToRight() ? 0 : rightSplitterThickness) + pe.r + "px";
            } else {
                topStyle.left = bottomStyle.left = pe.l + "px";
                topStyle.right = bottomStyle.right = pe.r + "px";
            }

            // Nodes in IE respond to t/l/b/r, and TEXTAREA doesn't respond in any browser
            var janky = dojo.isIE || dojo.some(this.getChildren(), function(child) {
                return child.domNode.tagName == "TEXTAREA";
            });
            if (janky) {
                // Set the size of the children the old fashioned way, by calling
                // childNode.resize({h: int, w: int}) for each child node)

                var borderBox = function(n, b, s) {
                    n = dojo.byId(n);
                    s = s || dojo.getComputedStyle(n);
                    if (!b) {
                        return dojo._getBorderBox(n, s);
                    }
                    var me = dojo._getMarginExtents(n, s);
                    dojo._setMarginBox(n, b.l, b.t, b.w + me.w, b.h + me.h, s);
                    return null;
                };

                var resizeWidget = function(widget, dim) {
                    if (widget) {
                        (widget.resize ? widget.resize(dim) : dojo.marginBox(widget.domNode, dim));
                    }
                };

                // TODO: use dim passed in to resize() (see _LayoutWidget.js resize())
                // Then can make borderBox setBorderBox(), since no longer need to ever get the borderBox() size
                var thisBorderBox = borderBox(this.domNode, null, cs);

                var containerHeight = thisBorderBox.h - pe.t - pe.b;
                var middleHeight = containerHeight;
                if (this._top) {
                    middleHeight -= topHeight;
                }
                if (this._bottom) {
                    middleHeight -= bottomHeight;
                }
                if (topSplitter) {
                    middleHeight -= topSplitterThickness;
                }
                if (bottomSplitter) {
                    middleHeight -= bottomSplitterThickness;
                }
                var centerDim = { h: middleHeight };

                var sidebarHeight = sidebarLayout ? containerHeight : middleHeight;
                if (leftSplitter) {
                    leftSplitter.style.height = sidebarHeight;
                }
                if (rightSplitter) {
                    rightSplitter.style.height = sidebarHeight;
                }
                resizeWidget(this._leftWidget, {h: sidebarHeight});
                resizeWidget(this._rightWidget, {h: sidebarHeight});

                var containerWidth = thisBorderBox.w - pe.l - pe.r;
                var middleWidth = containerWidth;
                if (this._left) {
                    middleWidth -= leftWidth;
                }
                if (this._right) {
                    middleWidth -= rightWidth;
                }
                if (leftSplitter) {
                    middleWidth -= leftSplitterThickness;
                }
                if (rightSplitter) {
                    middleWidth -= rightSplitterThickness;
                }
                centerDim.w = middleWidth;

                var sidebarWidth = sidebarLayout ? middleWidth : containerWidth;
                if (topSplitter) {
                    topSplitter.style.width = sidebarWidth;
                }
                if (bottomSplitter) {
                    bottomSplitter.style.width = sidebarWidth;
                }
                resizeWidget(this._topWidget, {w: sidebarWidth});
                resizeWidget(this._bottomWidget, {w: sidebarWidth});

                resizeWidget(this._centerWidget, centerDim);
            } else {

                // We've already sized the children by setting style.top/bottom/left/right...
                // Now just need to call resize() on those children so they can re-layout themselves

                // TODO: calling child.resize() without an argument is bad, because it forces
                // the child to query it's own size (even though this function already knows
                // the size), plus which querying the size of a node right after setting it
                // is known to cause problems (incorrect answer or an exception).
                // This is a setback from older layout widgets, which
                // don't do that.  See #3399, #2678, #3624 and #2955, #1988

                var resizeList = {};
                if (changedRegion) {
                    resizeList[changedRegion] = resizeList.center = true;
                    if (/top|bottom/.test(changedRegion) && this.design != "sidebar") {
                        resizeList.left = resizeList.right = true;
                    } else if (/left|right/.test(changedRegion) && this.design == "sidebar") {
                        resizeList.top = resizeList.bottom = true;
                    }
                }

                dojo.forEach(this.getChildren(), function(child) {
                    if (child.resize && (!changedRegion || child.region in resizeList)) {
                        //              console.log(this.id, ": resizing child id=" + child.id + " (region=" + child.region + "), style before resize is " +
                        //                                   "{ t: " + child.domNode.style.top +
                        //                                  ", b: " + child.domNode.style.bottom +
                        //                                  ", l: " + child.domNode.style.left +
                        //                                   ", r: " + child.domNode.style.right +
                        //                                   ", w: " + child.domNode.style.width +
                        //                                   ", h: " + child.domNode.style.height +
                        //                                  "}"
                        //                      );
                        child.resize();
                        //              console.log(this.id, ": after resize of child id=" + child.id + " (region=" + child.region + ") " +
                        //                                   "{ t: " + child.domNode.style.top +
                        //                                  ", b: " + child.domNode.style.bottom +
                        //                                  ", l: " + child.domNode.style.left +
                        //                                   ", r: " + child.domNode.style.right +
                        //                                   ", w: " + child.domNode.style.width +
                        //                                   ", h: " + child.domNode.style.height +
                        //                                  "}"
                        //                      );
                    }
                }, this);
            }
        }
    });

// This argument can be specified for the children of a BorderContainer.
// Since any widget can be specified as a LayoutContainer child, mix it
// into the base widget class.  (This is a hack, but it's effective.)
    dojo.extend(dijit._Widget, {
        // region: String
        //      "top", "bottom", "leading", "trailing", "left", "right", "center".
        //      See the BorderContainer description for details on this parameter.
        region: '',

        // splitter: Boolean
        splitter: false,

        // minSize: Number
        minSize: 0,

        // maxSize: Number
        maxSize: Infinity
    });

    dojo.require("dijit._Templated");

    dojo.declare("dijit.layout._Splitter", [ dijit._Widget, dijit._Templated ],
    {
        /*=====
         container: null,
         child: null,
         region: null,
         =====*/

        // live: Boolean
        //      If true, the child's size changes and the child widget is redrawn as you drag the splitter;
        //      otherwise, the size doesn't change until you drop the splitter (by mouse-up)
        live: true,

        // summary: A draggable spacer between two items in a BorderContainer
        templateString: '<div class="dijitSplitter" dojoAttachEvent="onkeypress:_onKeyPress,onmousedown:_startDrag" tabIndex="0" waiRole="separator"><div class="dijitSplitterThumb"></div></div>',

        postCreate: function() {
            this.inherited(arguments);
            this.horizontal = /top|bottom/.test(this.region);
            dojo.addClass(this.domNode, "dijitSplitter" + (this.horizontal ? "H" : "V"));
//      dojo.addClass(this.child.domNode, "dijitSplitterPane");
//      dojo.setSelectable(this.domNode, false); //TODO is this necessary?

            this._factor = /top|left/.test(this.region) ? 1 : -1;
            this._minSize = this.child.minSize;

            this._computeMaxSize();
            //TODO: might be more accurate to recompute constraints on resize?
            this.connect(this.container, "layout", dojo.hitch(this, this._computeMaxSize));

            this._cookieName = this.container.id + "_" + this.region;
            if (this.container.persist) {
                // restore old size
                var persistSize = dojo.cookie(this._cookieName);
                if (persistSize) {
                    this.child.domNode.style[this.horizontal ? "height" : "width"] = persistSize;
                }
            }
        },

        _computeMaxSize: function() {
            var dim = this.horizontal ? 'h' : 'w';
            var available = dojo.contentBox(this.container.domNode)[dim] - (this.oppNode ? dojo.marginBox(this.oppNode)[dim] : 0);
            this._maxSize = Math.min(this.child.maxSize, available);
        },

        _startDrag: function(e) {
            if (!this.cover) {
                this.cover = dojo.doc.createElement('div');
                dojo.addClass(this.cover, "dijitSplitterCover");
                dojo.place(this.cover, this.child.domNode, "after");
            } else {
                this.cover.style.zIndex = 1;
            }

            // Safeguard in case the stop event was missed.  Shouldn't be necessary if we always get the mouse up.
            if (this.fake) {
                dojo._destroyElement(this.fake);
            }
            if (!(this._resize = this.live)) { //TODO: disable live for IE6?
                // create fake splitter to display at old position while we drag
                (this.fake = this.domNode.cloneNode(true)).removeAttribute("id");
                dojo.addClass(this.domNode, "dijitSplitterShadow");
                dojo.place(this.fake, this.domNode, "after");
            }
            dojo.addClass(this.domNode, "dijitSplitterActive");

            //Performance: load data info local vars for onmousevent function closure
            var factor = this._factor,
                    max = this._maxSize,
                    min = this._minSize || 10;
            var axis = this.horizontal ? "pageY" : "pageX";
            var pageStart = e[axis];
            var splitterStyle = this.domNode.style;
            var dim = this.horizontal ? 'h' : 'w';
            var childStart = dojo.marginBox(this.child.domNode)[dim];
            var splitterStart = parseInt(this.domNode.style[this.region]);
            var resize = this._resize;
            var region = this.region;
            var mb = {};
            var childNode = this.child.domNode;
            var layoutFunc = dojo.hitch(this.container, this.container._layoutChildren);

            var de = dojo.doc.body;
            this._handlers = (this._handlers || []).concat([
                dojo.connect(de, "onmousemove", this._drag = function(e, forceResize) {
                    var delta = e[axis] - pageStart,
                            childSize = factor * delta + childStart,
                            boundChildSize = Math.max(Math.min(childSize, max), min);

                    if (resize || forceResize) {
                        mb[dim] = boundChildSize;
                        // TODO: inefficient; we set the marginBox here and then immediately layoutFunc() needs to query it
                        dojo.marginBox(childNode, mb);
                        layoutFunc(region);
                    }
                    splitterStyle[region] = factor * delta + splitterStart + (boundChildSize - childSize) + "px";
                }),
                dojo.connect(de, "onmouseup", this, "_stopDrag")
            ]);
            dojo.stopEvent(e);
        },

        _stopDrag: function(e) {
            try {
                if (this.cover) {
                    this.cover.style.zIndex = -1;
                }
                if (this.fake) {
                    dojo._destroyElement(this.fake);
                }
                dojo.removeClass(this.domNode, "dijitSplitterActive");
                dojo.removeClass(this.domNode, "dijitSplitterShadow");
                this._drag(e); //TODO: redundant with onmousemove?
                this._drag(e, true);
            } finally {
                this._cleanupHandlers();
                delete this._drag;
            }

            if (this.container.persist) {
                dojo.cookie(this._cookieName, this.child.domNode.style[this.horizontal ? "height" : "width"]);
            }
        },

        _cleanupHandlers: function() {
            if(this._handlers){
                dojo.forEach(this._handlers, dojo.disconnect);
            }
            delete this._handlers;
        },

        _onKeyPress: function(/*Event*/ e) {
            // should we apply typematic to this?
            this._resize = true;
            var horizontal = this.horizontal;
            var tick = 1;
            var dk = dojo.keys;
            switch (e.charOrCode) {
                case horizontal ? dk.UP_ARROW : dk.LEFT_ARROW:
                    tick *= -1;
                    break;
                case horizontal ? dk.DOWN_ARROW : dk.RIGHT_ARROW:
                    break;
                default:
//              this.inherited(arguments);
                    return;
            }
            var childSize = dojo.marginBox(this.child.domNode)[ horizontal ? 'h' : 'w' ] + this._factor * tick;
            var mb = {};
            mb[ this.horizontal ? "h" : "w"] = Math.max(Math.min(childSize, this._maxSize), this._minSize);
            dojo.marginBox(this.child.domNode, mb);
            this.container._layoutChildren(this.region);
            dojo.stopEvent(e);
        },

        destroy: function() {
            this._cleanupHandlers();
            delete this.child;
            delete this.container;
            delete this.fake;
            this.inherited(arguments);
        }
    });
};

genropatches.tree = function() {
    dojo.require('dijit.Tree');
    dijit.Tree.prototype._expandNode_replaced=dijit.Tree.prototype._expandNode;
    dijit.Tree.prototype._expandNode = function(node) {
        if(node.item && node.item._resolver && node.item._resolver.expired()){
            node.state = 'UNCHECKED';
        }
        return this._expandNode_replaced(node)
    }
    dijit._TreeNode.prototype.setLabelNode = function(label) {
        this.labelNode.innerHTML = "";
        var itemattr = this.item.attr || {};
        if ((typeof(label) == 'string') && (label.indexOf('innerHTML:') >= 0)) {
            this.labelNode.innerHTML = label.replace('innerHTML:', '');
        }
        else {
            this.labelNode.appendChild(dojo.doc.createTextNode(label));
        }
        ;
        if ('node_class' in itemattr) {
            dojo.addClass(this.domNode, itemattr.node_class);
        }
        if (itemattr.tip){
            this.domNode.setAttribute('title',itemattr.tip);
        }
        var sourceNode = this.tree.sourceNode;
        var draggable = sourceNode.attr.draggable;
        //var nodeattrs=this.tree.gnrNodeAttributes;
        if (draggable && (this.item instanceof gnr.GnrBagNode)) {
            this.domNode.setAttribute('draggable', draggable);
        }
        /*var dropTarget=sourceNode.attr.dropTarget
         if (dropTarget && (this.item instanceof gnr.GnrBagNode)){
         this.contentNode.setAttribute('droppable',droppable);
         }*/
    };

};


genropatches.parseNumbers = function() {
    dojo.require('dojo.number');

    dojo.number._integerRegexp = function(/*dojo.number.__IntegerRegexpFlags?*/flags) {
        // summary:
        //		Builds a regular expression that matches an integer

        // assign default values to missing paramters
        flags = flags || {};
        if (!("signed" in flags)) {
            flags.signed = [true, false];
        }
        if (!("separator" in flags)) {
            flags.separator = "";
        } else if (!("groupSize" in flags)) {
            flags.groupSize = 3;
        }
        // build sign RE
        var signRE = dojo.regexp.buildGroupRE(flags.signed,
                                             function(q) {
                                                 return q ? "[-+]" : "";
                                             },
                true
                );

        // number RE
        var numberRE = dojo.regexp.buildGroupRE(flags.separator,
                                               function(sep) {
                                                   if (!sep) {
                                                       return "(?:\\d+)";
                                                   }

                                                   sep = dojo.regexp.escapeString(sep);
                                                   if (sep == " ") {
                                                       sep = "\\s";
                                                   }
                                                   else if (sep == "\xa0") {
                                                       sep = "\\s\\xa0";
                                                   }

                                                   var grp = flags.groupSize, grp2 = flags.groupSize2;
                                                   if (grp2) {
                                                       var grp2RE = "(?:0|[1-9]\\d{0," + (grp2 - 1) + "}(?:[" + sep + "]\\d{" + grp2 + "})*[" + sep + "]\\d{" + grp + "})";
                                                       return ((grp - grp2) > 0) ? "(?:" + grp2RE + "|(?:0|[1-9]\\d{0," + (grp - 1) + "}))" : grp2RE;
                                                   }
                                                   return "(?:0|[1-9]\\d{0," + (grp - 1) + "}(?:[" + sep + "]\\d{" + grp + "})*)";
                                               },
                true
                );

        // integer RE
        return signRE + numberRE; // String
    };
};
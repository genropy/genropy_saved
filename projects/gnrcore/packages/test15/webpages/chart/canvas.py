# -*- coding: UTF-8 -*-
# 
"""Canvas"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'
    
    def test_1_basic(self, pane):
        """Basic canvas"""
        pane=pane.div(background_color='white',height='400px')
        fb=pane.formBuilder(cols=4,lblpos='T',border_spacing='6px')
        kwargs=dict(width='200px',height='150px',
                                            border='1px solid silver',shadow='2px 2px 4px silver')
        
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                            ctx.fillStyle = "rgb(200,0,0)";
                                            ctx.fillRect (10, 10, 55, 50);

                                            ctx.fillStyle = "rgba(0, 0, 200, 0.5)";
                                            ctx.fillRect (30, 30, 55, 50);""",lbl='Test 1',**kwargs)
                                            
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                           ctx.fillRect(25,25,100,100);
                                           ctx.clearRect(45,45,60,60);
                                           ctx.strokeRect(50,50,50,50);""",lbl='Test 2',**kwargs)
                                           
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                            ctx.beginPath();
                                            ctx.moveTo(75,50);
                                            ctx.lineTo(100,75);
                                            ctx.lineTo(100,25);
                                            ctx.fill();""",lbl='Test 3',**kwargs)
                                            
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                            ctx.beginPath();
                                            ctx.arc(75,75,50,0,Math.PI*2,true); // Outer circle
                                            ctx.moveTo(110,75);
                                            ctx.arc(75,75,35,0,Math.PI,false);   // Mouth (clockwise)
                                            ctx.moveTo(65,65);
                                            ctx.arc(60,65,5,0,Math.PI*2,true);  // Left eye
                                            ctx.moveTo(95,65);
                                            ctx.arc(90,65,5,0,Math.PI*2,true);  // Right eye
                                            ctx.stroke();""",lbl='Test 4',**kwargs)
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                                 ctx.beginPath();
                                                 ctx.moveTo(25,25);
                                                 ctx.lineTo(105,25);
                                                 ctx.lineTo(25,105);
                                                 ctx.fill();
                                                 ctx.beginPath();
                                                 ctx.moveTo(125,125);
                                                 ctx.lineTo(125,45);
                                                 ctx.lineTo(45,125);
                                                 ctx.closePath();
                                                 ctx.stroke();
                                            """,lbl='Test 5',**kwargs)
                                         
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                 r(var i=0;i<4;i++){
                                  for(var j=0;j<3;j++){
                                  ctx.beginPath();
                                  var x              = 25+j*50;               // x coordinate
                                  var y              = 25+i*50;               // y coordinate
                                  var radius         = 20;                    // Arc radius
                                  var startAngle     = 0;                     // Starting point on circle
                                  var endAngle       = Math.PI+(Math.PI*j)/2; // End point on circle
                                  var anticlockwise  = i%2==0 ? false : true; // clockwise or anticlockwise
                                 
                                  ctx.arc(x,y,radius,startAngle,endAngle, anticlockwise);
                                 
                                  if (i>1){
                                      ctx.fill();
                                      } else {
                                      ctx.stroke();
                                      }
                                      }
                                  }""",lbl='Test 6 ',**kwargs)
     

        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                    ctx.beginPath();
                                    ctx.moveTo(75,40);
                                    ctx.bezierCurveTo(75,37,70,25,50,25);
                                    ctx.bezierCurveTo(20,25,20,62.5,20,62.5);
                                    ctx.bezierCurveTo(20,80,40,102,75,120);
                                    ctx.bezierCurveTo(110,102,130,80,130,62.5);
                                    ctx.bezierCurveTo(130,62.5,130,25,100,25);
                                    ctx.bezierCurveTo(85,25,75,37,75,40);
                                    ctx.fill()""",lbl='Test 7 ',**kwargs)

    def test_2_special(self, pane):
        """Basic canvas"""
        pane=pane.div(background_color='white',height='600px')
        fb=pane.formBuilder(cols=4,lblpos='T',border_spacing='6px')
        kwargs=dict(width='700px',height='500px',
                                            border='1px solid silver',shadow='2px 2px 4px silver')
        fb.canvas(onCreated="""var ctx =widget.getContext('2d');
                                            var x = 188;
                                            var y = 130;
                                            var width = 200;
                                            var height = 137;
                                            var imageObj = new Image();
                                            imageObj.onload = function() {
                                                ctx.drawImage(imageObj, x, y, width, height);
                                            };
                                            imageObj.src = "http://www.html5canvastutorials.com/demos/assets/darth-vader.jpg";
""",lbl='Test X',**kwargs)




    def test_3_special(self, pane):
        """Basic canvas"""
        pane=pane.div(background_color='white',height='600px')
        fb=pane.formBuilder(cols=4,lblpos='T',border_spacing='6px')
        kwargs=dict(width='700px',height='500px',
                                            border='1px solid silver',shadow='2px 2px 4px silver')
        fb.canvas(onCreated="""var canvas=widget;var context =widget.getContext('2d');
                               var arc=function(ctx,cx,cy,radius,start,end,linew){
                                         ctx.arc(cx, cy, radius,  start * Math.PI,  end * Math.PI, true);
                                         ctx.lineWidth = linew;
                                         ctx.strokeStyle = "black";
                                         ctx.stroke();
                                         }
                                    line=function(ctx,x0,y0,x1,y1,linew){
                                         ctx.moveTo(x0, y0);
                                         ctx.lineTo(x1, y1);
                                         ctx.lineWidth = linew;
                                         ctx.strokeStyle = "black";
                                         ctx.stroke();
                                    }
                                        var w=canvas.width
                                        var h=canvas.height
                                        
                                        arc(context,w/2,h/2,40,0,-0.5,10)

""",lbl='Test X',**kwargs)


    def test_4_special(self, pane):
        """Basic canvas"""
        pane=pane.div(background_color='white',height='600px')
        fb=pane.formBuilder(cols=4,lblpos='T',border_spacing='6px')
        kwargs=dict(width='700px',height='500px',
                                            border='1px solid silver',shadow='2px 2px 4px silver')
        fb.canvas(onCreated="""var canvas=widget;var context =widget.getContext('2d');
        
                                roundrect=function(ctx,cx,cy,width,height,radius,stroke,fill){
                                        var x=cx-width/2
                                        var y=cy-height/2
                                        ctx.save();	// save the context so we don't mess up others
                                        ctx.beginPath();

                                        // draw top and top right corner
                                        ctx.moveTo(x+radius,y);
                                        ctx.arcTo(x+width,y,x+width,y+radius,radius);

                                        // draw right side and bottom right corner
                                        ctx.arcTo(x+width,y+height,x+width-radius,y+height,radius); 

                                        // draw bottom and bottom left corner
                                        ctx.arcTo(x,y+height,x,y+height-radius,radius);

                                        // draw left and top left corner
                                        ctx.arcTo(x,y,x+radius,y,radius);

                                        if(fill){
	                                        ctx.fill();
                                        }
                                        if(stroke){
	                                        ctx.stroke();
                                        }
                                        ctx.restore();	// restore context to what it was on entry
                                }
                                 roundhalfrect=function(ctx,cx,cy,width,height,radius,stroke,fill){
                                        var x=cx-width/2
                                        var y=cy-height/2
                                        ctx.save();	// save the context so we don't mess up others
                                        ctx.beginPath();

                                        ctx.moveTo(x+width+20,y+radius+10);
                                        ctx.lineTo(x+width,y+radius+10);
                                       ctx.arcTo(x+width, y+height,   x+width-radius,y+height,radius); 
                                       ctx.lineTo(x+width/2, y+height)
                                       
                                       ctx.moveTo(x-20,y+radius+10);
                                       ctx.lineTo(x,y+radius+10);
                                       ctx.arcTo(x, y+height,   x+width-radius,y+height,radius); 
                                       ctx.lineTo(x+width/2, y+height)

                                        if(fill){
	                                        ctx.fill();
                                        }
                                        if(stroke){
	                                        ctx.stroke();
                                        }
                                        ctx.restore();	// restore context to what it was on entry
                                }
                                context.strokeStyle='rgb(40,40,40)';
                                context.fillStyle='rgb(0,150,0)';
                                context.lineWidth=8;
                                var cx=canvas.width/2;
                                var cy=canvas.height/2
                                var naso_w=100
                                var naso_h=80
                                var naso_r=25
                                var muso_w=130
                                var muso_h=120
                                var muso_r=40
                                var narice_h=25
                                var narice_w=25
                                var narice_r=10
                                roundrect(context,cx,cy,naso_w,naso_h,naso_r,true,false)
                                roundrect(context,cx-naso_w/4,cy,narice_w,narice_h,narice_r,true,false)
                                roundrect(context,cx+naso_w/4,cy,narice_h,narice_w,narice_r,true,false)
                                
                                roundhalfrect(context,cx,cy,muso_w,muso_h,muso_r,true,false)
                                    
                        

""",lbl='Test X',**kwargs)










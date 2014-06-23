var gnrcanvas={

    muzzleline:function(ctx,cx,cy,w,h,r,b,k,rm){
        var r=r +b-rm ;
        var w=w +2*b;
        var h=h +2*b;
        ctx.beginPath();
        ctx.moveTo(cx-w/2-k,cy);
        ctx.lineTo(cx-w/2-rm,cy);
        ctx.arc(cx-w/2-rm, cy+rm, rm, 1.5 * Math.PI, 2.0 * Math.PI, false);
        ctx.arc(cx-w/2+r, cy+rm, r, 3 * Math.PI, 2.5 * Math.PI, true);
        ctx.lineTo(cx+w/2-r, cy+h/2, r, 3 * Math.PI, 2.5 * Math.PI, true);
        ctx.arc(cx+w/2-r, cy+rm, r, 2.5 * Math.PI, 2.0 * Math.PI, true);
        ctx.arc(cx+w/2+rm, cy+rm, rm, 3 * Math.PI, 1.5 * Math.PI, false);
        ctx.lineTo(cx+w/2+k,cy);
        ctx.stroke()
    },
     topline:function(ctx,cx,cy,w,h,r,b,th,dr,side){
        var r=r+b
        var dx=(w+b*2)/2-r
        var dy=(h+b*2)/2-r
        ctx.beginPath();
        if (side=='L'){
            ctx.moveTo(cx-dx,cy-h/2-b-th);
            ctx.arc(cx-dx,cy-dy,r,1.5 * Math.PI,(1.5-dr) * Math.PI, true);
        }else{
            ctx.moveTo(cx+dx,cy-h/2-b-th);
            ctx.arc(cx+dx,cy-dy,r,1.5 * Math.PI, (1.5+dr) * Math.PI, false)
        }
        
        ctx.stroke()
     },
     roundrect:function(ctx,cx,cy,w,h,r){
        var dx=w/2-r
        var dy=h/2-r
        ctx.beginPath();
        ctx.moveTo(cx-dx,cy-h/2);
        ctx.lineTo(cx+dx,cy-h/2);
        ctx.arc(cx+dx, cy-dy, r, 1.5 * Math.PI, 2.0 * Math.PI, false);
        ctx.lineTo(cx+dx+r,cy+dy);
        ctx.arc(cx+dx, cy+dy, r, 2.0 * Math.PI, 2.5 * Math.PI, false);
        ctx.lineTo(cx-dx,cy+dy+r);
        ctx.arc(cx-dx, cy+dy, r, 2.5 * Math.PI, 3.0 * Math.PI, false);
        ctx.lineTo(cx-dx-r,cy-dy);
        ctx.arc(cx-dx, cy-dy, r, 3.0 * Math.PI, 3.5 * Math.PI, false);
        ctx.stroke()
     },
   pigbackground:function(ctx,cx,cy,pig){
        var grad = ctx.createRadialGradient(cx,cy,0,cx,cy,pig.nose.width*2);
        grad.addColorStop(0, 'rgba(255,255,255,1)');
       // grad.addColorStop(0.9, '#019F62');
        grad.addColorStop(1, 'rgba(200,230,255,0)');
        //grad.addColorStop(1, 'rgba(255,255,255,1)');
        ctx.fillStyle = grad;
        ctx.fillRect(0,0,cx*2,cy*2);
   },
   pigtext:function(ctx,cx,cy,pig,s){
       ctx.textAlign= 'center'
       ctx.font=  parseInt(24*s)+"px arial black ";
       ctx.textBaseline = "top";
       ctx.fillStyle = "black";
       ctx.fillText('Genropy', cx, cy+pig.nose.height/2+pig.muzzle.border)
   },
   genropig:function(domnode,kw){
        var context =domnode.getContext('2d');
        var cx= domnode.width/2
        var cy= domnode.height/2
        var s=kw.size/100
        var pig={ nose:{width:90*s,height:70*s,radius:35*s},
                  nostril:{width:25*s,height:25*s,radius:12*s,distance:36*s},
                  muzzle:{border:10*s,sideradius:3*s,sidewidth:10*s},
                  top:{height:10*s,rad:0.3}
        }
        this.pigbackground(context,cx,cy,pig)
        context.lineWidth=6*s;
        context.strokeStyle=kw.strokeStyle;
        context.fillStyle=kw.fillStyle
        this.roundrect(context,cx,cy,pig.nose.width,pig.nose.height,pig.nose.radius)
        this.roundrect(context,cx-pig.nostril.distance/2,cy,pig.nostril.width,pig.nostril.height,pig.nostril.radius)
        this.roundrect(context,cx+pig.nostril.distance/2,cy,pig.nostril.width,pig.nostril.height,pig.nostril.radius)
        this.muzzleline(context,cx,cy,pig.nose.width,pig.nose.height,pig.nose.radius,pig.muzzle.border,pig.muzzle.sidewidth,pig.muzzle.sideradius)
        this.topline(context,cx,cy,pig.nose.width,pig.nose.height,pig.nose.radius,pig.muzzle.border,pig.top.height,pig.top.rad,'L')
        this.topline(context,cx,cy,pig.nose.width,pig.nose.height,pig.nose.radius,pig.muzzle.border,pig.top.height,pig.top.rad,'R')
        //this.pigtext(context,cx,cy,pig,s)
    }
}
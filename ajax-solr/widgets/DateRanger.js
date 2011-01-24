//Date range picker without a date picker but using sliders
//Dual float or int widget
//with 2 sliders

//we have a one day offset problem may be due to inclusive range ussues FIX
(function ($) {

AjaxSolr.DateRangerWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
    console.log(" THIS.FIELD "+this.id);
    var d1=Date.today().set({year:this.themin, month:0, day:1});
    var d2=Date.today().set({year:this.themax+1, month:0, day:1});
    console.log("DATE "+d1+"-"+d2);
    var tmin=0;
    var tmax=0;
    for (var y=this.themin; y < this.themax+1; y++){
        for (var m=0; m<12;m++){
            var daysinmonth=Date.getDaysInMonth(y,m);
            tmax=tmax+daysinmonth;
        }
    }
    //tmax=tmax-1;//so that 1 would represent 2nd Jan not 1st Jan
    //var tmax=d2-d1;
    console.log("TMAX is "+tmax);
    var convertit=function (myvar){
        var theinitialdate=myvar;
        console.log("setting up func "+myvar);
        var a=function(theday){
            var thedate=theinitialdate.clone().addDays(theday);
            console.log(theinitialdate+"THEDATE "+thedate+" THEDAY "+theday);
            return thedate;
        };
        return a;
    }(d1);
    
    var pqvalues=self.manager.store.values('fq');
    var ourmin=undefined;
    var ourmax=undefined;
    if (pqvalues.length > 0){
        for (var tval in pqvalues){
            console.log(">>>>>>"+pqvalues[tval]);
            var splitfq=pqvalues[tval].split(':');
            console.log("??? "+splitfq[0]);
            var vcount=0;
            if (splitfq[0]===this.field){
                //console.log("splitfq here is "+splitfq[1]);
                var splitstring=splitfq.slice(1).join(":");
                console.log("splitstring="+splitstring);
                var splitonto=splitstring.split('TO');
                console.log(splitonto[0], splitonto[1]);
                var ourminiso=splitonto[0].trim().substr(1);
                var tempmax=splitonto[1].trim();
                var ourmaxiso=tempmax.slice(0,tempmax.length -1);
                var ourmindate=new Date(ourminiso);
                var spanmin = new TimeSpan(ourmindate - d1);
                var ourmaxdate=new Date(ourmaxiso);
                var spanmax = new TimeSpan(ourmaxdate - d1);
                ourmin=spanmin.getDays();
                ourmax=spanmax.getDays();
                console.log("OURMINDATE "+ourmin+"---"+ourmax);
                vcount=vcount+1;
            }
        }
        if (ourmin==undefined){
            ourmin=tmin;
        }
        if (ourmax==undefined){
            ourmax=tmax;
        }
    } else {
        ourmin=tmin;
        ourmax=tmax;
    }
    console.log ("MIN MAX "+ourmin+" "+ourmax);
    
    $(this.target).slider('destroy').slider({
        'range':true,
        'max': tmax,
        'min': tmin,
        'step':this.thestep,
        'values':[ourmin,ourmax],
        slide: function( event, ui ) {
                console.log("IN SLIDE "+ui.values);
                $( "#"+self.id+"_amount" ).text(convertit(ui.values[0]).toString("d-MMM-yyyy")+'-'+convertit(ui.values[1]).toString("d-MMM-yyyy") );
        },
        stop: function( event, ui ) {
                    console.log("ONSTOP"+ui.values);
                    //self.manager.store.addByValue('fq', facet.field + ':' + facet.value)
                    //console.log(self.manager.store.get('facet.pubyear'));
                    if (self.manager.store.addByValue('fq',self.field+':['+convertit(ui.values[0]).toISOString()+' TO '+convertit(ui.values[1]).toISOString()+']')) {
                        self.manager.doRequest(0);
                    }
        }
    });
    $( "#"+this.id+"_amount" ).text(convertit($(this.target).slider( "values" ,0)).toString("d-MMM-yyyy")+'-'+ convertit($(this.target).slider( "values" ,1)).toString("d-MMM-yyyy"));
  }
});

})(jQuery);

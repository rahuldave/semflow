//Date range picker without a date picker but using sliders
//Dual float or int widget
//with 2 sliders

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
            var thedate=theinitialdate.clone().addDays(theday)
            console.log(theinitialdate+"THEDATE "+thedate+" THEDAY "+theday);
            return thedate;
        };
        return a;
    }(d1);
    $(this.target).slider({
        'range':true,
        'max': tmax,
        'min': tmin,
        'step':this.thestep,
        'values':[tmin,tmax],
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

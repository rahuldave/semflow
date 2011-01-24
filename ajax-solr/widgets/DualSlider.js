//Dual float or int widget
//with 2 sliders
(function ($) {

AjaxSolr.DualSliderWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
    console.log(" THIS.DUALSLIDER.FIELD "+this.id);
    var pqvalues=self.manager.store.values('fq');
    var themin=undefined;
    var themax=undefined;
    if (pqvalues.length > 0){
        for (var tval in pqvalues){
            var splitfq=pqvalues[tval].split(':');
            console.log("??? "+splitfq[0]);
            var vcount=0;
            if (splitfq[0]===this.field){
                var splitonto=splitfq[1].split('TO');
                themin=splitonto[0].trim().substr(1);
                var tempmax=splitonto[1].trim();
                themax=tempmax.slice(0,tempmax.length -1);
                vcount=vcount+1;
            }
        }
        if (themin==undefined){
            themin=this.themin;
        }
        if (themax==undefined){
            themax=this.themax;
        }
    } else {
        themin=this.themin;
        themax=this.themax;
    }
    console.log ("MIN MAX "+themin+" "+themax);
    $(this.target).slider('destroy').slider({
        'range':true,
        'max': this.themax,
        'min': this.themin,
        'step':this.thestep,
        'values':[themin,themax],
        slide: function( event, ui ) {
                console.log('SLIDE EVENT');
                $( "#"+self.id+"_amount" ).val(ui.values[0]+'-'+ui.values[1] );
        },
        stop: function( event, ui ) {
                    console.log("ONSTOP"+ui.values);
                    //self.manager.store.addByValue('fq', facet.field + ':' + facet.value)
                    //console.log(self.manager.store.get('facet.pubyear'));
                    if (self.manager.store.addByValue('fq',self.field+':['+ui.values[0]+' TO '+ui.values[1]+']')) {
                        self.manager.doRequest(0);
                    }
        }
    });
    $( "#"+this.id+"_amount" ).val($(this.target).slider( "values" ,0)+'-'+ $(this.target).slider( "values" ,1));
  }
});

})(jQuery);

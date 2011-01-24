//with 2 sliders
(function ($) {

AjaxSolr.YearWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
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
            themin=this.manager.store.get('facet.pubyear.start').val();
        }
        if (themax==undefined){
            themax=this.manager.store.get('facet.pubyear.end').val();
        }
    } else {
        themin=this.manager.store.get('facet.pubyear.start').val();
        themax=this.manager.store.get('facet.pubyear.end').val();
    }
    console.log ("MIN MAX "+themin+" "+themax);
    $(this.target).slider("destroy").slider({
        'range':true,
        'max': this.manager.store.get('facet.pubyear.end').val(),
        'min': this.manager.store.get('facet.pubyear.start').val(),
        'step':this.manager.store.get('facet.pubyear.step').val(),
        //'values':[this.manager.store.get('facet.pubyear.start').val(),this.manager.store.get('facet.pubyear.end').val()],
        'values':[themin, themax],
        slide: function( event, ui ) {
                $( "#amount" ).val(ui.values[0]+'-'+ui.values[1] );
        },
        stop: function( event, ui ) {
                    console.log("ONSTOP"+ui.values);
                    //self.manager.store.addByValue('fq', facet.field + ':' + facet.value)
                    //console.log(self.manager.store.get('facet.pubyear'));
                    if (self.manager.store.addByValue('fq',self.manager.store.get('facet.pubyear').val()+':['+ui.values[0]+' TO '+ui.values[1]+']')) {
                        self.manager.doRequest(0);
                    }
        }
    });
    $( "#amount" ).val($(this.target).slider( "values" ,0)+'-'+ $(this.target).slider( "values" ,1));
  }
});

})(jQuery); 

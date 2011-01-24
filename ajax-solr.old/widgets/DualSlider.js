//Dual float or int widget
//with 2 sliders
(function ($) {

AjaxSolr.DualSliderWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
    console.log(" THIS.FIELD "+this.id);
    $(this.target).slider({
        'range':true,
        'max': this.themax,
        'min': this.themin,
        'step':this.thestep,
        'values':[this.themin,this.themax],
        slide: function( event, ui ) {
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

//with 2 sliders
(function ($) {

AjaxSolr.YearWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
    $(this.target).slider({
        'range':true,
        'max': this.manager.store.get('facet.pubyear.end').val(),
        'min': this.manager.store.get('facet.pubyear.start').val(),
        'step':this.manager.store.get('facet.pubyear.step').val(),
        'values':[this.manager.store.get('facet.pubyear.start').val(),this.manager.store.get('facet.pubyear.end').val()],
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

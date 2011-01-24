(function ($) {

AjaxSolr.YearWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    var self = this;
    $(this.target).slider({
        'max': this.manager.store.get('facet.pubyear.end').val(),
        'min': this.manager.store.get('facet.pubyear.start').val(),
        'step':this.manager.store.get('facet.pubyear.step').val(),
        'value':1995,
        slide: function( event, ui ) {
                $( "#amount" ).val(ui.value );
        },
        stop: function( event, ui ) {
                    console.log("ONSTOP"+ui.value);
                    //self.manager.store.addByValue('fq', facet.field + ':' + facet.value)
                    //console.log(self.manager.store.get('facet.pubyear'));
                    if (self.manager.store.addByValue('fq',self.manager.store.get('facet.pubyear').val()+':'+ui.value)) {
                        self.manager.doRequest(0);
                    }
        }
    });
    $( "#amount" ).val($(this.target).slider( "value" ) );
  }
});

})(jQuery);

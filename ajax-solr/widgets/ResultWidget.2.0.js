(function ($) {

AjaxSolr.ResultWidget = AjaxSolr.AbstractWidget.extend({
  afterRequest: function () {
    $(this.target).empty();
    for (var i = 0, l = this.manager.response.response.docs.length; i < l; i++) {
      var doc = this.manager.response.response.docs[i];
      $(this.target).append(AjaxSolr.theme('result', doc, AjaxSolr.theme('snippet', doc), 
		AjaxSolr.theme('title', doc),AjaxSolr.theme('pivot', doc, 
		this.facetHandler('bibcode', doc.bibcode)), this.moreHandler(doc), this.lessHandler(doc)));
      //$(this.target).append(AjaxSolr.theme('result', doc, "DOGDOG"));
      var items = [];
      //alert(doc.keywords_s);
      var gaga=this.facetLinks("keywords_s", doc.keywords_s);
      items.concat(gaga);
      //console.log(gaga.length+","+items.length);
      AjaxSolr.theme('list_items', '#links_' + doc.id, gaga, "| ");
    }
  },
  facetLinks: function (facet_field, facet_values) {
    var links = [];
    if (facet_values) {
        for (var i = 0, l = facet_values.length; i < l; i++) {
            links.push(AjaxSolr.theme('facet_link', '"'+facet_values[i]+'"', this.facetHandler(facet_field, '"'+facet_values[i]+'"')));
        }
    }
    //alert(links);
    return links;
  },
  moreHandler: function(doc){
	var self = this;
	var thedoc=doc;
	return function() {
		$('#am_'+thedoc.id).hide();
		$('#p_'+thedoc.id).show();		
		$('#al_'+thedoc.id).show();
		return false;
	};
  },
  lessHandler: function(doc){ 
	var self = this;
	var thedoc=doc;
	return function() {
		$('#am_'+thedoc.id).show();
		$('#p_'+thedoc.id).hide();
		$('#al_'+thedoc.id).hide();
		return false;
	};
  },
  facetHandler: function (facet_field, facet_value) {
    var self = this;
    return function () {
	console.log("For facet "+facet_field+" Trying value "+facet_value);
        self.manager.store.remove('fq');
        self.manager.store.addByValue('fq', facet_field + ':' + facet_value);
        self.manager.doRequest(0);
        return false;
    };
  },
  init: function () {
	//$('a.more').click(alert("Hi"));
    /*$('a.more').live(function () {
        $(this).toggle(function () {
            $(this).parent().find('span.abstract').show();
            $(this).text('less');
            return false;
        }, function () {
            $(this).parent().find('span.abstract').hide();
            $(this).text('more');
            return false;
        });
    });*/
  },
  beforeRequest: function () {
    $(this.target).html($('<img/>').attr('src', 'images/ajax-loader.gif'));
  }
});

})(jQuery);

(function ($) {

AjaxSolr.TagcloudWidget = AjaxSolr.AbstractFacetWidget.extend({
  justthisfacetHandler: function (facet_field, facet_value) {
    var self = this;
    return function () {
        self.manager.store.remove('fq');
        self.manager.store.addByValue('fq', facet_field + ':' + facet_value);
        self.manager.doRequest(0);
        return false;
    };
  },
  afterRequest: function () {
     console.log(">>>"+this.manager.response.facet_counts.facet_fields);
    if (this.manager.response.facet_counts.facet_fields[this.field] === undefined) {
      $(this.target).html(AjaxSolr.theme('no_items_found'));
      return;
    }

    var maxCount = 0;
    var objectedItems = [];
    for (var facet in this.manager.response.facet_counts.facet_fields[this.field]) {
      var count = parseInt(this.manager.response.facet_counts.facet_fields[this.field][facet]);
      if (count > maxCount) {
        maxCount = count;
      }
      objectedItems.push({ facet: facet, count: count });
    }
    objectedItems.sort(function (a, b) {
      return a.facet < b.facet ? -1 : 1;
    });

    $(this.target).empty();
    for (var i = 0, l = objectedItems.length; i < l; i++) {
      var facet = objectedItems[i].facet;
      var $tagthemelist=AjaxSolr.theme('tag', facet, objectedItems[i].count, parseInt(objectedItems[i].count / maxCount * 10), this.clickHandler(facet), this.justthisfacetHandler(this.field, facet));
      //$(this.target).append($tagthemelist[0]);
      //$(this.target).append($tagthemelist[1]);
      //$(this.target).append($tagthemelist[2]);
      $(this.target).append($tagthemelist);
    }
  }
});

})(jQuery);

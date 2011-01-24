(function ($) {

AjaxSolr.CurrentSearchWidget = AjaxSolr.AbstractWidget.extend({
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
    var self = this;
    var links = [];
    console.log("+++++++++++++++++++++++++++++++++ in csw afterrequest "+this.ffields);
    var fq = this.manager.store.values('fq');
    var oldfqs={};
    var likefq=[];
    for (var i = 0, l = fq.length; i < l; i++) {
      var $link=$('<a href="#"/>').text('(x) ' + fq[i]).click(self.removeFacet(fq[i]));
      var $span=$('<span></span>');
      var splitfq=fq[i].split(':');
      console.log("[]"+splitfq[0]+"[]");
      var doc=null;
      var $pivot=AjaxSolr.theme('pivot', doc, this.justthisfacetHandler(splitfq[0], splitfq[1]));
      //oldfqs[splitfq[0]]=[i,$span.append($link).append($pivot)];
      if (this.ffields.indexOf(splitfq[0])!=-1){
        console.log("in an ffields zone "+splitfq[0]);
        likefq.push($span.append($link).append($pivot));
      }
      else {
        oldfqs[splitfq[0]]=[i,$span.append($link).append($pivot)];
        likefq.push('UNDONE');  
      }
      //oldfqs.push(splitfq[0]);
    }
    for (var i = 0, l = fq.length; i < l; i++) {
        var sfq=fq[i].split(':')[0];
        if (likefq[i]=='UNDONE'){
            console.log('In undone '+sfq);
            if (oldfqs[sfq][0]==i){
                links.push(oldfqs[sfq][1]);
            }
            else {
                console.log("removing facet for "+fq[i]);
                if (self.manager.store.removeByValue('fq', fq[i])) {
                    self.manager.doRequest(0);
                 }            
            }
        }
        else {
            console.log("constructing "+sfq);
            links.push(likefq[i]);       
        }
    }

    if (links.length > 1) {
      links.unshift($('<a href="#"/>').text('remove all').click(function () {
        self.manager.store.remove('fq');
        self.manager.doRequest(0);
        return false;
      }));
    }

    if (links.length) {
      AjaxSolr.theme('list_items', this.target, links);
    }
    else {
      $(this.target).html('<div>Viewing all documents!</div>');
    }
  },

  removeFacet: function (facet) {
    var self = this;
    return function () {
      if (self.manager.store.removeByValue('fq', facet)) {
        self.manager.doRequest(0);
      }
      return false;
    };
  }
});

})(jQuery);

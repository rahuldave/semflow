var Manager;
(function() {
   function nop() {}
   if (! ("console" in window) || !("firebug" in console)) {
      var names = ["log", "debug", "info", "warn", "error", "assert", "dir",
		   "dirxml", "group", "groupEnd", "time", "timeEnd", "count",
		   "trace", "profile", "profileEnd"];
      window.console = {};
      for (var i = 0; i < names.length; ++i) {
	 window.console[names[i]] = nop;
      }
   }
})();

(function ($) {
  $(function () {
    console.log("WHEN IS THIS CALLED?");
    Manager = new AjaxSolr.Manager({
      solrUrl: 'http://boom.dyndns.org:8983/solr/'
	  //solrUrl: 'http://adslabs.nareau.com:8983/solr/'
    });
    Manager.addWidget(new AjaxSolr.ResultWidget({
      id: 'result',
      target: '#docs'
    }));
    Manager.addWidget(new AjaxSolr.PagerWidget({
      id: 'pager',
      target: '#pager',
      prevLabel: '&lt;',
      nextLabel: '&gt;',
      innerWindow: 1,
      renderHeader: function (perPage, offset, total) {
        $('#pager-header').html($('<span/>').text('displaying ' + Math.min(total, offset + 1) + ' to ' + Math.min(total, offset + perPage) + ' of ' + total));
      }
    }));
    var fields = [ 'keywords', 'author', 'papertype', 'objecttypes', 'objectnames', 'obsvtypes', 'obsids', 'instruments', 'missions', 'emdomains', 'targets', 'propids', 'proposaltype', 'proposalpi'];
    var facet_fields= [ 'keywords_s', 'author_s', 'papertype_s' , 'objecttypes_s', 'objectnames_s', 'obsvtypes_s', 'obsids_s', 'instruments_s', 'missions_s', 'emdomains_s', 'targets_s', 'propids_s', 'proposaltype_s', 'proposalpi_s'];
    for (var i = 0, l = fields.length; i < l; i++) {
      Manager.addWidget(new AjaxSolr.TagcloudWidget({
        id: fields[i],
        target: '#' + fields[i],
        field: facet_fields[i]
      }));
    }
    
    Manager.addWidget(new AjaxSolr.CurrentSearchWidget({
        id: 'currentsearch',
        target: '#selection',
        ffields: facet_fields
    }));
    /*Manager.addWidget(new AjaxSolr.TextWidget({
    id: 'text',
    target: '#search',
    field: 'text'
    }));*/
    Manager.addWidget(new AjaxSolr.AutocompleteWidget({
        id: 'text',
        target: '#search',
        field: 'text',
        fields: facet_fields
    }));
    Manager.addWidget(new AjaxSolr.YearWidget({
        id: 'pubyear',
        target: '#pubyear',
        field: 'pubyear_i'
    }));
    numericfields=['ra', 'dec', 'exptime'];
    facet_numericfields=['ra_f', 'dec_f', 'exptime_f'];
    min_numericfields=[0.0, -90.0, 0.0];
    max_numericfields=[360.0, 90.0, 10.0];
    step_numericfields=[15.0, 10.0, 1.0];
    for (var i = 0, l = numericfields.length; i < l; i++) {
        Manager.addWidget(new AjaxSolr.DualSliderWidget({
            id: numericfields[i],
            target: '#'+numericfields[i],
            field: facet_numericfields[i],
            themin: min_numericfields[i],
            themax: max_numericfields[i],
            thestep: step_numericfields[i]
        }));
    }
    Manager.addWidget(new AjaxSolr.DateRangerWidget({
        id: 'obsvtime',
        target: '#obsvtime',
        field: 'obsvtime_d',
        themin: 1988,
        themax: 2010,
        thestep: 10
    }));
    Manager.init();
    Manager.store.addByValue('q', '*:*');
    console.log("facet_fields:", facet_fields);
    var params = {
      'facet': true,
      'facet.field': facet_fields,
      'facet.pubyear': 'pubyear_i',
      'facet.pubyear.start':1990,
      'facet.pubyear.end':2010,
      'facet.pubyear.step':1,
      'facet.limit': 20,/* change this to set autocompletion limits differently...or solr 1.5*/
      'facet.mincount': 1,
      'f.topics.facet.limit': 50,
      'json.nl': 'map',
      'sort':'citationcount_i desc',
      'rows':20
    };
    for (var name in params) {
      Manager.store.addByValue(name, params[name]);
    }
    Manager.doRequest();
	//$('a.iframe').fancybox({autoDimensions: false, width:1024, height:768});

  });
})(jQuery);

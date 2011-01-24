(function ($) {

AjaxSolr.theme.prototype.result = function (doc, snippet, thetitlelink, thepivot) {
  //console.log("DIC: "+doc);
  var $thisdiv=$('<div></div>');
  var $h2 = $('<h2></h2>').append(doc.title+" ").append(thetitlelink).append(thepivot);
  //var output = '<div><h2>' + thetitle + '['+thepivot+']</h2>';
  var output='';
  output += '<p id="links_' + doc.id + '" class="links"></p>';
  output += '<p>' + snippet + '</p></div>';
  output += '<div style="display:none"><p id="p_'+doc.id+'">'+doc.title+'</p></div>';
  //return output;
  return $thisdiv.append($h2).append($(output));
}

AjaxSolr.theme.prototype.title = function (doc) {
    var $output=$('<a class="iframe"/>').text('(Link)').attr('href', "http://labs.adsabs.harvard.edu/ui/abs/"+doc.bibcode).fancybox({autoDimensions: false, width:1024, height:768});
    //var $output=$('<a class="colorbox-iframe"/>').text(doc.title).attr('href', "#p_"+doc.id).fancybox();
    return $output;
}

AjaxSolr.theme.prototype.pivot = function (doc, handler){
    var $pivot = $('<a href="#"/>').text(' [P]').click(handler);
    return $pivot;
}
AjaxSolr.theme.prototype.snippet = function (doc) {
  var output = '';
//  if (doc.text.length > 300) {
//    output += doc.dateline + ' ' + doc.text.substring(0, 300);
//    output += '<span style="display:none;">' + doc.text.substring(300);
//    output += '</span> <a href="#" class="more">more</a>';
//  }
//  else {
    output += "<b>Authors</b>: "+doc.author.join(' ; ')+"<br/>";
    output += "<b>Year</b>: "+doc.pubyear_i + ' <b>BibCode</b>:' + doc.bibcode + ' <b>Citations</b>:' + doc.citationcount_i;
//  }
  return output;
};

AjaxSolr.theme.prototype.tag = function (value, thecount, weight, handler, handler2) {
  
  var $thelink=$('<a href="#"/>').text(value).click(handler);
  var $thetext=$('<span></span>').text('('+thecount+')');
  //var $thepivot=$('<a href="#""/>').text('P').click(handler2);
  var $span=$('<span class="tagcloud_item"></span>').addClass('tagcloud_size_' + weight).append('[').append($thelink).append($thetext).append(']');
  //return [$thelink, $thetext, $thepivot]
  return $span;
};

AjaxSolr.theme.prototype.facet_link = function (value, handler) {
  return $('<a href="#"/>').text(value).click(handler);
};

AjaxSolr.theme.prototype.no_items_found = function () {
  return 'no items found in current selection';
};

AjaxSolr.theme.prototype.list_items = function (list, items, separator) {
  //var $list=$('#'+list);
  //console.log(list);
  //console.log($list);
  var $list=$(list);
  $list.empty();
  for (var i = 0, l = items.length; i < l; i++) {
    var li = jQuery('<li/>');
    //console.log("li"+li);
    if (AjaxSolr.isArray(items[i])) {
      for (var j = 0, m = items[i].length; j < m; j++) {
        if (separator && j > 0) {
          li.append(separator);
        }
        li.append(items[i][j]);
      }
    }
    else {
      //console.log("here");
      if (separator && i > 0) {
        li.append(separator);
      }
      li.append(items[i]);
    }
    $list.append(li);
  }
  //console.log("C"+$list);
};

})(jQuery);

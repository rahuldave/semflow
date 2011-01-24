# You can configure Blacklight from here. 
#   
#   Blacklight.configure(:environment) do |config| end
#   
# :shared (or leave it blank) is used by all environments. 
# You can override a shared key by using that key in a particular
# environment's configuration.
# 
# If you have no configuration beyond :shared for an environment, you
# do not need to call configure() for that envirnoment.
# 
# For specific environments:
# 
#   Blacklight.configure(:test) {}
#   Blacklight.configure(:development) {}
#   Blacklight.configure(:production) {}
# 

Blacklight.configure(:shared) do |config|

  # Set up and register the default SolrDocument Marc extension
  #SolrDocument.extension_parameters[:marc_source_field] = :marc_display
  #SolrDocument.extension_parameters[:marc_format_type] = :marc21
  #SolrDocument.use_extension( Blacklight::Solr::Document::Marc) do |document|
  #  document.key?( :marc_display  )
  #end
    
  # Semantic mappings of solr stored fields. Fields may be multi or
  # single valued. See Blacklight::Solr::Document::ExtendableClassMethods#field_semantics
  # and Blacklight::Solr::Document#to_semantic_values
#  SolrDocument.field_semantics.merge!(    
#    :title => "title_display",
#    :author => "author_display",
#    :keywords => "language_facet"  
#  )
        
  
  ##############################

  config[:default_solr_params] = {
    :find_by_id => {:qt => :document},
    :qt => "search",
    :per_page => 10 
  }
  
#  SolrDocument.default_params[:find_by_bibcode]= {:qt => :document}
#  config[:default_qt] = "search"
  
  

  # solr field values given special treatment in the show (single result) view
  config[:show] = {
    :html_title => "title",
    :heading => "title",
    #:display_type => "format"
  }

  # solr fld values given special treatment in the index (search results) view
  config[:index] = {
    :show_link => "title",
    #:record_display_type => "format",
    :num_per_page => 10
  }

  # solr fields that will be treated as facets by the blacklight application
  #   The ordering of the field names is the order of the display
  # TODO: Reorganize facet data structures supplied in config to make simpler
  # for human reading/writing, kind of like search_fields. Eg,
  # config[:facet] << {:field_name => "format", :label => "Format", :limit => 10}
  config[:facet] = {
    :field_names => (facet_fields = [
      "author_s",
      "keywords_s",
      "objecttypes_s",
      "pubyear",
    ]),
    :labels => {
      "author_s"              => "Author",
      "keywords_s"            => "Keywords",
      "objecttypes_s"         => "Object Types",
      "pubyear"               => "Publication Year",
    },
    # Setting a limit will trigger Blacklight's 'more' facet values link.
    # * If left unset, then all facet values returned by solr will be displayed.
    # * If set to an integer, then "f.somefield.facet.limit" will be added to
    # solr request, with actual solr request being +1 your configured limit --
    # you configure the number of items you actually want _displayed_ in a page.    
    # * If set to 'true', then no additional parameters will be sent to solr,
    # but any 'sniffed' request limit parameters will be used for paging, with
    # paging at requested limit -1. Can sniff from facet.limit or 
    # f.specific_field.facet.limit solr request params. This 'true' config
    # can be used if you set limits in :default_solr_params, or as defaults
    # on the solr side in the request handler itself. Request handler defaults
    # sniffing requires solr requests to be made with "echoParams=all", for
    # app code to actually have it echo'd back to see it.     
    :limits => {
      nil => 10
    }
  }

  # Have BL send all facet field names to Solr, which has been the default
  # previously. Simply remove these lines if you'd rather use Solr request
  # handler defaults, or have no facets.
  config[:default_solr_params] ||= {}
  config[:default_solr_params][:"facet.field"] = facet_fields

  # solr fields to be displayed in the index (search results) view
  #   The ordering of the field names is the order of the display 
  config[:index_fields] = {
    :field_names => [
      "title",
      "bibcode",
      "author",
      "keywords",
      "pubyear",
    ],
    :labels => {
      "title"           => "Title:",
      "bibcode"      => "Bibcode:",
      "author"          => "Author:",
      "keywords"     => "Keywords:",
      "pubyear"      => "Publication Year:",
    }
  }

  # solr fields to be displayed in the show (single result) view
  #   The ordering of the field names is the order of the display 
  config[:show_fields] = {
    :field_names => [
      "title",
      "bibcode",
      "author",
      "keywords",
      "objectnames",
      "objecttypes",
      "pubyear",
    ],
    :labels => {
      "title"           => "Title:",
      "bibcode"      => "Bibcode:",
      "author"          => "Author:",
      "keywords"     => "Keywords:",
      "objectnames"  => "Object Names:",
      "objecttypes"  => "Object Types:",
      "pubyear"      => "Publication Year:",
    }
  }


  # "fielded" search configuration. Used by pulldown among other places.
  # For supported keys in hash, see rdoc for Blacklight::SearchFields
  #
  # Search fields will inherit the :qt solr request handler from
  # config[:default_solr_parameters], OR can specify a different one
  # with a :qt key/value. Below examples inherit, except for subject
  # that specifies the same :qt as default for our own internal
  # testing purposes.
  #
  # The :key is what will be used to identify this BL search field internally,
  # as well as in URLs -- so changing it after deployment may break bookmarked
  # urls.  A display label will be automatically calculated from the :key,
  # or can be specified manually to be different. 
  config[:search_fields] ||= []

  # This one uses all the defaults set by the solr request handler. Which
  # solr request handler? The one set in config[:default_solr_parameters][:qt],
  # since we aren't specifying it otherwise. 
  config[:search_fields] << {
    :display_label => 'All Filds',
    :qt => 'search',
    :key => {:display_label=>"All Fields", :qt=>"search"}   
  }

  
  # "sort results by" select (pulldown)
  # label in pulldown is followed by the name of the SOLR field to sort by and
  # whether the sort is ascending or descending (it must be asc or desc
  # except in the relevancy case).
  # label is key, solr field is value
  config[:sort_fields] ||= []
  config[:sort_fields] << ['relevance', 'score desc']
  
  # If there are more than this many search results, no spelling ("did you 
  # mean") suggestion is offered.
  config[:spell_max] = 5
end


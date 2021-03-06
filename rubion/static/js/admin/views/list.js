$R.listView = {
    SearchList : ( function ( base ) {
	var cls = function( base ){
	    var self = this;
	    self.base = '#mainlist';
	    if (base !== undefined) {
		self.base = base;
	    }
	    self.items = $(this.base + ' *[data-rubion-searchable="true"]');

	    self.$noResultsMessage = $('<div class="alert alert-info">Foo</div>').insertAfter($(self.base)).hide()
	    var searchTitles = [],
		title;

	    // set placeholder for search field
	    self.items.each(function(){
		title =  $(this).data('rubion-searchable-title');
		if (title != undefined && searchTitles.indexOf(title) == -1){
		    searchTitles.push(title);
		}
	    })
	    
	    self.doSearch = function(input){
		self.$noResultsMessage.hide()
		if (input.length < 3) {
		    $(self.base + ' li').removeClass('pseudofirst').show().unmark();
		    return;
		}
		
		var pattern = RegExp('.*'+input+'.*', 'i');
		self.items.each( function(){
		    $this = $(this);
		    // Hide all
		    $this.parents('li').first().hide().removeClass('pseudofirst')
		    $this.unmark({
			'done' : function(){
			    $this.mark(input, {
				'className' : 'highlighted'
			    });
			}
		    });
		});
		// show all which contain a match
		$('.highlighted').parents('li').show();
		$(self.base+' li:visible').first().addClass('pseudofirst');
		if ($('.highlighted').length == 0){
		    self.$noResultsMessage.html('Der Suchbegriff <strong>'+input+'</strong> wurde nicht gefunden.').show()
		} 
	    }
	    this.attachTo = function( elements ){
		elements.each( function() {
		    $(this).attr('placeholder', searchTitles.join(', '));
		    $(this).keyup( function(){
			if ($(this).val().length < 3 && $(this).val().length > 0){
			    $(this).popover('show')
			} else {
			    $(this).popover('hide')
			}
			self.doSearch($(this).val());
		    });
		    $(this).change( function(){
			if ($(this).val().length < 3 && $(this).val().length > 0){
			    $(this).popover('show')
			} else {
			    $(this).popover('hide')
			}
			self.doSearch($(this).val());
		    });
		    $(this).popover({trigger:'manual'})
		})
	    }
	    
	    
	}
	return cls;
    })(),

    SortList : ( function(base, dropdown){
	var cls = function(base, dropdown){
	    var self = this;
	    self.base = '#mainlist';
	    if (base !== undefined){
		self.base = base;
	    }
	    self.sortOnInit = $(self.base).data('rubion-sort-on-init') != false;
	    self.dropdown = '#btnSortOrder';
	    if (dropdown !== undefined){
		self.dropdown = dropdown;
	    }
	    self.dropdownId = self.dropdown.substring(1);
	    self.dropdownContainer = $('[aria-labelledby="'+self.dropdownId+'"]');
	    self.addLink = function(label){
		$('<a href="#"></a>')
		    .addClass('dropdown-item')
		    .click(
			function(){
			    self.sort(label);
			    self.group_by(label);
			}
		    )
		    .append($('<i></i>').addClass('fas fa-sort-alpha-down'))
		    .append($('<span>'+label.replace(',',', ')+'</span>').addClass('ml-1'))
		    .appendTo(self.dropdownContainer);
		$('<a></a>')
		    .addClass('dropdown-item')
		    .click(
			function(){
			    self.sortDesc(label);
			    self.group_by(label);
			}
		    )
		    .append($('<i></i>').addClass('fas fa-sort-alpha-up-alt'))
		    .append($('<span>'+label.replace(',',', ')+'</span>').addClass('ml-1'))
		    .appendTo(self.dropdownContainer);
	    },
	    self.getSortableText = function(txt){
		if (typeof txt === 'number')
		    txt = txt.toString()
		return txt.
		    replace('ß','s').toUpperCase()
		    .replace('Ä','A')
		    .replace('Ö','O')
		    .replace('Ü','U')
	    },
	    self.compareFcn = function(a,b, attribute){
		var $a = $(a).find('[data-rubion-sortable="'+attribute+'"]').first()
		if ($a.is('[data-rubion-sortable-value]')){
		    a_txt = $a.data('rubion-sortable-value')
		} else {
		    a_txt = $a.text()
		}
		var $b = $(b).find('[data-rubion-sortable="'+attribute+'"]').first()
		if ($b.is('[data-rubion-sortable-value]')){
		    b_txt = $b.data('rubion-sortable-value')
		} else {
		    b_txt = $b.text()
		}    
		var a_txt = self.getSortableText(a_txt)
		var a_fallback = self.getSortableText(
		    $(a).find('h5').first().text()
		);
		var b_txt = self.getSortableText(b_txt)
		var b_fallback = self.getSortableText(
		    $(b).find('h5').first().text()
		);  
		return (a_txt < b_txt) ? -1 :
		    (a_txt > b_txt) ? 1 :
		    (a_fallback < b_fallback) ? -1 : (a_fallback > b_fallback) ? 1 : 0;
	    },
	    self.sort = function(attribute){
		console.log('Sorting by', attribute);
		$(self.base+' li.group-header').remove();
		$(self.base+' > li').sort( function(a, b){
		    return self.compareFcn(a,b, attribute);
		}).appendTo($(self.base));
	    },
	    self.sortDesc = function(attribute){
		console.log('Sorting desc by', attribute);
		$(self.base+' li.group-header').remove();
		$(self.base+' > li').sort( function(a, b){
		    return -1 * self.compareFcn(a, b, attribute);
		}).appendTo($(self.base));
	    },
	    self.group_by = function(attribute){
		console.log('Grouping by', attribute);
		var last_group = undefined;
		$(self.base+ ' > li').each(function(){
		    
		    var $elem = $(this).find('[data-rubion-groupby="'+attribute+'"]').first()
		    if ($elem.data('rubion-group-title') != last_group){
			last_group = $elem.data('rubion-group-title');
			$(this).before('<li class="list-group-item group-header"><h5>'+last_group+'</h5></li>')
		    }
		})
	    }
	    

	    var fields = [];
	    $(self.base).find('[data-rubion-sortable]').each(
		function() { fields.push($(this).data('rubion-sortable')); }
	    );
	    fields 
		.filter(function(val, idx, arr){return arr.indexOf(val) === idx})
		.forEach(item => self.addLink(item));
	    if (self.sortOnInit){
		var default_sort = $(self.base).find('[data-rubion-is-default-sort="true"]').first()
		if (default_sort.length > 0){
		    var sort_field = default_sort.data('rubion-sortable');
		    var sort_order = default_sort.data('rubion-default-sort-order');
		    
		    if (sort_order == 'desc'){
			self.sortDesc(sort_field); 
		    } else {
			self.sort(sort_field); 
		    }
		    self.group_by(sort_field);
		}
		else{
		    self.sort(fields[0]);
		}
	    }
	}
	return cls;
    })(),
    addFilterCount : function(originalCount){
	var n = $('#mainlist > li').length;
	var o = parseInt($('#mainlist').data('rubion-original-object-count'));
	$btn = $('#btnOpenFilterSettings');
	$btn.append($('<span class="badge badge-info">'+(n-o)+'</span>'));

    }
    
};


$(document).on('rubiontail.baseloaded', 
    function(){
	setLoadStatus(
	    'initiiere Filter',
	    function(){
		$R.listView.addFilterCount();
	    }
	)
	setLoadStatus(
	    'initiiere Suchfeld',
	    function(){
		var $searchField = $('#searchlist-input');
		var Searcher = new $R.listView.SearchList()
		Searcher.attachTo($searchField);
		var q = $R.urlParam('q');
		if (q){
		    $searchField.val(q);
		    Searcher.doSearch(q);
		}
	    }
	)
	setLoadStatus(
	    'sortiere Liste',
	    function(){
		var Sorter = new $R.listView.SortList();
	    }
	)
	setLoadStatus(
	    'initiiere Einstellungsfenster',
	    function(){
		var formModals = new $R.generic.ModalFormHandling();
	    }
	)
    }
)

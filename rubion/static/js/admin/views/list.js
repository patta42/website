$R.listView = {
    SearchList : ( function ( base ) {
	var cls = function( base ){
	    var self = this;
	    self.base = '#mainlist';
	    if (base !== undefined) {
		self.base = base;
	    }
	    self.items = $(this.base + ' *[data-rubion-searchable="true"]');

	    self.doSearch = function(input){
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
	    }
	    this.attachTo = function( elements ){
		elements.each( function() {
		    $(this).keyup( function(){
			self.doSearch($(this).val());
		    });
		    $(this).change( function(){
			self.doSearch($(this).val());
		    });
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
			}
		    )
		    .append($('<i></i>').addClass('fas fa-sort-alpha-up-alt'))
		    .append($('<span>'+label.replace(',',', ')+'</span>').addClass('ml-1'))
		    .appendTo(self.dropdownContainer);
	    },
	    self.getSortableText = function(txt){
		return txt.
		    replace('ß','s').toUpperCase()
		    .replace('Ä','A')
		    .replace('Ö','O')
		    .replace('Ü','U')
	    },
	    self.compareFcn = function(a,b, attribute){
		var a_txt = self.getSortableText(
		    $(a).find('[data-rubion-sortable="'+attribute+'"]').text()
		);
		var a_fallback = self.getSortableText(
		    $(a).find('h5').first().text()
		);
		var b_txt = self.getSortableText(
		    $(b).find('[data-rubion-sortable="'+attribute+'"]').text()
		);
		var b_fallback = self.getSortableText(
		    $(b).find('h5').first().text()
		);  
		return (a_txt < b_txt) ? -1 :
		    (a_txt > b_txt) ? 1 :
		    (a_fallback < b_fallback) ? -1 : (a_fallback > b_fallback) ? 1 : 0;
	    },
	    self.sort = function(attribute){
		$(self.base+' > li').sort( function(a, b){
		    return self.compareFcn(a,b, attribute);
		}).appendTo($(self.base));
	    },
	    self.sortDesc = function(attribute){
		$(self.base+' > li').sort( function(a, b){
		    return -1 * self.compareFcn(a, b, attribute);
		}).appendTo($(self.base));
	    }

	    var fields = [];
	    $(self.base).find('[data-rubion-sortable]').each(
		function() { fields.push($(this).data('rubion-sortable')); }
	    );
	    fields 
		.filter(function(val, idx, arr){return arr.indexOf(val) === idx})
		.forEach(item => self.addLink(item));
	    self.sort(fields[0]);
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

$(document).ready(
    function(){
	$R.listView.addFilterCount();
	var $searchField = $('#searchlist-input');
	var Searcher = new $R.listView.SearchList()
	Searcher.attachTo($searchField);
	var q = $R.urlParam('q');
	if (q){
	    $searchField.val(q);
	    Searcher.doSearch(q);
	}
	var Sorter = new $R.listView.SortList();
	var formModals = new $R.generic.ModalFormHandling(); 
    }
)

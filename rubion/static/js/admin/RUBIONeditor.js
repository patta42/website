$R.editing = {
    PageEditor : (function(){
	var cls = function(){
	    
	}
	
	return cls
    })(),
    RAIInlinePanelConfig : {
	'suffixes' : {
	    'EMPTY_FORM_TEMPLATE' : 'EMPTY_FORM_TEMPLATE',
	    'TOTAL_FORMS' : 'TOTAL_FORMS',
	    'INITIAL_FORMS' : 'INITIAL_FORMS',
	    'MIN_NUM_FORMS' : 'MIN_NUM_FORMS',
	    'MAX_NUM_FORMS' : 'MAX_NUM_FORMS',
	    'FORMS' : 'FORMS'
	},
	'buttons' : {
	    'UP': 'move-up',
	    'DOWN': 'move-down',
	    'DEL': 'delete',
	    'ADD' : 'add'
	},
	'inputs' : {
	    'ID' : 'id',
	    'ORDER' : 'ORDER',
	    'DELETE' : 'DELETE'

	}
    },
    RAIInlinePanelItem : (function () {
	var cls = function($elem, id, opts){
	    var self = this;
	    self.$elem = $elem;
	    for (key in opts){
		self[key] = opts[key];
	    }
	    var cfg = $R.editing.RAIInlinePanelConfig;
	    self.id = id;
	    self.n = $elem.attr('id').substring(('inline_child_'+id+'-').length);
	    var $$ = (spec) => $('#id_'+self.id+'-'+spec);

	    self.$inputs = {};
	    for (var key in cfg.inputs){
		self.$inputs[key] = $$(self.n+'-'+cfg.inputs[key]);
	    }

	    self.hasValue = function(){
		return !(self.$inputs.ID.val().trim() === "");
	    }
	    self.setDelete = function(tf){
		if (tf === undefined){
		    tf = true;
		}
		if (tf){
		    tf = "1";
		} else {
		    tf = "0";
		}
		self.$inputs.DELETE.val(tf);
	    }
	    
	    self.setOrder = function(order){
		self.$inputs.ORDER.val(order);
	    }
	    if (self.order !== undefined){
		self.setOrder(self.order);
	    }

	    self.incOrder = function(){
		self.setOrder(self.$inputs.ORDER.val()+1);
	    }
	    self.decOrder = function(){
		self.setOrder(self.$inputs.ORDER.val()-1);
	    }
	    // use a different name than 'delete' to unify syntax highlighting
	    // 'delete' is a reserved keyword
	    self.deleteMe = function(){
		// true deletion takes place in RAIInlinePanel
		self.setDelete();
		self.$elem.hide(400, function(){
		    self.deleteCallback(self);
		});
	    }
	    self.moveUp = function(){
		// moving is a three steps process:
		// hiding self
		// changing self's position
		// showing self.
		$prev = self.$elem.prev('[id^="inline_child_"]');
		if ($prev.length > 0){
		    self.$elem.hide(400, function(){
			$prev.before($elem);
			self.$elem.show(400);
			self.moveUpCallback(self);		
		    });
		}
		
		
	    }
	    self.moveDown = function(){
		// moving is a three steps process:
		// hiding self
		// changing self's position
		// showing self.
		$next = self.$elem.next('[id^="inline_child_"]');
		if ($next.length > 0){
		    self.$elem.hide(400, function() {
			$next.after($elem);
			$elem.show(400);
		    });
		    self.moveDownCallback(self);
		}

	    }
	    self.disableMoveUp = function(){
		self.$upBtn.addClass('disabled');
	    }
	    self.enableMoveUp = function(){
		self.$upBtn.removeClass('disabled');
	    }
	    self.disableMoveDown = function(){
		self.$downBtn.addClass('disabled');
	    }
	    self.enableMoveDown = function(){
		self.$downBtn.removeClass('disabled');
	    }
	    self.setDeleteEnabled = function(tf){
		tf ? self.$delBtn.removeClass('disabled') : self.$delBtn.addClass('disabled');
	    }


	    self.$upBtn = $$(self.n+'-'+cfg.buttons.UP).click(
		function(){
		    if (!($(this).hasClass('disabled'))){
			self.moveUp();
		    }
		}
	    );
	    self.$downBtn = $$(self.n+'-'+cfg.buttons.DOWN).click(
		function(){
		    if (!($(this).hasClass('disabled'))){
			self.moveDown();
		    }
		}
	    );
	    self.$delBtn = $$(self.n+'-'+cfg.buttons.DEL).click(
		function(){
		    if (!($(this).hasClass('disabled'))){
			self.deleteMe();
		    }
		}
	    );
	    
	}
	return cls
    })(),
    RAIInlinePanel : ( function ($elem) {
	var cls = function($elem){
	    var self = this;
	    self.children = [];
	    var cfg = $R.editing.RAIInlinePanelConfig;
	    self.id = $elem.attr('id');
	    self.$config = {};
	    var $$ = (spec) => $('#id_'+self.id+'-'+spec);

	    for (var key in cfg.suffixes){
		self.$config[key] = $$(cfg.suffixes[key]);
	    }


	    // add a trash bin for deleted items after the add button
	    self.$trash = $('<div></div>').insertAfter($$(cfg.buttons.ADD).parent());

	    self.getTotalForms = function(){
		return parseInt(
		    self.$config[cfg.suffixes.TOTAL_FORMS].val()
		)
	    }
	    var setTotalForms = function(val){
		self.$config[cfg.suffixes.TOTAL_FORMS].val(val)
	    }

	    self.incTotalForms = function(){
		setTotalForms(self.getTotalForms()+1);
	    }
	    self.getInitialForms = function(){
		return parseInt(
		    self.$config[cfg.suffixes.INITIAL_FORMS].val()
		)
	    }
	    setTotalForms(self.getInitialForms());
	    self.getNextId = function(){
		var id = self.getTotalForms();
		self.incTotalForms();
		return id;
	    }
	    
	    self.getMaxNumForms = function(){
		return parseInt(
		    self.$config[cfg.suffixes.MAX_NUM_FORMS].val()
		)
	    }

	    self.getMinNumForms = function(){
		return parseInt(
		    self.$config[cfg.suffixes.MIN_NUM_FORMS].val()
		)
	    }

	    swap = function(arr, x, y){
		var tmp = arr[x];
		arr[x] = arr[y];
		arr[y] = tmp;
		return arr;
	    }
	    self.onChildMovedDown = function(child){
		var idx = self.children.indexOf(child);
		child.incOrder();
		self.children[idx+1].decOrder()
		self.children[idx+1].enableMoveDown();
		self.children = swap(self.children, idx, idx+1);
		self.adjustButtonState();
	    }
	    self.onChildMovedUp = function(child){
		var idx = self.children.indexOf(child);
		child.decOrder();
		self.children[idx-1].incOrder();
		self.children = swap(self.children, idx, idx-1);
		self.adjustButtonState();
	    }
	    self.onChildDeleted = function(child){
		if (child.hasValue()){
		    // move id and delete field to trash
		    self.$trash.append(child.$inputs.DELETE);
		    self.$trash.append(child.$inputs.ID);
		}
		child.$elem.remove();
		var idx = self.children.indexOf(child);
		self.children.splice(idx, 1);
		self.adjustButtonState();
	    }

	    self.inlinePanelOpts = {
		'deleteCallback' : self.onChildDeleted,
		'moveUpCallback' : self.onChildMovedUp,
		'moveDownCallback' : self.onChildMovedDown
	    }

	    
	    self.adjustButtonState = function(){
		var mayDelete = self.children.length > self.getMinNumForms();
		var mayAdd = self.children.length < self.getMaxNumForms();
		// make it simple, stupid!
		for ( var i = 0; i < self.children.length; i++){
		    self.children[i].setDeleteEnabled(mayDelete);
		    if (i==0){
			self.children[i].disableMoveUp();
		    } else {
			self.children[i].enableMoveUp();
		    }
		    if (i==self.children.length-1) {
			self.children[i].disableMoveDown();
		    } else {
			self.children[i].enableMoveDown();
		    }
		}
	    }

	    self.setAddButtonEnabled=function(tf){
		tf ? $$(cfg.buttons.ADD).removeClass('disabled') : $$(cfg.buttons.ADD).addClass('disabled');
	    }

	    self.add = function(){
		// add a new sub-form 
		var $new_elem = $(
		    self.$config.EMPTY_FORM_TEMPLATE.html().replace(
			    /__prefix__/g,
			self.getNextId()
		    )
		).hide();
		self.$config.FORMS.append($new_elem);
		// order is 1-based, thus it's a good idea to increase the total number here
		self.incTotalForms();
		var opts = self.inlinePanelOpts;
		opts['order'] = self.getTotalForms();
		self.children.push(new $R.editing.RAIInlinePanelItem( $new_elem, self.id, opts ));
		$new_elem.show(400);
		self.adjustButtonState();

	    }


	    // Init Panels
	    $elem.find(
		$('[id^=inline_child_'+self.id+'-]')
	    ).each(function(){
		self.children.push(
		    new $R.editing.RAIInlinePanelItem($(this), self.id, self.inlinePanelOpts)
		)
	    });
	    self.adjustButtonState();
			      

	    // Add callback to add button
	    $$(cfg.buttons.ADD).click(function(){
		if (!$(this).hasClass('disabled')){
		    self.add();
		}
	    });

	}
	return cls;
    })(),
    RAIMultipleSelectListBoxesWidget : (function(){
	var cls = function($elem){
	    self = this;
	    self.$elem = $elem;
	    self.$searchUnselected = $elem.find('.search-unselected').first();
	    self.$searchSelected = $elem.find('.search-selected').first();
	    self.$unselectedContainer = $elem.find('.unselected ul').first();
	    self.$selectedContainer = $elem.find('.selected ul').first();
	    self.$items = self.$elem.find('input[type="checkbox"]');
	    self.$items.each(function(){
		$this = $(this)
		var $box = $this.parents('li').first();

		if ($this.is(':checked')){
		    $box.appendTo(self.$selectedContainer);
		} else {
		    $box.appendTo(self.$unselectedContainer);
		}
		$this.change(function(){
		    self.assignToList($(this));
		})
	    });
	    self.$searchSelected.keyup( function() {
		self.searchSelected();
	    })
	    self.$searchSelected.keypress( function(evt){
		if (evt.which == 13){
		    event.preventDefault();
		    if (self.$searchSelected.val().length > 2){
			self.$selectedContainer.
			    find('li:visible input[type="checkbox"]').
			    prop('checked', false).
			    trigger('change');
			self.$searchSelected.val('');
			self.$searchSelected.trigger('keyup');
		    }
		    
		}
	    })
	    self.$searchUnselected.keypress( function(evt){
		if (evt.which == 13){
		    event.preventDefault();
		    if (self.$searchUnselected.val().length > 2){
			self.$unselectedContainer.
			    find('li:visible input[type="checkbox"]').
			    prop('checked', true).
			    trigger('change');
			self.$searchUnselected.val('');
			self.$searchUnselected.trigger('keyup');
		    }
		    
		}
	    })

	    self.$searchUnselected.keyup( function() {
		self.searchUnselected();
	    })
	    self.searchUnselected = function(){
		self.search(self.$searchUnselected.val(), self.$unselectedContainer);
	    }
	    self.searchSelected = function(){
		self.search(self.$searchSelected.val(), self.$selectedContainer);
	    }

	    self.search = function(txt, $container){
		if (txt.length < 3){
		    $container.find('li').show().unmark();
		} else {
		    $container.find('li').each( function(){
			$this = $(this);
			$this.hide().unmark({
			    'done' : function(){
				$this.mark(txt, { 'className' : 'highlighted' });
			    }
			});
			$('.highlighted').parents('li').first().show();
		    })
		}

	    }
	    self.assignToList = function($checkbox){
		var $box = $checkbox.parents('li').first();
		var $target = $checkbox.is(':checked') ? self.$selectedContainer : self.$unselectedContainer;
		$box.hide(300, function(){
		    $target.append($box);
		    $box.show(300);
		})
	    
	    }
	}
	return cls;
    })(),
}

$(document).ready(
    function(){
	$('.inline-panel').each( function() {
	    new $R.editing.RAIInlinePanel($(this));
	});
	$('.multiple-input-selection-list').each( function() {
	    new $R.editing.RAIMultipleSelectListBoxesWidget($(this));
	});
    }
)

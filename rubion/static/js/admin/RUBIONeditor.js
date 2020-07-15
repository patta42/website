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
	    self.getDelete = function(){
		return self.$inputs.DELETE.val();
	    }
	    self.setDelete = function(tf){
		if (tf === undefined){
		    tf = true;
		}
		if (tf){
		    tf = "1";
		} else {
		    tf = "";
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
	    // avoid auto-fill by browser
	    self.setDelete(false)
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
		console.log('Setting total forms to', val)
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
//		self.incTotalForms();
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
		console.log(1)
		var $new_elem = $(
		    self.$config.EMPTY_FORM_TEMPLATE.html().replace(
			    /__prefix__/g,
			self.getNextId()
		    )
		).hide();
		console.log(2)
		self.$config.FORMS.append($new_elem);
		// order is 1-based, thus it's a good idea to increase the total number here
		console.log('In Add, before increasing total forms, total forms is', self.getTotalForms())
		
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
		    console.log('add was clicked')
		    console.log('calling add')
		    self.add();
		    console.log('add finished')
		}
	    });

	}
	return cls;
    })(),
    RAIMultipleSelectListBoxesWidget : (function(){
	var cls = function($elem){
	    var self = this;
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
    RAIMarkdownCommand: ( function (){
	    var cls = function( pre, post, newline, defaultText ) {
		var self = this;
		self.pre = pre;
		self.post = post;
		self.newline = newline;
		
		if (defaultText === undefined){
		    self.defaultText = "";
		}
		else {
		    self.defaultText = defaultText;
		}
		self.newlineCheck = function(start, text){
		    if (start == 0){
			return ''
		    }

		    if (text.length == 1){
			if (text == '\n'){
			    return ''
			} else {
			    return '\n\n';
			}
		    } else {
			var nl = '';
			if (text.slice(-1) != '\n'){
			    return '\n\n';
			} else {
			    if (text.slice(-2,-1) == '\n'){
				return ''
			    } else {
				return '\n'
			    }
			}
			
		    }
		}
		self.execute = function( $elem ){

		    // Get start amnd end of selection
		    var elem = $elem[0];
		    var start = elem.selectionStart;
		    var end = elem.selectionEnd;
		    if (end < start){
			start = end;
			end = elem.selectionStart;
		    }

		    // get current text
		    var val = $elem.val()

		    // split into pre and post part
		    var before = val.slice(0, start);
		    var after = val.slice(end);

		    // get selected text, fill with default if empty
		    var selection = end > start ? val.slice(start, end) : self.defaultText;
		    selection = selection.trim().length == 0 ? self.defaultText : selection;


		    // set up first part of markdown command
		    var fullPre = (
			newline == "pre" || newline == "both"
			    ? self.newlineCheck(start, before) : ''
		    ) + self.pre;

		    // set up complete text to insert
		    var insert =  fullPre + selection + self.post
			+ (newline=="post" || newline =="both" ? '\n\n' : '');


		    // insert
		    $elem.val(before+insert+after);

		    elem.focus();
		    elem.selectionStart = start + fullPre.length;
		    elem.selectionEnd = elem.selectionStart+selection.length;
		}
	    }
	    return cls;
	})(),
    RAIMarkdownEditor : (
	function() {
	    var cls = function($elem){
		var self = this;
		self.identifier = 'markdown-editor'
		var $d = (id) => self.identifier+'-'+id;
		var $c = (id) => $elem.find('.'+self.identifier+'-'+id);
		var $textarea = $elem.find($elem.data($d('controls')));
		console.log($textarea)
		self.url = $elem.data($d('process'));
		self.element_id = $textarea.attr('id');
		var $$ = (id) => ($elem.find('#'+self.element_id+id));
		// set up components
		self.$components = {
		    'textarea' : $textarea,
		    'buttons' : $c('action'),
		    'textareaContainer' : $$('TextareaContainer'),
		    'previewBtn' : $$('TabPreviewLabel'),
		    'editorBtn' : $$('TabEditorLabel'),
		    'previewContainer' : $$('previewContainer'),
		    'spinnerContainer' : $$('spinnerContainer'),
		    'previewOuter' : $$('previewOuter'),
		    'spinner' : $$('Spinner').parent('span')
		};

		// move textarea

		self.$components.textareaContainer.append(self.$components.textarea);

		// smaller font for textarea
		self.$components.textarea.css('font-size', '.9rem');
		// copy height and padding from textarea to preview
		self.$components.previewOuter.css({
		    'position': 'relative',
		    'overflow':'auto'
		})
		self.setSizes = function(evt){
		    self.textareaContainerHeight = self.$components.textareaContainer.height()
		    var height = self.textareaContainerHeight;
		    if (height == 0){
			// happens if we are in a modal
			if ($elem.parents('.modal').length > 0){
			    // just set a reasonable height of both components
			    height = Math.min($(window).height()/3, 350);
			    self.$components.textareaContainer.height(height);
			}
		    } 
		    self.$components.previewOuter.height(height);

		}
		self.adjustPreviewHeight = function(){
			
		}
		    
		self.$components.previewContainer
		    .css({
			'padding-left': self.$components.textarea.css('padding-left'),
			'padding-right': self.$components.textarea.css('padding-right'),
			'padding-top': self.$components.textarea.css('padding-top'),
			'padding-bottom': self.$components.textarea.css('padding-bottom'),
		    });
		
		// style spinner container
		self.$components.spinnerContainer.css({
		    'position': 'absolute',
		    'top' : 0, 'left' : 0,
		    'height': '100%', 'width':'100%',
		    'background-color':'rgba(0,0,0,.25)',
		    'font-size':'600%', 'color':'rgba(255,255,255,.5)',
		});

		self.showSpinner = function(){
		    self.$components.spinnerContainer.css('width','100%');
		    self.$components.spinner.show();
		}
		self.hideSpinner = function(){
		    self.$components.spinner.hide();
		    self.$components.spinnerContainer.css('width', 0);
		}
		self.render = function(){
		    $R.post(self.url, {
			beforeSend: function(){
			    self.showSpinner(),
			    self.adjustPreviewHeight()
			},
			data : {'markdown': self.$components.textarea.val()}
		    }).done(
			function( data ) {
			    if (data.content != 'None'){
				self.$components.previewContainer.html(data.content);
			    } else {
				self.$components.previewContainer.html('');
			    }
			    self.hideSpinner();
			}
		    ).fail(
			function( data ) {
			    console.log(data);
			}
		    )
		}
		self.$components.editorBtn.on('hide.bs.tab', function(evt){
		    self.setSizes(evt);
		})
		self.$components.previewBtn.on('shown.bs.tab', function(){
		    self.render();
		})
		self.$components.buttons.each(
		    function(){
			var button = $(this);
			var bind_to = 'insertMarkdown'
			if (button.data($d('bind_to')) !== undefined){
			    bind_to = button.data($d('bind_to'));
			}
			button.click(function(evt){self[bind_to](this, evt)})
		    }
		)
		self.insertMarkdown = function(button, evt){
		    $button = $(button);
		    var command = new $R.editing.RAIMarkdownCommand(
			$button.data($d('pre')),
			$button.data($d('post')),
			$button.data($d('newline')),
			$button.data($d('default')),
		    );
		    command.execute(self.$components.textarea);
		}
		self.adjustPreviewHeight()		    
		self.render()

	    }
	    return cls;
	})(),
    PillsPanelErrors : (
	function(){
	    var cls = function($elem){
		
	    }
	    return cls;
	}
    )(),
}

var me = {}
$(document).on('rubiontail.baseloaded',
    function(){
	setLoadStatus(
	    'initiiere erweiterte Editiermöglichkeiten',
	
	    function(){
		$('.inline-panel').each( function() {
		    me.foo = new $R.editing.RAIInlinePanel($(this));
		});
		$('.multiple-input-selection-list').each( function() {
		    me.bar = new $R.editing.RAIMultipleSelectListBoxesWidget($(this));
		});
		$('.markdown-editor').each(function(){
		    me.baz = new $R.editing.RAIMarkdownEditor($(this));
		})
		$('pills-panel').each(function(){
		    new $r.editing.PillsPanelErrors($(this))
		})
	    }
	)
    }
)

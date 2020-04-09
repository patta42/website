$.widget(
    'raiwidgetsSelectionPanel.permissionSelectionPanelListHeader',
    // The header component in the selection list is a plugin on its own
    {
	options : {
	    expandable : true,
	    emptyText: 'Bitte eine Auswahl treffen',
	    status: 'open'
	},
	_setgetOption : function(key, value){
	    if (value === undefined){
		return this.options[key]
	    } else {
		this.options[key] = value;
	    }
	},

	status : function(val, evt)
	{
	    var current = this._setgetOption('status')

	    if (val == current) return
	    
	    if (val == 'toggle'){
		val = current == 'open' ? 'close' : 'open'
	    }
	    switch (val) {
	    case 'open':
		this._setgetOption('status', 'open')
		this.$openCloseIndicator.addClass('is-open').removeClass('is-closed')
		if (evt !== undefined){
		    this._trigger('open', evt)
		}
		break
	    case 'close':
		this._setgetOption('status', 'close')
		this.$openCloseIndicator.addClass('is-closed').removeClass('is-open')
		if (evt !== undefined){
		    this._trigger('close',evt)
		}
		break
	    }
	    if (evt !== undefined){
		this._trigger('toggle', evt, this._setgetOption('status'))
	    }
	},

	
	
	_create : function(){
	    this.element.addClass('d-flex align-items-center justify-content-between list-group-select-header').removeClass('list-group-choice')
	    this.$openClose = $(
		'<a class="btn" ><span class="open-close-indicator">'+
		    '<span class="is-open"><i class="fas fa-angle-up"></i></span>'+
		    '<span class="is-closed"><i class="fas fa-angle-down"></i></span>'+ 
		    '</span></a>'
	    )
	    this.$openCloseIndicator = this.$openClose.find('.open-close-indicator').first()
	    if (this.options.status == 'open'){
		this.$openCloseIndicator.addClass('is-open')
	    } else {
		this.$openCloseIndicator.addClass('is-closed')
	    }
	    this.$statusText = $('<span class="mr-2"></span>').text(
		this.options.emptyText
	    )
	    this.$expandIndicator = $(
		'<span class="expand-indicator">'+
		    '<i class="fas fa-chevron-right"></i>'+
		    '<span class="is-expanded">'+
		    '<i class="fas fa-chevron-right" data-fa-transform="left-1"></i>'+
		    '</span>'+
		    '</span>'
	    )
	    this.$wrapper = $('<div />').appendTo(this.element)
	    this.$wrapper.append(this.$openClose)
		.append(this.$statusText)
	    if (this.options.expandable){
		this.element.append(this.$expandIndicator)
	    }
	    var self = this;
	    this.element.click(
		function(evt){
		    self.status('toggle', evt)
		}
		
	    )
	    
	},
	selected : function(val){
	    this.$statusText.html('Auswahl: <strong>'+val+'</strong>')
	    this.element.addClass('active')
	},
	clear : function(){
	    this.$statusText.html(this.options.emptyText)
	    this.element.removeClass('active')
	},
    }
)
$.widget(
    'raiwidgetsSelectionPanel.permissionSelectionListBox',
    {
	options : {
	    shown : false,
	    duration : 200,
	    items : [],
	    expandable : true,
	    value : undefined
	},
	_setOption : function(key, val){
	    this.options[key] = val;
	},
	
	_value : undefined,

	value : function(val){
	    if (val === undefined){
		return this.options['value']
	    } else {
		if (val == this.options['value']) return
		var $item
		this.$list.find('li:data("value")').each(
		    function(){
			if ($(this).data('value') == val){
			    $item = $(this);
			    return false
			}
		    }
		)
		if (!$item){
		    $item = this.$list.find('li[data-value="'+val+'"]').first()
		}
		if ($item){
		    this.options.value = val;
		    this._value = val;
		    this.$headListChoice.permissionSelectionPanelListHeader(
			'selected', $item.text()
		    )
		}
	    }
	},

	// option functions
	shown : function(value){
	    if (value === undefined){
		return this.options.shown;
	    } else {
		this._setOption('shown', value)
		if (value == false){
		    this.$list.hide(this.options.duration)
		    this.$headListChoice.permissionSelectionPanelListHeader('status','close')
		} else {
		    this.$list.show(this.options.duration)
		    this.$headListChoice.permissionSelectionPanelListHeader('status','open')
		}
	    }
	},
	duration : function(value){
	    if (value === undefined){
		return this.options.duration;
	    } else {
		this_setOption('duration', value)
	    }
	},
	// api
	_getListGroup : () => (
	    $(
		'<ul class="list-group"></ul>'
	     )
	),
	_emptyLi : () => (
	    $('<li class="list-group-item mb-0 list-group-choice"></li>')
	),
	_create : function(){
	    var self = this
	    this.element.empty().css('width','30%').addClass('mr-1') // just to be sure
	    this.$headListGroup = this._getListGroup().appendTo(this.element)
	    this.$headListChoice = this._emptyLi()
		.appendTo(this.$headListGroup)
		.permissionSelectionPanelListHeader({
		    toggle : function(evt, data){
			self._toggle(evt, data)
		    },
		    expandable : self.options.expandable
		    
		})
	    this.$listContainer = $('<div />').css({
		'maxHeight': '300px',
		'overflow':'auto'
	    }).appendTo(this.element)
	    this.$list = this._getListGroup().appendTo(this.$listContainer)
	},
	_select : function(evt){
	    var $clicked = $(evt.currentTarget);
	    this.value($clicked.data('value'));
	    this._trigger('select', evt, {
		value: $clicked.data('value'),
		name : $clicked.text()
	    })
	},
	_toggle : function(evt, data){
	    if (data == 'open'){
		this.shown(true)
	    } else {
		this.shown(false)
	    }
	},
	addItem : function(item){
	    var self = this;
	    for (var key in item){
		self._emptyLi()
		    .text(item[key])
		    .data('value', key)
		    .appendTo(
			self.$list
		    ).click(
			function(evt){
			    self._select(evt);
			}
		    )
	    }
	    
	},
	
	clear : function(){
	    this.$list.empty()
	    this.$headListChoice.permissionSelectionPanelListHeader('clear'),
	    this._trigger('cleared', undefined, {'oldValue' : this._value}),
	    this._value = undefined
	},
    }
)
$.widget(
    'raiwidgetsSelectionPanel.permissionSelectionPanelChild',
    {
	options : {
	    initAsEmpty : false
	},
	_create : function(){
	    this._mainOptions = [],
	    this._subOptions = {},
	    this._values = {},

	    this._mainSelection = '',
	    this._subSelection = '',
	    this._permissionSelection = '',
	
	    this._savedStates = [],
	
	    this._initComponents()
	    this._initOptions()
	    this._initLists()

	},
	
	_$ : function(selector){return this.element.find(selector)},
	
	// some "constant" functions generating html 
	
	_getEmptyLi: () => (
	    $('<li class="d-flex justify-content-between align-items-center list-group-item mb-0"></li>')
	),
	_getListBox: () => ($('<div class="list-group"></div>')),
	_getListContainerWrapper: () => (
	    $('<div class="d-flex justify-content-start align-items-start w-100"></div>')
	),
	
	// generating HTML, but not so constant any more
	// set the components used in the widget, 

	_initComponents : function(){

	    this.$itemSelect = this._$('.select-rai-items').first();


	    if (this.$itemSelect.val() !== '' && !this.options.initAsEmpty ){
		var tmp = this.$itemSelect.val().split('.')
		this._mainSelection = tmp[0]
		this._subSelection = tmp[1]
	    }
	    var self = this;
	    this.element.attr('tabindex', 0)
		.blur(
		    function(){
			self._savedStates = [];
			for (var key in self.$lists){
			    self._savedStates.push(self.$lists[key].permissionSelectionListBox('shown'));
			    self.$lists[key].permissionSelectionListBox('shown', false)
			}
		    }
		).focus(
		    function(){
			var count = 0;
			for (var key in self.$lists){
			    self.$lists[key].permissionSelectionListBox(
				'shown',
				self._savedStates[count]
			    )
			    count ++;
			}
		    }
		)
	    this.$permissionSelect = this._$('.select-rai-permissions').first()
	    this._permissionSelection = this.$permissionSelect.val()
	    this.$fieldset = this._$('fieldset').first().css('position','relative')
	    this.$container = this.$fieldset.find('div').first().css({
		'position':'absolute',
		'top' : '-10000px'
	    })
	    this.$listContainerWrapper = this._getListContainerWrapper().appendTo(self.$fieldset)
	    this.$lists = {}
	},
	_initOptions : function(){
	    var self = this
	    this.$itemSelect.find('optgroup').each(function(){
		var lb= $(this).attr('label');
		var name = $(this).data('rai-item-main-label') === undefined ?
		    lb : $(this).data('rai-item-main-label')
		var ob = {}
		ob[lb] = name
	    	self._mainOptions.push(ob)
	    	var $optgroup = $(this)
	    	var arr = [];
	    	$optgroup.find('option').each(function(){
		    
	    	    var obj = {}
	    	    obj[$(this).val().split('.')[1]] = $(this).text()
	    	    arr.push(obj)
		    
	    	})
	    	self._subOptions[lb] = arr;
    	    });
	    self.$permissionSelect.find('optgroup').each(function(){
	    	var $optgroup = $(this),
	    	    label = $optgroup.attr('label'),
	    	    arr = [];
	    	$optgroup.find('option').each(function(){
	    	    var sub = {};
	    	    sub[$(this).val()] = $(this).text()
	    	    arr.push(sub)
	    	})
	    	self._values[label] = arr;
	    })

	    
	},
	_populateList : function(list, items){
	    for (var count=0; count < items.length; count++){
		list.permissionSelectionListBox('addItem', items[count])
	    }
	},
	_initLists : function(){
	    var self = this
	    var listnames = ['main', 'sub', 'permission'], count
	    for (count = 0; count < listnames.length; count++){
		self.$lists[listnames[count]] = $('<div class="list-container"/>')
		    .appendTo(this.$listContainerWrapper)
	    }
	    this.$lists.permission.permissionSelectionListBox({
		expandable : false,
		select : function(evt, data){
		    self._permissionSelection = data['value'];
		    for (var key in self.$lists){
			self.$lists[key].permissionSelectionListBox('shown', false)
		    }
		    var item = self._mainSelection+'.'+self._subSelection;
		    self.$itemSelect.find(
			'option[value="'+item+'"]'
		    ).attr('selected', true)
		    self.$permissionSelect.find(
			'optgroup[label="'+item+'"] option[value="'+self._permissionSelection+'"]'
		    ).attr('selected', true)
		}
	    })
	    this.$lists.sub.permissionSelectionListBox({
		select : function(evt, data){
		    var value = data['value'], count
		    var options = self._values[self._mainSelection+'.'+value]
		    self._subSelection = data['value'];
		    self._permissionSelection = '';
		    self.$lists.permission.permissionSelectionListBox('clear');
		    self._populateList(self.$lists.permission, options)
		    self.$lists.permission.permissionSelectionListBox('shown', true)
		},
		cleared : function(evt, data){
		    self.$lists.permission.permissionSelectionListBox('clear')
		}
	    })
	    this.$lists.main.permissionSelectionListBox({
		'shown' : true,
		'select' : function(evt, data){
		    var value = data['value'], count
		    var options = self._subOptions[value]
		    self._mainSelection = value;
		    self._subSelection = '';
		    self._permissionSelection = '';
		    self.$lists.sub.permissionSelectionListBox('clear')
		    self._populateList(self.$lists.sub, self._subOptions[self._mainSelection])
		    self.$lists.sub.permissionSelectionListBox('shown',true)
		    
		}
	    })
	    this._populateList(self.$lists.main, self._mainOptions)

	    if (this._mainSelection != ''){
		this.$lists['main']
		    .permissionSelectionListBox('value', self._mainSelection)
		    .permissionSelectionListBox('shown', false)
		this._populateList(self.$lists.sub, self._subOptions[this._mainSelection])
	    } else {
		// clear all other data
		self._subSelection = '';
		self._permissionSelection = ''
	    }
	    if (this._subSelection != ''){
		this.$lists['sub']
		    .permissionSelectionListBox('value', this._subSelection)
		    .permissionSelectionListBox('shown', false)
		this._populateList(
		    self.$lists.permission,
		    this._values[this._mainSelection+'.'+this._subSelection]
		)
	    } else {
		// clear all other data
		this._permissionSelection = ''
	    }
	    if (this._permissionSelection != ''){
		this.$lists['permission']
		    .permissionSelectionListBox('value', this._permissionSelection)
		    .permissionSelectionListBox('shown', false)
	    } 
	}
    }
)
$.widget(
    'raiwidgetsSelectionPanel.permissionSelectionPanel',
    {
	options : {
	    template:     '-EMPTY_FORM_TEMPLATE',
	    totalForms:   '-TOTAL_FORMS',
	    initialForms: '-INITIAL_FORMS',
	    container:    '-FORMS',
	    addBtn:       '-add',
	},
	_$ : function(selector){ return this.element.find(selector) },
	_$$: function(suffix) { return $('#id_'+this.id+suffix) },

	_create : function(){
	    this.element.find('.inline-child').permissionSelectionPanelChild()
	    this.id = this.element.attr('id')
	    this.$childTemplate = this._$$(this.options['template'])
	    this.$totalForms = this._$$(this.options.totalForms)
	    this.$initialForms = this._$$(this.options.initialForms)

	    // reset the numor of total forms on init. Some browser cache the
	    // value of the hidden fields after a relaod

	    this.totalForms(this.$initialForms.val())
	    var self = this
	    this.$add = this._$$(this.options.addBtn)
		.click(function(){self._addChild()})
	    
	},
	totalForms : function(val){
	    if (val == undefined){
		return parseInt(this.$totalForms.val())
	    } else {
		return this.$totalForms.val(val).val()
	    }
	},
	incTotalForms : function(){
	    return this.totalForms(this.totalForms()+1)
	},	
	_addChild : function(){
	    console.log(this.$childTemplate)
	    var newElem =$(this.$childTemplate.html().replace(/__prefix__/g,(this.incTotalForms()-1)))
		.insertBefore(this.$add).permissionSelectionPanelChild({
		    initAsEmpty : true
		})
	    
	    
	}
    }
)

$R.Widgets = {
    init : function(){
	// activate all widgets
	$('.type-and-select').each(function(){
	    new $R.Widgets.TypeAndSelect($(this));
	})
	instances = []
	$('.inline-panel-select-permissions').permissionSelectionPanel()
    },

    TypeAndSelect : ( function() {
	var cls = function($elem){
	    var self = this;
	    self.$components = {};
	    $elem.wrap('<div class="type-and-select-wrapper"></div>');
	    self.$components.wrapper = $elem.parent('.type-and-select-wrapper').first().css({
		position: 'relative'
	    });

	    // move select far away
	    $elem.css({
		position: 'absolute',
		top: -10000,
		left:0,
	    })

	    var inputStructure= $(
		'<div class="input-group">'+
		    '  <input type="text" class="form-control" placeholder="Tippe, um zu suchen"/>'+
		    '    <div class="input-group-append bg-white">'+
		    '      <button type="button" class="btn btn-outline-secondary">'+
		    '        <svg width="10" height="10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 5">'+
		    '          <path fill="#3343a40" d="M2 0L0 2h4zm0 5L0 3h4z"/>'+
		    '        </svg>'+
		    '      </button>'+
		    '    </div>'+
		    '</div>');
	    
	    self.$components.wrapper.append(inputStructure);
	    self.$components.input = self.$components.wrapper.find('input').first();
	    self.$components.button = self.$components.wrapper.find('button').first();
	    self.$components.optionSurrounder = $('<ul class="list-group type-and-select-selection"></ul>')
	    $elem.find('option').each(
		function(){
		    $(this).attr('selected', false);
		    var txt = $(this).text().split('|')
		    var subline = txt.length > 1 ? '<span class="text-muted">'+txt[1]+'</span>' : ''
		    self.$components.optionSurrounder.append(
			$('<li class="list-group-item d-flex" data-type-and-select-value="'
			  + $(this).val()+'">'+
			  '<span class="status"><i class="selected-icon fas fa-check"></i><i class="not-selected-icon far fa-circle"></i></span>'+
			  '<span><h6>'+txt[0]+'</h6>'+subline+'</span></li>'
			 )
		    )
		}
	    )
	    self.$components.emptyOption = $('<option value="">--</option>');
	    $elem.append(self.$components.emptyOption);
	    self.$components.emptyOption.attr('selected', true)
	    self.$components.wrapper.append(self.$components.optionSurrounder)
	    self.$components.optionSurrounder.hide();
	    self.$options = self.$components.optionSurrounder.find('li');
	    self.$options.click(function(evt){
		self.select(evt);
	    })
	    self.$components.wrapper.css({
		'height':self.$components.wrapper.height()+'px',
		'overflow':'visible',
	    }) 

	    self.$components.button.click(
		function(){self.toggleSelection()}
	    )
	    self.$components.input.keyup(
		function(){
		    self.showSelection();
		    var txt = self.$components.input.val();
		    self.$options.removeClass('d-flex').hide()
		    self.$options.each(function(){
			$this = $(this);
			$this.unmark({
			    done : function(){
				$this.mark(txt, {
				    'className' : 'highlighted'
				});
			    }
			})
		    })
		    $('.highlighted').parents('li').addClass('d-flex').show();
		}
	    );
	    self.select = function(evt){
		$this = $(evt.currentTarget);
		if ($elem.attr('multiple') === undefined){
		    self.$options.removeClass('selected');
		    self.$components.emptyOption.attr('selected', true)
		}
		var value = $this.data('type-and-select-value');
		
		$this.addClass('selected');
		$elem.find('option[value="'+value+'"]').attr('selected',true);
		self.$components.emptyOption.attr('selected', false)
		self.toggleSelection();
		self.$components.input.val($this.find('h6').text());
		self.$options.unmark();
		self.$options.show().addClass('d-flex');
	    }
	    self.getHeight = function(){
		var ip = self.$components.input;
		return ($('.sidebar-sticky').outerHeight()+30) -
		    (ip.offset().top-$(window).scrollTop()+ip.height());
	    }
	    self.showSelection = function(){
		self.$components.optionSurrounder.css('height', self.getHeight()+'px');
		self.$components.optionSurrounder.show()
	    }
		
	    self.toggleSelection = function(){
		self.$components.optionSurrounder.css('height', self.getHeight()+'px');
		self.$components.optionSurrounder.toggle()
	    }
	}
	return cls;
    })(),
    // PermissionSelctionInlineChild : ( function() {
    // 	var cls = function($elem){

    // 	    // some "constants" first

    // 	    var emptyLi =
    // 		''
    // 	    var 
	    
    // 	    var self = this;
    // 	    self.$elem = $elem;
    // 	    self.$itemsSelect = $elem.find('').first()
    // 	    self.$permissionsSelect = $elem.find('.select-rai-permissions').first()
    // 	    self.$fieldset = self.$elem.find('fieldset').first()
    // 	    self.$container = self.$fieldset.find('div').first() 
    // 	    // position element

    // 	    self.$elem.css('position', 'relative');
    // 	    self.$container.css({
    // 		'position' : 'absolute',
    // 		'top': '-10000px'
    // 	    })
    // 	    self.$listContainer = $(
    // 		'<div class="d-flex justify-content-start '+
    // 		    'align-items-start w-100 border-secondary"></div>'
    // 	    ).appendTo(self.$fieldset)

    // 	    self.makeListBox = function(){
    // 		return $('<ul class="list-group mr-2"></ul>').css({
    // 		    'maxHeight' : '300px',
    // 		    'overflow': 'auto',
    // 		    'width':'30%'
    // 		})
    // 	    }

    // 	    // make the three lists
    // 	    self.$lists = {}
    // 	    var lbnames = ['main', 'sub', 'permission']
    // 	    for (var count = 0; count < lbnames.length; count++){
    // 		self.$lists[lbnames[count]] = self.makeListBox().appendTo(self.$listContainer)
    // 		if (count>0){
    // 		    self.$lists[lbnames[count]].hide()
    // 		}
    // 	    }

	    
    // 	    self.addListItems = function($list, items, labels, addIndicator){
    // 		addIndicator = addIndicator === undefined ? true : addIndicator;
    // 		var indicator = !addIndicator ? '' : '<span class="open-indicator">'+
    // 		    '<span class="is-open">'+
    // 		    '<i class="fas fa-chevron-right"></i>'+
    // 		    '<i class="fas fa-chevron-right" data-fa-transform="left-1"></i>'+
    // 		    '</span>'+
    // 		    '<span class="is-closed">'+
    // 		    '<i class="fas fa-chevron-right"></i>'+
    // 		    '</span>'+
    // 		    '</span>'
    // 		$('<li class="d-flex justify-content-between align-items-center list-group-item mb-0">'+
    // 		  '<span class=""><span class="is-open"><i class="fas fa-angle-down"></i></span><span class="is-closed"><i class="fas fa-angle-down"></i></span></span><span>Bitte eine Auswahl treffen:</span>'+
    // 		  indicator+
    // 		  '</li>'
    // 		 ).appendTo($list)
    // 		for (var count = 0; count < items.length; count++){
    // 		    $('<li class="d-flex justify-content-between align-items-center list-group-item mb-0"'+
    // 		      ' data-selected-value="'+items[count]+'">'+
    // 		      '<span>'+labels[count]+'</span>'+
    // 		      '</li>'
    // 		     ).appendTo($list)
    // 		}
    // 	    }



	    
    // 	    self.getMainIds = function(){
    // 		var ids = []
    // 		self.$itemsSelect.find('optgroup').each(
    // 		    function(){
    // 			ids.push($(this).attr('label'))
    // 		    }
    // 		)
    // 		return ids;
    // 	    }
    // 	    self.getMainIdNames = function(){
    // 		var names = []
    // 		self.$itemsSelect.find('optgroup').each(
    // 		    function(){
    // 			if ($(this).data('rai-item-main-label') === undefined){
    // 			    names.push($(this).attr('label'))
    // 			} else {
    // 			    names.push($(this).data('rai-item-main-label'))
    // 			}
    // 		    }
    // 		)
    // 		return names
    // 	    }
    // 	    self.getSubIds = function(main){
    // 		var group = self.$itemsSelect.find('optgroup[label="'+main+'"]').first()
    // 		var ids = []
    // 		group.find('option').each(function(){
    // 		    ids.push($(this).val().split('.')[1]);
    // 		})
    // 		return ids;
    // 	    }
    // 	    self.getSubIdNames=function(main){
    // 		var group = self.$itemsSelect.find('optgroup[label="'+main+'"]').first()
    // 		var names = []
    // 		group.find('option').each(function(){
    // 		    names.push($(this).text());
    // 		})
    // 		return names;
    // 	    }
    // 	    self.makeSubList = function(main){
    // 		self.$lists.sub.empty();
    // 		self.addListItems(self.$lists.sub, self.getSubIds(main), self.getSubIdNames(main))
    // 		self.$lists.sub.show(200)
    // 	    }
    // 	    // populate the first list
    // 	    self.addListItems(self.$lists.main, self.getMainIds(), self.getMainIdNames())
    // 	    // assign callbacks
    // 	    self.$lists.main.find('li').click(function(evt){
    // 		var $this = $(this);
    // 		if (!$this.hasClass('active')){
    // 		    $this.siblings('.active').removeClass('active')
    // 		    $this.addClass('active') 
    // 		    self.makeSubList($(evt.currentTarget).data('selected-value'));
    // 		}
    // 	    })
	    
    // 	}
    // 	return cls;
    // })(),
    // PermissionSelectionPanel : ( function(){
    // 	var cls = function($elem){
    // 	    var self = this;
    // 	    self.$elem = $elem;
    // 	    self.children = []

    // 	    // attach children 
    // 	    $elem.find('.inline-child').each(
    // 		function(){
    // 		    self.children.push(new $R.Widgets.PermissionSelctionInlineChild($(this)));
    // 		}
    // 	    )
	    
	    
    // 	    // we might have multiple instances
	    
    // 	}
    // 	return cls;
    // })()
}

$(document).ready(function(){
    $R.Widgets.init()
})

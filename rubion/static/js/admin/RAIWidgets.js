


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
	    initAsEmpty : false,
	    id : undefined,
	    prefix : ''
	},
	_create : function(){
	    var id_prefix = 'inline_child_'+this.options.prefix+'-';
	    this.options['id'] = this.element.attr('id').substring(id_prefix.length)
	    
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
	_$$ : function(suffix) {return this._$(
	    '#id_'+this.options.prefix+'-'+this.options.id+'-'+suffix)},
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
	    this.$deleteBtn = this._$$('delete')
	    this.$deleteIndicator = this._$$('DELETE')

	    
	    if (this.$itemSelect.val() !== '' && !this.options.initAsEmpty ){
		var tmp = this.$itemSelect.val().split('.')
		this._mainSelection = tmp[0]
		this._subSelection = tmp[1]
	    }
	    var self = this;
	    this.$deleteBtn.click( function(evt){
		self._delete(evt)
	    })
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
	},
	_delete : function(evt){
	    this._$('input[type="hidden"]').insertBefore(this.element)
	    
	    this.element.hide(200, function(){
		$(this).remove()
	    })
	    this.$deleteBtn.remove()
	    this.$deleteIndicator.val("1")
	    this._trigger('delete', evt, this)
	},
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
	    this.id = this.element.attr('id')
	    this.element.find('.inline-child')
		.permissionSelectionPanelChild({prefix:this.id})
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
	    var newElem =$(this.$childTemplate.html().replace(/__prefix__/g,(this.incTotalForms()-1)))
		.insertBefore(this.$add).permissionSelectionPanelChild({
		    initAsEmpty : true,
		    prefix : this.id
		})
	    
	    
	}
    }
)

$.widget('raiwidgets.templateeditor', {
    _$ : function(selector){
	return this.element.find(selector)
    },
    _create : function(){
	this.previewUrl = this.element.data('template-editor-preview-url')
	this.notificationId = this.element.data('template-editor-notification-id')
	this.$template = this._$('textarea[name=template]').first()
	
	this.$btnContainer = this._$('.template-editor-button-container').first()

	// assign functionality for buttons and preview field
	var self = this
	this.$btnContainer.find('a.dropdown-item').each(function(){
	    $(this).click(function(evt){self._insertFilter(evt)})
	})
	this.$previewWrapper =  this._$('.template-editor-preview').first().click(
	    function(){
		if ($(this).hasClass('template-editor-preview-not-loaded')){
		    self._getPreview()
		}
	    }
	)
	this.$preview = $('<div class="p-2"/>').appendTo(this.$previewWrapper)
	

	this.$previewOptions = this._$('.template-editor-preview-options select')
	    .change(
		function(){ self._setPreviewInvalid() }
	    )
	this.$template.change(
	    function(){ self._setPreviewInvalid() }
	)
	
    },
    _setPreviewInvalid : function(){
	this.$preview.html('')
	this.$previewWrapper
	    .removeClass('template-editor-preview-loading')
	    .addClass('template-editor-preview-not-loaded')
	
    },
    _insertFilter : function(evt){
	evt.preventDefault()
	var filter = $(evt.currentTarget).attr('href')
	var prefix = $(evt.currentTarget).data('template-tag-prefix')
	var tpl = this.$template.val()
	var textarea = this.$template[0],
	    start = textarea.selectionStart,
	    end = textarea.selectionEnd,
	    pre = tpl.slice(0, start),
	    post = tpl.slice(end),
	    insert = '{{ '+prefix+'|'+filter+' }}'
	this.$template.val(pre+insert+post)
	textarea.selectionStart = start + insert.length
	textarea.selectionStart = start + insert.length
	this._setPreviewInvalid()
    },
    _getPreview : function(){
	var data = {}
	data['template'] = this.$template.val()
	data['notification_id'] = this.notificationId
	this.$previewOptions.each(function(){
	    data[$(this).attr('name')] = $(this).val()
	})
	var self = this
	$R.post(this.previewUrl, {
	    data : data,
	    beforeSend : function(){
		self.$previewWrapper
		    .removeClass('template-editor-preview-not-loaded')
		    .addClass('template-editor-preview-loading')
	    }
	})
	    .fail(
		self.$previewWrapper
		    .addClass('template-editor-preview-not-loaded')
		    .removeClass('template-editor-preview-loading')
	    )
	    .done(
		function(data){
		    self.$previewWrapper
			.removeClass('template-editor-preview-loading')
			.removeClass('template-editor-preview-not-loaded')
		    self.$preview.html('<pre>'+data['preview']+'</pre>')
		}
	    )
    }
    
})

$.widget(
    'raiwidget.editable',
    {
	options : {
	    bgColor : 'rgba(0,0,128,.25)'
	},
	_create: function(){
	    this.$button = $(this.element.data('activated-by'))
	    var self = this
	    this.$button.click(
		function(){
		    self.element[0].contentEditable = true;
		    css = self.element.css(['backgroundColor', 'cursor'])
		    self.element.focus().css({
			'backgroundColor': self.options['bgColor'],
			'cursor' : 'text'
		    })
		    $R.selectElementText(self.element[0]);
		    self.element.blur( function(){
			self.element[0].contentEditable = false;
			self.element.css(css)
			self._save()
		    })
		}
	    )
	},
	_save : function(){
	    var url = this.element.data('edit-url')
	    var field = this.element.data('field-label')
	    
	    $R.post(url, {
		data : {
		    field: field,
		    value: this.element.html()
		}
	    })
		.done()
		.fail()
	}
    }
)
$.widget(
    'raiwidget.editablecontent',
    {
	options : {
	    bgColor : 'rgba(0,0,128,.25)'
	},
	_create : function(){
	    this.$button = $(this.element.data('activated-by'))
	    this.$parentAnchor = this.element.parents('a[href]')
	    var self = this
	    var css  
	    this.$button.click(function(){
		self.element[0].contentEditable = true;
		css = self.element.css(['backgroundColor', 'cursor'])
		self.element.focus().css({
		    'backgroundColor': self.options['bgColor'],
		    'cursor' : 'text'
		})
		$R.selectElementText(self.element[0]);
		var href = self.$parentAnchor.attr('href');
		self.$parentAnchor.removeAttr('href');
		self.element.blur( function(){
		    self.element[0].contentEditable = false;
		    self.element.css(css)
		    self.$parentAnchor.attr('href', href)
		    self._save()
		})
	    })
	},
	_save : function(){
	    var url = this.element
		.parents('[data-admin-menu-settings-url]')
		.first()
		.data('admin-menu-settings-url')
	    var data = {}
	    var content = {}
	    content[this.element.data('edit-type-id')] = this.element.text().trim()
	    data[this.element.data('edit-type')] = JSON.stringify(content)
	    data['user'] = $('body').first().data('rai-user_pk')
	    $R.post(url, {data:data})
		.done()
		.fail()
	    
	}
    }
)

$.widget(
    'raiwidget.inlinealloptions',
    {
	_create : function(){
	    this.id = this.element.attr('id')
	    var self = this
	    var $$ = function(sel){
		return self.element.find('#id_'+self.id+sel)
	    }
	    
	    this.$formTemplate = $$('-EMPTY_FORM_TEMPLATE')
	    this.$totalForms = $$('-TOTAL_FORMS')
	    this.$initialForms = $$('-INITIAL_FORMS')
	    var $template = $(this.$formTemplate.html()),
		$options = $template.find('select').first().find('option'),
		$addBtn = $$('-add').parent().hide(),
		fieldName = $template.find('select').first().attr('name')
	    
	    
	    
	    this._totalForms(this.$initialForms.val())
	    this.$wrapper = $$('-FORMS').css({
		position : 'absolute',
		top : '-10000px',
		left : '-10000px'
	    })
	    this.$list = this._getListWrapper().insertAfter(this.$wrapper)
	    var count = 0;
	    $options.sort(function(a,b){
		var $a = $(a),
		    $b = $(b)
		return $a.html() < $b.html() ? -1 :
		    $a.html() > $b.html() ? 1 : 0
		    
	    }).each(function(){
		if ($(this).val() !== undefined && $(this).val() !== ''){ 
		    self._addOption(this, count)
		}
		$(this).data('options-count', count)
		count += 1;
	    })
	    var totalForms = this._totalForms()
	    for (count = 0; count < totalForms; count++){
		var $select = $('#id_'+fieldName.replace(/__prefix__/g, count)),
		    $input = this.$list.find('input[value="'+$select.val()+'"]').first(),
		    $li = $input.parents('li').first(),
		    $selPar = $select.parents('.form-group'),
		    $siblings = $selPar.siblings('.form-group')
		$input.prop('checked', true).data('was-initial', count)
		// display additional values
		if ($siblings.length > 0){
		    var $addInp = $('<div />')
			.addClass('additional-inputs')
			.appendTo($li)
		    $siblings.appendTo($addInp)
		    
		}
	    }
	},
	
	_totalForms : function(val){
	    if (val == undefined){
		return parseInt(this.$totalForms.val())
	    } else {
		this.$totalForms.val(val)
	    }
		
	},
	_incTotalForms : function(){
	    this._totalForms(this._totalForms()+1)
	    
	},
	_decTotalForms : function(){
	    this._totalForms(this._totalForms()-1)
	},
	_getListWrapper : function(){
	    return $('<ul class="list-group"/>')
	},
	_addOption: function(elem, count){
	    var self = this

	    $elem = $(elem);
	    this.$list.append(
		$('<li />')
		    .data('selection-value', $elem.val())
		    .addClass('list-group-item')
		    .append(
		    	$('<div>')
		    	    .addClass('custom-control custom-checkbox checked-indicator mr-2')
		    	    .append(
		    		$(
				    '<input type="checkbox" />'
				)
		    		    .addClass('custom-control-input')
				    .data('options-count', count)
				    .data('was-initial', -1)
		    		    .attr('id', 'cbfor_'+self.id+'_'+$elem.val())
				    .val($elem.val())
		    		    .change(
		    			function(){
		    			    self._toggle($(this))
		    			}
		    		    )
			    )
		    	    .append(
		    		$('<label />')
		    		    .addClass('custom-control-label')
		    		    .attr('for', 'cbfor_'+this.id+'_'+$elem.val())
		    		    .html($elem.html())
				
		    	    )
			
		    )
	    
	    )
	    
	},
	_toggle : function($elem){
	    if ($elem.data('was-initial') >= 0){
		// in this case, toggle the DELETE hidden form
		console.log('Changing initial form', $elem.data('was-initial') )
		$('#id_'+this.id+'-'+$elem.data('was-initial')+'-DELETE')
		    .val(
			$elem.prop('checked') ? '' : '1'
		    )
		var $li = $elem.parents('li').first(),
		    $addInp = $li.find('.additional-inputs')
		$elem.prop('checked') ? $addInp.show(200) : $addInp.hide(200)
	    } else {
		var $li = $elem.parents('.list-group-item').first()

		if ($elem.prop('checked')){
		    // add new form
		    var $form = $(
			this.$formTemplate.html().replace(/__prefix__/g, this._totalForms())
		    ),
			wrapperId = 'id_'+this.id+'-'+this._totalForms()+'-WRAPPER',
			$formWrapper = $('<div />')
			.attr('id', wrapperId),
			// move first select to invisible wrapper
			$select = $form
			.find('select')
			.first()
			.parents('.form-group')
			.appendTo($formWrapper),
			$additionalInputs = $('<div />').addClass('additional-inputs').hide(),
			$children = $form.find('.form-group').appendTo($additionalInputs)
		    $formWrapper.appendTo(this.$wrapper)
		    $elem.attr('data-children-counter', this._totalForms())
		    

		    $form.find('input[name="'+this.id+'-'+this._totalForms()+'-ORDER"]')
			.val(0)
			.appendTo($formWrapper)
		    $select.find('option[value="'+$elem.val()+'"]').first().prop('selected', true)		    
		    if ($children.length > 0){
			
			$additionalInputs.appendTo($li).show(
			    200,
			)
		    }
		    this._incTotalForms()
		} else {
		    // remove new form
		    var $addInp = $li.find('div.additional-inputs'),
			oldTotalForms = this._totalForms(),
			removedChildCount = $elem.data('children-counter')

		    $('#id_'+this.id+'-'+removedChildCount+'-WRAPPER').remove()
		    
		    
		    $addInp.hide(200, function(){$addInp.remove()})
		    var self = this
		    for (var count = removedChildCount + 1; count < oldTotalForms; count++){
			// decrease all numbers in id, name, for, etc...
			var $formWrapper = $('#id_'+this.id+'-'+count+'-WRAPPER')
			var attrs = ['id', 'for', 'name']
			var $input = this.element.find('[data-children-counter="'+count+'"]').first()
			var $additional = $input.parents('li').first().find('.additional-inputs')

			var $containers = $formWrapper.add($additional)
			for (var acount = 0; acount < attrs.length; acount++){
			    var attr = attrs[acount]
			    $containers.find('['+attr+'*="'+this.id+'-'+count+'-"]').each(
				function(){
				    $(this).attr(
					attr,
					$(this).attr(attr).replace(
					    self.id+'-'+count+'-',
					    self.id+'-'+(count-1)+'-'
					)
				    )
				}
			    )
			    
			}
			$formWrapper.attr('id', 'id_'+this.id+'-'+(count-1)+'-WRAPPER');
			$input.attr('data-children-counter', count-1)
			
			
		    }
		    this._decTotalForms()
		}
	    }
	    
	    
	}
    }
)

$.widget(
    'raiwidgets.commenthandlers',
    {
	_create : function(){
	    var self = this
	    this.element.find('.comment-delete-button').ajaxify({
		successCallback : function(){self._commentDeleted()}
	    })
	    this.$modal = this.element.find('.comment-edit-button').first()
	    var self = this;
	    this.$modal.genericmodal(
		{
		    title : 'Kommentar ändern',
		    contentReady : function(evt, $content){
			var $mde = $content.find('.markdown-editor').first()
			new $R.editing.RAIMarkdownEditor($mde)
		    },
		    onSave : function(evt, data){
			self._save(evt, data)
		    }
		}
	    )
	},
	_save : function(evt, data){
	    var $body = data['body'],
		$textarea = $body.find('textarea').first(),
		self = this
	    
	    $R.post(data.url, {data : {comment: $textarea.val()}})
		.done(
		    function(data){
			if (data.status == 200){
			    self.$modal.genericmodal('destroy')
			    self.element.find('.markdown-widget-content').first().html(
				data['html']
			    ).before(
				'<div class="alert alert-info alert-dismissible fade show" role="alert">'+
				    'Kommentar wurde geändert'+
				    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
				    '<span aria-hidden="true">&times;</span>'+
				    '</button>'+
				    '</div>'
			    )
			    
			} else {
			    console.log(data)
			}
		    }
		    
		)
		.fail()
	},
	_commentDeleted : function(data){
	    var self = this;
	    this.element.hide(200, function(){
		var $notification = $(
		    '<div class="alert alert-warning alert-dismissible fade show ml-5" role="alert">' +
			'<strong>Kommentar gelöscht!</strong>'+
			'<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
			'<span aria-hidden="true">&times;</span>'+
			'</button>'+
			'</div>')
		self.element.before($notification)
		self.element.remove()
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
	$('.inline-panel-all-options').inlinealloptions()
	$('.hide-show-widget').hideshow()
	$('.template-editor').templateeditor()
	$('.depending-field').dependingfield()
	$.fn.datetimepicker.Constructor.Default =
	    $.extend(
		{}, $.fn.datetimepicker.Constructor.Default,
		{
		    icons: {
			time: "fas fa-clock",
			date: "fas fa-calendar",
			up: "fas fa-arrow-up",
			down: "fas fa-arrow-down",
			previous: 'fa fa-chevron-left',
			next: 'fas fa-chevron-right',
			today: 'fas fa-calendar-check',
			clear: 'fas fa-trash-alt',
			close: 'fas fa-times'
		    },
		    locale : 'de',
		    allowInputToggle : true,
		    calendarWeeks : true,
		    buttons: {
			showToday: true,
			showClear: true,
			showClose: true
		    }
			
		}
	    )
	
	$('.input-group.date').datetimepicker({
	    format : 'YYYY-MM-DD'
	})
	    
	$('.input-group.date-time').datetimepicker({
	    format : 'YYYY-MM-DD HH:mm'
	})
	$('.input-group.time').datetimepicker({
	    format : 'HH:mm'
	})
	$('.rai-comment').commenthandlers()
	$('.show-hide-controller').showhidecontroller()
	$('.display-as-table').displayastable()
	var count = 0;
	$('.editing-controller').each(function(){
	    $(this).editingcontroller({count:count})
	    count ++;
	})
	$('.editable-field').editable()
	$('.file-field.add-file').documentupload()
	$('.file-delete-button').each(
	    function(){
		var $elem = $(this)
		$elem.ajaxify(
		    {
			successCallback : function(data){
			    if (data.status == "200"){
				$li = $elem.parents('li').first()
				$li.hide(200, function(){
				    $li.remove()
				});
			    } else {
				console.log(data)
			    }
			}
		    }
		)
	    }
	)
	$('.tree-view-select').treeviewselect()
	bsCustomFileInput.init()
	$('a.ajaxify').ajaxify()
	$('.panel-grid-wrapper').panelgrid()

	$('.dropdown [data-toggle="dropdown"]').on('click', function(e) {
            $(this).dropdown('toggle');
            e.stopPropagation();
	});
	$('.dropdown').on('hide.bs.dropdown', function(e) {
            if ($(this).is('.has-child-dropdown-show')) {
		$(this).removeClass('has-child-dropdown-show');
		e.preventDefault();
            }
            e.stopPropagation();
	});

	$('input[type="checkbox"].check-all').checkall()
	$('table thead th.select-shown-rows').selectshownrows()
	$('.attendee-list').attendeelist()
	$('select.nuclide-select').nuclideselect()
	$R.addDomInsertionCallback(function(elem){
	    $(elem).find('select.nuclide-select').nuclideselect()
	})

//	$('.rai-comment a[href$="#genericModal"').genericmodal()
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
	    var selectedValues = []
	    $elem.find('option').each(
		function(){
		    if ($(this).prop('selected') == true){
			selectedValues.push($(this).val());
		    }
		    $(this).attr('selected', false);
		    var txt = $(this).text().split('|')
		    var subline = txt.length > 1 ? '<span class="text-muted">'+txt[1]+'</span>' : ''
		    if ($(this).val() !== undefined){ 
			self.$components.optionSurrounder.append(
			    $('<li class="list-group-item d-flex align-items-center" data-type-and-select-value="'
			      + $(this).val()+'">'+
			      '<span class="status"><i class="selected-icon fas fa-check"></i><i class="not-selected-icon far fa-circle"></i></span>'+
			      '<span><h6>'+txt[0]+'</h6>'+subline+'</span></li>'
			     )
			)
		    }
		}
	    )
	    
	    self.$components.emptyOption = $('<option value="">--</option>');
	    $elem.append(self.$components.emptyOption);
	    self.$components.emptyOption.attr('selected', true)
	    self.$components.wrapper.append(self.$components.optionSurrounder)
	    self.$components.optionSurrounder.toggle();
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
		$elem.find('option[value="'+value+'"]').prop('selected',true);
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

	    // init initial values
	    var evt = $.Event('click');
	    for (var count = 0; count < selectedValues.length; count ++){
		self.$components.optionSurrounder.find('li[data-type-and-select-value="'+selectedValues[count]+'"]').trigger(evt);
		self.$components.optionSurrounder.hide()
	    }
	}
	return cls;
    })(),
}
$.widget(
    'raiwidgets.hideshow',
    {
	options : {
	    labelShow : 'Anzeigen',
	    labelHide : 'Verbergen',
	    buttonPos : 'before',
	    initial : 'shown'
	},
	_create : function(){
	    // read options from element
	    if (this.element.data('hide-show-show') !== undefined){
		this.options['labelShow'] = this.element.data('hide-show-show');
	    }
	    if (this.element.data('hide-show-hide') !== undefined){
		this.options['labelHide'] = this.element.data('hide-show-hide');
	    }
	    if (this.element.data('hide-show-button-position') !== undefined){
		this.options['buttonPos'] = this.element.data('hide-show-button-position');
	    }
	    if (this.element.data('hide-show-initial') !== undefined){
		this.options['initial'] = this.element.data('hide-show-initial');
	    }
	    this.$btnText = $('<span></span>');
	    this.$btnIconWrapper = $('<span class="ml-1"></span>')
	    this.$showIcon = $('<i class="fas fa-caret-right"></i>')
	    this.$hideIcon = $('<i class="fas fa-caret-down"></i>')
	    var self = this
	    this.$btn = $('<a href="#"></a>')
		.append(this.$btnText)
		.append(this.$btnIconWrapper)
		.click(function(){self._toggle()})
	    
	    if (this.options['buttonPos'] == 'before'){
		this.$btn.insertBefore(this.element)
	    } else {
		this.$btn.insertAfter(this.element)
	    }
	    if (this.options['initial'] == 'shown'){
		this.element.addClass('hswidget-hidden')
	    } else {
		this.element.addClass('hswidget-shown')
	    }
	    this._toggle()
	},
	_toggle : function(){
	    var label, $icon;
	    if (this.element.hasClass('hswidget-shown')){
		label = this.options.labelShow
		$icon = this.$showIcon
		this.element
		    .removeClass('hswidget-shown')
		    .addClass('hswidget-hidden')
		    .hide(200)
	    } else {
		label = this.options.labelHide
		$icon = this.$hideIcon
		this.element
		    .removeClass('hswidget-hidden')
		    .addClass('hswidget-shown')
		    .show(200)
	    }
	    this.$btnText.text(label);
	    this.$btnIconWrapper.empty().append($icon)
	}
    }
    
)
$.widget('raiforms.dependingfield', {
    _create : function(){
	var dependsObj = this.element.data('depends-on')
	
	var self = this;
	for (var item in dependsObj) {
	    var $item = $('[name='+item+']')
	    $item.change(function(evt){
		self._toggle($(this), dependsObj[item])
	    }).each(
		function(){
		    self._toggle($item, dependsObj[item])
		}
	    )
	}
    },
    _toggle : function($elem, values){
	var self = this, $fg;
	if (self.element.hasClass('form-group')){
	    $fg = self.element;
	} else {
	    $fg = self.element.find('.form-group')
	}
	$elem = $elem.filter(':checked')
	var checked = $elem.prop('checked') ? ':checked' : ':unchecked'
	if (values.indexOf($elem.val()) > -1 || values.indexOf(checked) > -1 ){
	    
	    $fg.addClass('required')
	    self.element.show(200);
	} else {
	    $fg.removeClass('required')
	    self.element.hide(200);
	}
    }
})

$.widget(
    'raiwidgets.ajaxify',
    {
	options : {
	    successCallback : undefined,
	    failCallback : undefined,
	    method : 'POST',
	    updateIcon : undefined
	},
	_create : function(){
	    if (this.element.data('ajaxify-container') !== undefined){
		this.$container = $(this.element.data('ajaxify-container'))
	    } else {
		this.$container = this.element
	    }
	    if (this.element.data('ajaxify-method') !== undefined){
		this.options['method'] = this.element.data('ajaxify-method')
	    }
	    if (this.element.data('ajaxify-update-icon') !== undefined){
		this.options['updateIcon'] = $(this.element.data('ajaxify-update-icon'))
	    }
	    this.$icon = $('<i class="fas fa-cog fa-spin"></i>')
	    var self = this;
	    this.element.click(function(evt){
		evt.preventDefault();
		var fnc
		if (self.options['updateIcon'] !== undefined){
		    self.options['updateIcon'].html('').append(self.$icon)
		}
		
		if (self.options.method == 'GET'){
		    fnc = $R.get
		} else {
		    fnc = $R.post
		}
		fnc(
		    self.element.attr('href'),
		    self._collectData()
		).fail(
		    function(){
			if (self.options.failCallback !== undefined){
			    self.options.failCallback()
			}
		    }
			
		).done(
		    function(data){
			if (self.options.successCallback !== undefined){
			    self.options.successCallback(data)
			} else {
			    self._replaceContent(data)
			}
		    }
		
		)
	    })
	},
	_collectData : function(){
	    return {}
	},
	_replaceContent : function(data){
	    var $content = $(data['content'])
	    $content.insertBefore(this.$container)
	    this.$container.remove()
	}
	
    }
)

$.widget(
    'raiwidgets.genericmodal',
    {
	options : {
	    'events' : ['click'],
	    'content' : null,
	    'title' : null,
	    'saveButtonLabel': 'Speichern',
	    'cancelButtonLabel': 'Abbrechen',
	    'applyButtonLabel': 'Anwenden',
	    'saveButton' : true,
	    'applyButton' : true,
	    'cancelButton' : true,
	    
	    
	},

	_create : function(){
	    this.$modal = $('#genericModal')
	    this.$saveButton = $('#btnSavegenericModal')
	    var self = this;
	    this.$applyButton = $('#btnApplygenericModal')
	    
	    this.$cancelButton = $('#btnCancelgenericModal')
	    this.$body = this.$modal.find('.modal-body').first()
	    this.$title = $('#genericModalTitle')
	    var splitVals = this.element.attr('href').split('#')
	    this.url = splitVals[0]
	    
	    for (var count = 0; count < this.options['events'].length; count ++){
		this.element.on(
		    this.options.events[count],
		    function(evt){
			evt.preventDefault()
			self._launch()
		    }
		)
	    }
	    
	},
	destroy : function(){
	    this.$saveButton.off('click')
	    this.$applyButton.off('click')
	    this.$cancelButton.off('click')
	    this.$body.html('')
	    this.$modal.modal('hide')
	},
	_launch : function(){
	    for (key in this.options){
		this._setOption(key, this.options[key])
	    }
	    var self = this;
	    this.$saveButton.click(
		function(evt){
		    self._trigger('onSave', null, {url : self.url, body : self.$body})
		}
	    )
	    this.$applyButton.click(
		function(evt){
		    self._trigger('onApply', null, {url : self.url, body : self.$body})
		}
	    )
	    this.$cancelButton.click(
		function(evt){
		    self._trigger('onCancel', null, {url : self.url, body : self.$body})
		}
	    )

	    this.$modal.modal('show')
	},
	_setOption: function( key, value ) {
	    if ( key === "saveButtonLabel" ) {
		this.$saveButton.html( value );
	    }
	    if ( key === "cancelButtonLabel" ) {
		this.$cancelButton.html( value );
	    }
	    if ( key === "applyButtonLabel" ) {
		this.$applyButton.html( value );
	    }
	    if ( key === "title" ) {
		this.$title.html( value );
	    }
	    if ( key === "content" ) {
		if (value === null){
		    this._fetchContentFromHref()
		} else {
		    this.$body.html(value)
		    
		    self._trigger('contentReady', null, this.$body)
		}
	    }
	   
	    this._super( key, value );
	},
	_fetchContentFromHref : function(){
	    var html, self=this
	    $R.get(this.url).done(
		function(data){
		    self.$body.html(data['html']);
		    self._trigger('contentReady', null, self.$body)
		}
	    )
	    
	}
    }
)

$.widget(
    'raiwidgets.showhidecontroller',
    {
	options : {
	    targetContainer : null,
	    targetClass : null,
	    showButton : null,
	    hideButton : null
	},
	_create : function(){
	    this.options.targetClass = this.element.data('show-hide-elements-class')
	    this.options.targetContainer = this.element.data('show-hide-elements-container')
	    this.options.$controller = this.element.find('.show-hide-controller-input')
	    this.options.hideButton = this.element.find('input[value="hide"]')
	    this.elements = $(this.options.targetContainer).find('.'+this.options.targetClass)

	    var self = this
	    this.options.$controller.change(function(){
		if ($(this).prop('checked')){
		    self.elements.show().css('listStyleType', 'none')
		} else {
		    self.elements.hide()
		}
	    })
	}
    }
)

$.widget(
    'raiwidget.displayastable',
    {
	options : {
	    headings : ['label', '.label'],
	    longHeading : 'h4'
	    
	},
	
	_create : function(){
	    // rows for the table
	    this.$rows = this.element.find('.display-as-table-row')
	    this._setupTable()
	    this._populateTableHead()
	    this._populateTable()
	    // move the remaining parts of this element to somewhere invisible.
	    this.$storage = $('<div />').insertBefore(this.element).css({
		position : 'relative'
	    })
	    this.element.css({
		position : 'absolute',
		width: '0',
		height: '0',
		top : '-10000px'
		
	    }).appendTo(this.$storage)
	    // get unique fields
	    var classes = this.element.attr('class').split(' '),
		uniqueFields = []
	    var self = this
	    for (var count = 0; count < classes.length; count ++){
		if (classes[count].startsWith('unique--')){
		    var fieldId = classes[count].substr(8)
		    this.$table.find('input[name$="'+fieldId+'"]').change(
			function(evt){
			    var idParts = $(this).attr('id').split('-')
			    var fid = idParts[idParts.length - 1]
			    self.$table.find('input[id$="'+fid+'"]').prop('checked', false);
			    $(this).prop('checked', true)
			}
		    )
									 
		}
	    }

	},
	_populateTableHead : function(){
	    var self = this
	    // populate head with labels from first row
	    var first_row = this.$rows.first()
	    first_row.children().each(
		function(){
		    var $th = $('<th></th>').appendTo(self.$theadrow)
		    for (var count = 0; count < self.options.headings.length; count ++){
			var candidates = $(this).find(self.options.headings[count])
			if (candidates.length > 0){
			    candidates.first().contents().appendTo($th)
			    break
			}
		    }
		    
		}
	    )
	},
	_populateTable : function(){
	    var self = this
	    this.$rows.each(
		function(){
		    var $currentRow = $('<tr />').appendTo(self.$tbody)
		    var fieldcounter = 0;
		    $(this).children().each(
			function(){
			    // check for a .form-group in the row
			    var $fgroups = $(this).find('.form-group'),
				$currentField = $('<td />').appendTo($currentRow)
			    if (fieldcounter == 0){
				$currentField.css('position', 'relative')
				$('<span class="fake-label"></span>').appendTo($currentField)
			    }
			    fieldcounter++;
			    if ($fgroups.length > 0){
				// Assume only one form-group in the row...
				var $fgroup = $fgroups.first()

				// remove the label candidates
				for (var count = 0; count < self.options.headings.length; count ++){
				    $(this).find(self.options.headings[count]).each(
					function(){
					    if ($(this).hasClass('custom-control-label')){
						$(this).html('')
					    } else {
						$(this).remove()
					    }
					}
				    )
				}
				
				$fgroup.appendTo($currentField)
			    } else {
								// remove the label candidates
				for (var count = 0; count < self.options.headings.length; count ++){
				    $(this).find(self.options.headings[count]).each(
					function(){
					    if ($(this).hasClass('custom-control-label')){
						$(this).html('')
					    } else {
						$(this).remove()
					    }
					}
				    )
				}

				$(this).appendTo($currentField)
			    }
			    $currentField.appendTo($currentRow)
			}
		    )
		}
	    )
	    // look if this is inside a fieldset within the current form
	    var $parent = this.element.parent(),
		inFieldset = false
	    while ($parent.length > 0 && $parent.prop('tagName') != 'FORM'){
		if ($parent.prop('tagName') == 'FIELDSET'){
		    inFieldset = true
		    break
		} else {
		    $parent = $parent.parent()
		}
		    
	    }
	    if (inFieldset){
		this.$table.insertBefore(this.element)
	    } else {
		var $fieldset = $('<fieldset />')
		// look for a heading for the fieldset
		var $headings = this.element.find(this.options['longHeading'])
		if ($headings.length > 0){
		    $('<legend />').html($headings.first().html()).appendTo($fieldset)

		}
		this.$table.appendTo($fieldset)
		$fieldset.insertBefore(this.element)
	    }
	},
	_setupTable : function(){
	    // setup table
	    this.$table = $('<table></table>')
	    this.$thead = $('<thead></thead>').appendTo(this.$table)
	    this.$theadrow = $('<tr></tr>').appendTo(this.$thead)
	    this.$tbody = $('<tbody></tbody>').appendTo(this.$table)
	}

	   
    }
)

$.widget(
    'raiwidgets.editingcontroller',
    {
	options : {
	    controlFields : ['input', 'textarea', 'select'],
	    $container : null,
	    inputName : 'allow_edit'
	},
	_create : function(){
	    var parentContainerSelector = this.element.data('editing-controller-parent-container')
	    if ( parentContainerSelector !== undefined)
	    {
		this.options.$container = this.element.parents(parentContainerSelector).first()
	    }
	    this.$control = this.element.find('input[name="'+this.options.inputName+'"]').first()
	    var self = this
	    this.$control.change(
		function(evt){
		    self._setEnabledState($(this).prop('checked'))
		}
	    )
	    self._setEnabledState(this.$control.attr('checked') == "checked")
	    
	},
	_setEnabledState : function(tf){
	    if (typeof(tf) !== 'boolean'){
		tf = (tf == "true");
	    }
	    for (var count = 0; count < this.options.controlFields.length; count++){
		var $elems = this.options.$container.find(this.options.controlFields[count])
		$elems.each(
		    function(){
			$(this).prop('readonly', !tf)
			var thisId = $(this).attr('id')
			// look for labels and add/remove .disabled
			if (!tf){
			    $('label[for="'+thisId+'"]').addClass('disabled')
			} else { 
			    $('label[for="'+thisId+'"]').removeClass('disabled')
			}
		    }
		)
	    }
	    //switches should always work
	    this.$control.prop('disabled', false)
	}
    }
)

$.widget(
    'raiwidget.documentupload',
    {
	_create : function(){
	    this.$input = this.element.find('input[type="file"]')
	    this.$label = this.element.find('label')
	    var self = this
	    this.$label[0].addEventListener('dragenter', function(evt){
		evt.stopPropagation();
		evt.preventDefault();
	    	self.$label.addClass('drag-enter')
		
	    }, false)
	    this.$label[0].addEventListener('dragleave', function(evt){
		evt.stopPropagation();
		evt.preventDefault();
	    	self.$label.removeClass('drag-enter')
		
	    }, false)
	    this.$label[0].addEventListener('dragover', function(evt){
		evt.stopPropagation();
		evt.preventDefault();
		
	    }, false)
	    this.$label[0].addEventListener('drop', function(evt){
		evt.stopPropagation();
		evt.preventDefault();
		self._preview(evt.dataTransfer.files)
		
	    }, false)

	    this.$previewList = $('<ul class="list-group add-file-list"></ul>').appendTo(this.element)
	    var self = this
	    this.$input.change(function(evt){
		self._preview(evt.target.files)
	    })
	},
	_preview : function(fileList){
	    
	    for (var count = 0; count < fileList.length; count ++){
		this._previewItem(fileList[count])
	    }
	},
	_previewItem : function( item ){
	    var $li = $('<li class="list-group-item" />');
	    $li.append($(
		'<div class="d-flex justify-content-between">'+
		    '  <h6>'+item.name+'</h6>'+
		    '  <div>'+
		    '    <button class="btn btn-primary">'+
		    '      <i class="fas fa-upload"></i> Datei hochladen'+
		    '    </button>'+
		    '  </div>'+
		    '</div>'+
		    '<div class="row">'+
		    '  <div class="document-icon col-md-1"></div>'+
		    '    <div class="form-group col-md-3">'+
		    '      <label for="">Dokument-Titel</label>'+
		    '      <input class="document-title-input" id="" type="text" class="form-control" value="'+item.name+'">'+
		    '    </div>'+
		    '    <div class="form-group col-md-4">'+
		    '      <label for="">Dokument-Beschreibung</label>'+
		    '      <input class="document-description-input" id="" class="form-control" type="text" value="" placeholder="Beschreibung für das Dokument">'+
		    '    </div>'+
		    '  </div>'+
		    '</div>'))
	    this.$previewList.append($li)
	    this._makeIcon(item, $li.find('.document-icon').first())
	    var self = this
	    $li.find('button').click(function(evt){
		evt.preventDefault()
		self._upload($(this))
	    })
	},
	_upload : function($elem){
	    var $li = $elem.parents('li').first(),
		$iconContainer = $li.find('.document-icon').first(),
		fd = new FormData(),
		$progressWrapper = $('<div class="upload-progress-wrapper"/>').insertAfter($elem),
		$progressCounter = $('<span class="upload-progress-counter">0 %</span>').appendTo($progressWrapper),
		$progressBar = $('<span class="upload-progress-bar" />').appendTo($progressWrapper),
		url = $elem.parents('[data-add-files-url]').first().data('add-files-url'),
		$svg = $iconContainer.find('svg').first(),
		iconClass = $svg.data('icon'),
		iconPrefix = $svg.data('prefix')
	    
	    fd.append('title', $li.find('.document-title-input').first().val())
	    fd.append('description', $li.find('.document-description-input').first().val())
	    fd.append('file', $iconContainer[0].file)

	    

	    $elem.hide()
	    var self = this
	    var jqXHR = $R.post(
		url,
		{
		    data : fd,
		    processData : false,
		    contentType : false, //'multipart/form-data',
		    xhr : function(){
			var xhr = $.ajaxSettings.xhr();
			xhr.upload.addEventListener(
			    'progress',
			    function(e){
				if (e.lengthComputable){
				    var p = Math.round(100 * e.loaded/e.total) 
				    $progressCounter.html(p)
				    $progressBar.css('width',p+'%')
				}
			    },
			    false
			)
			xhr.upload.addEventListener(
			    'load',
			    function(e){
				$progressCounter.html('100')
			    },
			    false
			)
			return xhr
		    }
		}
	    )
		.done(function(data){
		    if (data.status == '200'){

			$newli = $('<li />')
			    .addClass('file-field list-group-item')
			    .attr('data-toggle', 'tooltip')
			    .attr(
				'title',
				'Erstellt am ' + data.created_at +
				    ', hochgeladen von '+ data.uploaded_by)
			$fileInfo = $('<div/>')
			    .addClass('file-info')
			    .appendTo($newli)
			$fileIcon = $('<span />')
			    .addClass('file-icon')
			    .appendTo($fileInfo)
			$icon = $('<i/>')
			    .addClass('fa-fw')
			    .addClass(iconPrefix)
			    .addClass('fa-'+iconClass)
			    .appendTo($fileIcon)
			$wrapper = $('<div/>')
			    .appendTo($fileInfo)
			$h6 = $('<h6 />')
			    .addClass('file-title editable-field-wrapper')
			    .appendTo($wrapper)
			$field = $('<span />')
			    .addClass('editable-field')
			    .attr('data-activated-by', '#edit-button-title-'+data.pk)
			    .attr('data-field-label', 'title')
			    .attr('data-edit-url', data.edit_url)
			    .html(data.title)
			    .appendTo($h6)
			$(
			    '<span id="edit-button-title-'+data.pk+'" class="edit-button">'
				+'<i class="fas fa-pen"></i>'
				+'</span>'
			).appendTo($h6)
			$p = $('<p />')
			    .addClass('text-muted editable-field-wrapper')
			    .appendTo($wrapper)
			
			var description = "Keine Beschreibung angegeben."
			if (data.description != ""){
			    description = data.description;
			}
			$desc = $('<span />')
			    .addClass('editable-field')
			    .attr('data-activated-by', '#edit-button-desc-'+data.pk)
			    .attr('data-field-label', 'description')
			    .attr('data-edit-url', data.edit_url)
			    .html(description)
			    .appendTo($p)
			$(
			    '<span id="edit-button-desc-'+data.pk+'" class="edit-button">'
				+'<i class="fas fa-pen"></i>'
				+'</span>'
			).appendTo($p)
			$menu = $('<div />')
			    .addClass('file-field-menu')
			    .appendTo($newli)
			$delete = $('<a />')
			    .addClass('btn file-delete-button ajaxify')
			    .attr('href', data.delete_url)
			    .appendTo($menu)
			$delIcon = $('<i class="fas fa-trash-alt" />')
			    .appendTo($delete)
			$delLabel = $('<span>Datei löschen</span>')
			    .addClass('ml-1')
			    .appendTo($delete)

			
			$download = $('<a />')
			    .addClass('btn')
			    .appendTo($menu)
			$downIcon = $('<i class="fas fa-download" />')
			    .appendTo($download)
			$downLabel = $('<span>Herunterladen</span>')
			    .addClass('ml-1')
			    .appendTo($download)
			$newli.hide()
			$newli.insertBefore(self.element)
			$li.hide(200, function(){
			    $li.remove()
			    $newli.show(300)
			    $field.editable()
			    $desc.editable()
			    $delete.ajaxify(
				{
				    successCallback : function(data){
					var $elem = $delete.parents('li').first()
					if (data.status == "200"){
					    $elem.hide(200, function(){
						$elem.remove()
					    })
					}
				    }
				}
			    )
			})
			
		    }
		})
		.fail(function(data){
		    console.log('error')
		})
	    
	    console.log(jqXHR)
	},
	_makeIcon : function(item, $container){
	    var parts = item.type.split('/'),
		nameParts = item.name.split('.'),
		ending = nameParts[nameParts.length-1],
		addIcon = true,
		icon = 'file'
	    
	    switch (parts[0])
	    {
		case 'image':
		switch(ending.toLowerCase())
		{
		    case 'jpg':
		    case 'jpeg':
		    case 'png':
		    this._makeThumbnail(item, $container)
		    addIcon = false
		    break
		    default:
		    icon = 'file-image'
		}
		break
		
		case 'application':
		switch (ending.toLowerCase())
		{
		    case 'pdf' :
		    icon = 'file-pdf'
		    break
		    case 'doc':
		    case 'docx':
		    icon = 'file-word'
		    break
		    case 'xls':
		    case 'xlsx':
		    icon = 'file-excel'
		    break
		    case 'ppt':
		    case 'pptx':
		    icon = 'file-powerpoint'
		    break
		}
		case 'text':
		switch(parts[1])
		{
		    case 'plain':
		    icon = 'file-alt'
		    break
		}
		break
		
	    }
	    if (addIcon){
		$container.append($('<span><i class="fas fa-'+icon+'"></i></span>'))
		$container[0].file = item
	    }
	},
	_makeThumbnail : function(item, $container){
	    var $img = $('<img>').appendTo($container),
		img = $img[0]
	    $container[0].file = item
	    var reader = new FileReader()
	    reader.onload = (
		function(aImg){
		    return function(e) { aImg.src = e.target.result; }; 
		}
	    )(img)
	    reader.readAsDataURL(item)
	}
    }
)

$.widget(
    'raiwidgets.treeviewselect',
    {
	_create : function(){

	    var self = this
	    
	    this.idCounter = 0
	    this.fetchUrl = this.element.data('fetch-mail-url')
	    this.$list = this.element.find('dl').first()
	    this.$list.addClass('tree-view')
	    this.$selectedList = this.element.find('ul.selected-email-to-list').first()
	    this.$mainWrapper = this.element.find('.main-wrapper')
	    this.$input = this.element.find('input').first().focus(
		function(){
		    self.$mainWrapper.addClass('focus')
		}
	    ).blur(
		function(){
		    self.$mainWrapper.removeClass('focus')
		}
	    )
	    
	    
	    this.fieldname = this.$input.attr('name')
	    this.$input.attr('name', '').keyup(function(evt){
		self._search(evt)
	    }).attr('placeholder', 'Nutzer oder Gruppe suchen')
	    
	    this.$iGroup = this.$input.parents('.input-group')
	    this.$list.css('top', this.$list.position().top + 'px')
	    this.hiddenExplorerCss = this.$list.css(['maxHeight', 'borderWidth', 'overflow', 'top','bottom'])
	    this.$selectedValuesContainer = $('<div>').css({
		position: 'absolute',
		top: '-10000px',
		left:'-10000px',
		height:'0px',
		width:'0px'
	    })
		.appendTo(this.element)
	    

	    
	    this.$exploreBtn = this.element.find('.explore-button').first().click(
		function(){
		    self._toggleExplorer()
		}
	    )
	    this.$list.find('dt').addClass('closed').click(
		function(evt){
		    if(evt.originalEvent.ctrlKey){
			var $next = $(this).next('dd'), data = []
			
			$next.find('[data-select-value]').each(function(){
			    data.push($(this).data('select-value'))
			})
			var $elem = $(this)
			$(this).unmark({
			    done : function(){
				self._addAll($elem.html(), data)
			    }
			})
			
		    } else {
			if ($(this).hasClass('closed')){
			    $(this)
				.removeClass('closed')
				.addClass('open')
			} else {
			    $(this)
				.removeClass('open')
				.addClass('closed')
			}
		    }
		}
	    )

	    this.$list.find('dd[data-select-value]').click(
		function(){
		    self._addToSelected($(this).data('select-value'))
		}
	    )
	    this.$list.find('dd[data-fetch-value]').click(
		function(){
		    self._fetchAndAdd($(this))
		}
	    )

	    this._parseInput()
	},
	/* we might receive some values in the input (from a non-valid form, for example)*/
	_parseInput : function(){
	    // entries either look like a mail address or are appended with __<groupname>

	    if (this.$input.val().trim() == '')
		return
	    var rawValues = this.$input.val().split(','),
		tmp

	    // clear field
	    this.$input.val('')
	    var entries = {}, order = []
	    
	    for (var count = 0; count < rawValues.length; count++){
		tmp = rawValues[count].split('__')
		if (tmp.length == 2){
		    if (entries[tmp[1]] == undefined){
			entries[tmp[1]] = []
			order.push(tmp[1])
		    }
		    entries[tmp[1]].push(tmp[0].trim())
		} else {
		    entries[count] = tmp[0].trim()
		    order.push(count)
		}
	    }
	    var key
	    for (count = 0; count < order.length; count++){
		key = order[count]
		if(Array.isArray(entries[key])){
		    this._addAll(key, entries[key])
		} else {
		    this._addToSelected(entries[key])
		}
	    }
	    
	},
	_search : function(evt){
	    var val = this.$input.val().trim(),
		$matches

	    if (val == ''){
		this.$list.find('[data-fetch-value], [data-select-value], dt').unmark()
		this._hideExplorer()
	    } else {
		this._showExplorer()
		this.$list.find('dt,dd').hide()
		this.$list.find('[data-fetch-value], [data-select-value], dt').each(
		    function(){
			var $elem = $(this)
			$elem.unmark(
			    {
				done : function(){
				    $elem.mark(val)
				}
			    }
			)
		    }
		)
		$matches = this.$list.find('mark')
		$matches.parents('dd,dt').show().prev('dt').show().addClass('open')
	    }
	    
	},
	_addToSelected : function(address){
	    var $item = this._makeSelectedListItem(address).insertBefore(this.$input)
	    this._addToList($item)
	    this._hideExplorer()
	},
	_fetchAndAdd : function($item){
	    var self = this
	    $item.unmark(
		{
		    done : function(){
			$R.post(
			    self.fetchUrl,
			    {
				data : {
				    'pk' : $item.data('fetch-obj-pk'),
				    'id' : $item.data('fetch-collection-id')
				}
			    }
			)
			    .done(
				function(data){
				    var $newitem = self._makeSelectedListItem($item.html(), data.mails).insertBefore(self.$input)
				    self._addToList($newitem, $item.html())
				    self._hideExplorer()
				}
			    )
			    .fail(
			    )
			self._hideExplorer()
		    }
		}
	    )
	},
	_addAll : function(name, values){
	    var $item = this._makeSelectedListItem(name, values).insertBefore(this.$input)
	    this._addToList($item, name)
	    this._hideExplorer()
	},
	_constructCheckbox : function(value, group){
	    var re = /\(.*\)/
	    if (group === undefined){
		group = ''
	    } else {
		group= '__'+group.replace(re,'').trim()
	    }
	    var $check = $('<input type="checkbox" name="'+this.fieldname+'" checked>')
		.attr('id', 'tree_select_item_'+this.idCounter)
		.appendTo(this.$selectedValuesContainer)
		.data('for-id', this.idCounter)
		.val(value+group)
	    this.idCounter++;
	    return this.idCounter - 1; 
	},

	_removeFromList : function($elem){
	    var $par = $elem.parents('.selected-mail-container').first(),
		isInGroup = $par.prop('tagName').toUpperCase() == 'LI',
		count, $grandpar
	    
	    if ($par.attr('data-for-checkbox-id') !== undefined){
		$('#tree_select_item_'+$par.data('for-checkbox-id')).remove()
	    }
	    $par.find('[data-for-checkbox-id]').each(
		function(){
		    console.log($(this))
		    $('#tree_select_item_'+$(this).data('for-checkbox-id')).remove()
		}
	    )
	    $par.hide(200, function(){
		if(isInGroup){
		    // reduce by one since the current item will be deleted
		    count = $par.parents('ul').first().find('li').length - 1
		    $grandpar = $par.parents('.selected-mail-container').first()
		    $grandpar.find('.group-counter').first()
			.text('('+count+')')
		}
		$par.remove()
		if (count == 0){
		    $grandpar.hide(200, function(){
			$grandpar.remove()
		    })
		}
	    })	    
	},
	_addToList : function($elem, name){
	    var self = this, id
	    
	    if ($elem.attr('data-email-address') !== undefined){
		id = this._constructCheckbox($elem.data('email-address'))
		$elem.attr('data-for-checkbox-id', id)
	    }
	    $elem.find('[data-email-address]').each(function(){
		id = self._constructCheckbox($(this).data('email-address'), name)
		$(this).attr('data-for-checkbox-id', id)
	    })
	    this.$input.val('')
	    this.$input.focus()
	},
	/*
	  make an item suitable for showing in the list of selected accounts
	  Options:
	  name: is the name displayed
	  values (optional): if the item is for a group, these are the single values
	  
	  the formatting of values should be "Some string <mail@address.com>"

	  if values is omitted, `name` should follow this formatting, too 
	 */
	_makeSelectedListItem : function(name, values){
	    var $removeBtn = $('<span><i class="fas fa-times-circle fa-fw"></i></span>')
		.addClass("remove-button inline-button"),
		$expandBtn = $('<span><i class="fas fa-ellipsis-v fa-fw"></i></span>')
		.addClass("expand-button inline-button"),
		$showBtn = $('<span><i class="fas fa-list-alt fa-fw"></i></span>')
		.addClass("show-button inline-button"),
		$span = $('<span class="selected-mail-container" />'),
		re = /<.*>/,
		re2 = /\(.*\)/,
		single = false,
		self = this,
		$li, $btn
	    name = name.replace(re2,'').trim()
	    
	    if (values === undefined){
		$span.attr('data-email-address', name).text(name.replace(re,'').trim())
		single = true
	    } else {
		var $ul = $('<ul />')
		for (var count = 0; count < values.length; count ++){
		    
		    $li = $('<li class="selected-mail-container">'+values[count].replace(re,'').trim()+'</li>')
			.attr('data-email-address', values[count])
			.appendTo($ul)
		    $btn = $removeBtn.clone().click(function(){
			self._removeFromList($(this))
		    }).appendTo($li)
		}
		$span.append($('<span class="group-name">'+name+'</span>'))
		$span.append('<span class="group-counter">('+values.length+')</span>').append($ul)
	    }
	    $span.append($removeBtn)

	    $removeBtn.click(function(){
		self._removeFromList($(this))
	    })
	    if (!single){
		$span.append($showBtn).append($expandBtn)
		$expandBtn.click(function(){
		    var $par = $(this).parents('.selected-mail-container').first()
		    if ($par.hasClass('expanded')){
			$par.removeClass('expanded')
		    } else {
			$par.addClass('expanded')
		    }
		})
		$showBtn.click(function(){
		    self._showGroup($(this))
		})
	    }

	    
		
	    return $span
	},
	_showGroup : function($elem){
	    // shows the group in a modal
	    var $genericModal = $('#genericModal'),
		$modalSaveBtn = $('#btnSavegenericModal').text('Übernehmen'),
		$modalBody = $genericModal.find('.modal-body').first().html(''),
		$modalTitle = $('#genericModalTitle'),
		$list = $('<ul class="list-group group-selection-modal" />'),
		$par = $elem.parents('.selected-mail-container').first(),
		$items = $par.find('[data-email-address]'),
		groupName = $par.find('.group-name').first().text(),
		$listItem, address, name, mail, $wrapper, $btn,
		$input = $('<input type="text" placeholder="Gruppe durchsuchen" class="search-field form-control"/>'),
		$inputWrapper = $('<div class="mb-2">').append($input),
		$counter = $('<span>').text('('+$items.length+')'),
		self = this
	    
	    
	    $modalTitle.text(groupName).append($counter)
	    $items.sort(function(a,b){
		var $a = $(a),
		    $b = $(b)
		return $a.data('email-address') < $b.data('email-address') ? -1 :
		    $a.data('email-address') > $b.data('email-address') ? 1 : 0
		    
	    }).each(function(){
		address = $(this).data('email-address').split('<')
		name = address[0]
		mail = '&lt;'+address[1].replace('>','&gt;')
		
		$listItem = $('<li class="list-group-item mb-0" />').addClass('d-flex justify-content-between')
		$listItem[0].origItem = $(this)
		$wrapper = $('<div />')
		$wrapper.append($('<div>'+name+'</div>').append('<div class="text-muted">'+mail+'</div>'))
		$listItem.append($wrapper)
		$wrapper = $('<div />')
		$btn = $('<span class="restore-btn"><i class="fas fa-plus-circle"></i></span><span class="delete-btn"><i class="fas fa-times-circle"></i></span>').appendTo($wrapper)
		$btn.css('cursor', 'pointer').click(function(){
		    var $item = $(this).parents('li').first()
		    if ($item.hasClass('deleted')){
			$item.removeClass('deleted')
		    } else {
			$item.addClass('deleted')
		    }
		    $counter.text('('+$list.find('li').not('li.deleted').length+')')
		})
		$wrapper.appendTo($listItem)
		$list.append($listItem)
	    })
	    $modalBody.append($inputWrapper).append($list)
	    $genericModal.on('shown.bs.modal', function(){
		var $content = $genericModal.find('.modal-content').first(),
		    margin = 50,
		    vpHeight = $(window).height(),
		    listHeight = $list.height(),
		    offset = $content.height() - listHeight
		$list.css(
		    {
			'height': (vpHeight - margin - offset)+'px',
			'overflow': 'auto'
		    }
		)
	    })
	    $genericModal.on('hidden.bs.modal', function(){
		// clean up
		$modalSaveBtn.off('click')
		$modalBody.html('')
		$modalTitle.html('')
		$genericModal.off('shown.bs.modal').off('hidden.bs.modal')
		
	    })
	    $input.keyup(function(){
		var val = $input.val()
		if (val == ''){
		    $list.unmark({
			done : function(){$list.find('li').addClass('d-flex').show()}
		    })
		} else {
		    $list.unmark({
			done : function(){
			    $list.mark(val, {
				done : function(){
				    $list.find('li').removeClass('d-flex').hide()
				    $list.find('mark').parents('li').addClass('d-flex').show()
				}
			    })
			}
		    })
		}
	    })
	    $modalSaveBtn.click(function(){
		var $deleted = $list.find('li.deleted')
		$deleted.each(function(){
		    // remove from lists expects something from within the <li> tag,
		    // but this.origItem is the li tag. Pass a child. Usually it's the button. 
		    self._removeFromList(this.origItem.find('.remove-button').first())
		})
		
		$genericModal.modal('hide')
	    })
	    
	    $genericModal.modal('show').modal('handleUpdate')
	    
	    
	},
	_toggleExplorer : function(){
	    if (this.$exploreBtn.hasClass('closed')){
		this._showExplorer()
	    } else {
		this._hideExplorer()
	    }
	},
	_showExplorer : function(){
	    this.$exploreBtn.addClass('opened').removeClass('closed')
	    var vpHeight = $(window).height(),
		borderOffset = 5,
		scrollTop = $(window).scrollTop(),
		yPos = this.$list.offset().top,
		heightToBottom = vpHeight-yPos+scrollTop,
		pageOffset = $('.page-header').first().offset().top + $('.page-header').first().height(),
		heightToTop = this.$input.offset().top-scrollTop-pageOffset,
		height, top, bottom

	    if ((heightToBottom < 100) && (heightToTop > heightToBottom)){
		height = heightToTop
		bottom = this.$iGroup.height()
		top = 'auto'
	    } else {
		height = heightToBottom
		top = this.$list.position().top
		bottom = 'auto'
	    }
	    this.$list.css({
		'maxHeight': (height-borderOffset) + 'px',
		'borderWidth' : '2px',
		'overflow' : 'auto',
		'top' : top,
		'bottom': bottom
	    })
	},
	_hideExplorer : function(){
	    // clean up elements from search
	    this.$list.find('[style]').removeAttr('style')
	    this.$list.find('dt.open').removeClass('open').addClass('closed')
	    this.$exploreBtn.addClass('closed').removeClass('opened')
	    this.$list.css(this.hiddenExplorerCss)
	}
    }
)
$.widget(
    /* implements a single panel of the panel grind on the home-page
     * of RUBIONtail
     */ 
    'raiwidgets.panelgridpanel',
    {
	_create : function(parent){
	    this.parent = parent
	    // set options from data
	    if (this.element.data('grid-position') !== undefined)
		this.options['position'] = this.element.data('grid-position')
	    if (this.element.data('grid-max-width') !== undefined)
		this.options['maxCols'] = this.element.data('grid-max-width')
	    if (this.element.data('grid-min-width') !== undefined)
		this.options['minCols'] = this.element.data('grid-min-width')
	    if (this.element.data('grid-max-height') !== undefined)
		this.options['maxRows'] = this.element.data('grid-max-height')
	    if (this.element.data('grid-min-width') !== undefined)
		this.options['minRows'] = this.element.data('grid-min-height')
	    if (this.element.data('grid-width') !== undefined)
		this.options['colSpan'] = this.element.data('grid-width')
	    if (this.element.data('grid-height') !== undefined)
		this.options['rowSpan'] = this.element.data('grid-height')

	    this.$parentRow = this.element.parents('.row').first()
	    if(this.$parentRow.data('grid-columns') !== undefined){
		this.options['colsAvailable'] = this.$parentRow.data('grid-columns')
	    }
	    this.$menu = this.element.find('.panel-menu').first()

	    
	},
	isResizable : function(){
	    return this.options['maxRows'] != this.options['minRows'] || this.options['maxCols'] != this.options['minCols']
	},
	isDraggable : function(){
	    return self.options['position'] != -1
	},
	setDataPosition : function(row, col){
	    this.element.data('grid-col', col)
	    this.element.data('grid-row', row)
	    this._addMenu()
	},
	_changeSize : function(rs, cs){
	    console.log('in _changeSize', rs, cs)
	    this.element.data('grid-width', cs)
	    this.element.data('grid-height', rs)
	    this.options['colSpan'] = cs
	    this.options['rowSpan'] = rs
	    this._trigger('sizeChanged')
	},
	_addMenu : function(){
	    var self = this
	    if (this.isResizable()){
		// since this is called every time the layout is rendered
		// clear menu first

		this.$menu.find('*').remove()

		// Built container
		var $dropdown = $('<div />')
		    .addClass('dropdown-menu')
		    .attr('aria-labelled-by', 'btn_dd_'+this.uuid)

		// size sub-menu-header
		var $szHeader = $('<h6">Größe ändern</h6>')
		    .addClass('dropdown-header')
		    .appendTo($dropdown)
		
		
		for (var rs = this.options['minRows']; rs <= this.options['maxRows']; rs++){
		    for (var cs = this.options['minCols']; cs <= this.options['maxCols']; cs++){
			$btn = $('<button>'+rs+'×'+cs+'</button>')
			    .appendTo($dropdown)
			    .attr('type','button')
			    .data('grid-rs', rs)
			    .data('grid-cs', cs)
			    .addClass('dropdown-item')
			if (
			    this.options['colSpan'] == cs
				&& this.options['rowSpan'] == rs
			){
			    $btn.addClass('disabled')
				.attr('aria-disabled', true)
				.attr('tabindex',-1)
			} else {
			    $btn.click(function(evt){
				evt.preventDefault()
				self._changeSize($(this).data('grid-rs'), $(this).data('grid-cs'))
			    })
			}
		    }
		}

		// make menu button
		var $menuBtn = $('<button type="button" />')
		    .attr('id', 'btn_dd_'+this.uuid)
		    .attr('data-toggle', 'dropdown')
		    .attr('aria-haspopup','true')
		    .attr('aria-expanded','false')
		    .addClass('btn btn-xs')
		var $iconContainer = $('<span />')
		    .appendTo($menuBtn)
		var $menuIcon = $('<i />')
		    .addClass(this.options['menuIconFont'])
		    .addClass(this.options['menuIcon'])
		    .appendTo($iconContainer)
	   
	
		this.$menu.append($menuBtn)
		this.$menu.append($dropdown)

		
	    }
	}
    }
)
$.raiwidgets.panelgridpanel.prototype.options = {
    rowSpan : 1,
    colSpan : 1,
    position : 0,
    maxRows: 1,
    minRows : 1,
    maxCols : 1,
    minCols : 1,
    colsAvailable : 3,
    menuIconFont:'fas',
    menuIcon : 'fa-ellipsis-h'
}


$.widget(
    /* implements the additional functionality of the "add-panel" panel
     */
    'raiwidgets.addpanelpanel',
    {
	_create : function(parent){
	    this.parent = parent;
	    // find checkboxes
	    var self = this
	    this.element.find('input[type=checkbox]').change(
		function (evt){
		    self._trigger('panelAdded', evt, {
			panelKey : $(this).attr('name')
		    })
		}
	    )
	}
    }
)
$.widget(
    /* This implements the panels on the home-page of RUBIONtail
     * 
     * Data for sizing is included as data attributes on the single panels (aka cards)
     */
    'raiwidgets.panelgrid',
    {
	_addChild : function(child){
	    var self = this
	    if (child.data('raiwidgets-panelgridpanel') === undefined){
		child.panelgridpanel({
		    'sizeChanged' : function(){
			self._layout()
		    }
		})
	    } 
	    var instance = child.panelgridpanel('instance')

	    if (instance.options.position < 0){
		this.appendedChildren.push(instance)
	    } else {
		this.children.push(instance)
	    }
	},
	_sortChildren : function(){
	    this.children.sort(
		function(a,b) {
		    return a.option('position') - b.option('position')
		}
	    )
	},
	_layout : function(){
	    // clear the current grid
	    this.element.children().remove()
	    this._sortChildren()
	    var row, col, r, c, grid = [],
		childCounter = 0,
		children = this.children.concat(this.appendedChildren),
		rowSpans = [ 1 ],
		area = 0

	    for (var cnt = 0; cnt < children.length; cnt ++){
		area += children[cnt].options['rowSpan'] * children[cnt].options['colSpan']
	    }
	    for (cnt = 0; cnt < Math.ceil(area/3); cnt ++){
		grid.push([null, null, null])
	    }
	    console.log(grid, children)
	    for (row = 0; row < grid.length && childCounter < children.length; row++){
		for (col = 0;
		     col < grid[row].length && childCounter < children.length;
		     col ++){
		    console.log('row', row, 'col', col, 'grid[row][col]', grid[row][col])
		    if (grid[row][col] === null){
			rowSpans[row] = Math.max(rowSpans[row], children[childCounter].options['rowSpan'])
			for (r = 0; r < children[childCounter].options['rowSpan']; r++){
			    // expand grid if necessary
			    if ( r + row > grid.length - 1){
				grid.push([null, null, null])
				rowSpans.push(1)
			    }
			    // We don't check for cols that do not match...
			    // maybe we should...
			    for (c = 0; c < children[childCounter].options['colSpan']; c++) {
				grid[row + r][col + c] = childCounter
			    }
			}
			childCounter ++
		    }
		}
	    }


	    // inline-functions are not very nice, but anyway...
	    
	    var getRowSpan = function(rowIdx, colIdx, colSpan){
//		console.log('getRowSpan with rowIdx', rowIdx, 'colIdx', colIdx, 'colSpan', colSpan, 'grid (global)', grid)
		var span = 1
		if (rowIdx + 1 < grid.length){
		    var ext = true
		    var rowCnt = rowIdx + 1
		    
		    while (rowCnt < grid.length && ext){
			ext = false
			
			for (var colCnt = colIdx; colCnt < colIdx + colSpan; colCnt ++){
			    if (grid[rowCnt][colCnt] == grid[rowCnt-1][colCnt]){
				console.log('grid', rowCnt, colCnt, 'equals', rowCnt, colCnt-1)
				console.log(grid[rowCnt][colCnt],grid[rowCnt][colCnt-1])
				ext = true
				span++
				break
			    }
			}
			
			rowCnt++
			
		    }
		    
		}
//		console.log('getRowSpan returns', span)
		return span
	    }

	    var getColSpan = function(rowIdx, colIdx, rowSpan){
//		console.log('getColSpan with rowIdx', rowIdx, 'colIdx', colIdx, 'rowSpan', rowSpan, 'grid (global)', grid)
		var span = 1
		if (colIdx < 2){
		    var ext = true
		    var colCnt = colIdx + 1
		    while (colCnt < 3 && ext){
			ext = false
			for (var rowCnt = rowIdx; rowCnt < rowIdx + rowSpan; rowCnt++){
			    if (grid[rowCnt][colCnt] == grid[rowCnt][colCnt-1]){
				ext = true
				span++
				break
			    }
			}
			colCnt ++
			
		    }
		}
//		console.log('getColSpan returns', span)
		return span
	    }

	    function renderRow(row, col, colSpan, inner){

		if (inner === undefined)
		    inner = false
//		console.log('renderRow with row', row, 'col', col,'colSpan', colSpan,'inner', inner)
		var rowSpan = getRowSpan(row, col, colSpan),

		    $row = $('<div />')
		    .addClass('row panel-grid-row')
		    .attr('data-grid-rowspan', rowSpan)
		    .attr('data-grid-colspan', colSpan),
		    
		    colCnt = 0,
		    
		    $col
		
		while (colCnt < colSpan){
		    $col = renderCol(row, col+colCnt, rowSpan, colSpan, inner)
		    $row.append($col)
		    colCnt += parseInt($col.data('grid-colspan'))
		}
		return $row
	    }

	    function renderCol(row, col, rowSpan, outerColSpan, inner){
		// for renderCol, inner is set
		// outerColSpan is required for the column width only

//		console.log('renderCol with row', row, 'col', col,'rowSpan', rowSpan, 'outerColSpan', outerColSpan, 'inner', inner)
		
		var colSpan = getColSpan(row, col, rowSpan),

		    $col = $('<div />')
		    .addClass('panel-grid-col')
		    .attr('data-grid-rowspan', rowSpan)
		    .attr('data-grid-colspan', colSpan)
		    .addClass('col-md-'+12/outerColSpan  * colSpan),
		
		    rowCnt = 0,

		    $row
		if (inner){
		    // 
		    
		    // console.log('Adding panel at position',row, col)
		    // console.log('panel number is', grid[row][col])
		    var panel = children[grid[row][col]]
//		    console.log('panel is ', panel)
		    if (panel !== undefined){
			$col.append(panel.element)
			panel.setDataPosition(row, col)
		    }
		    
		} else {
		    while (rowCnt < rowSpan){
			// call renderRow with inner = true
			$row = renderRow(row+rowCnt, col, colSpan, true)
			$col.append($row)
			rowCnt += parseInt($row.data('grid-rowspan'))
		    }
		}
		return $col
	    }

	    // loop through the grid
	    var rowCounter = 0, $outerRow
	    while (rowCounter < grid.length){
		$outerRow = renderRow(rowCounter, 0, 3)
		this.element.append($outerRow)
		rowCounter += parseInt($outerRow.data('grid-rowspan'))
	    }
	},
	_addPanel : function(evt, data){
	    var self = this
	    $R.post(
		this.options['addPanelURL'],
		{
		    data : { panelId : data['panelKey'] }
		}
	    ).done(function(data){
		var panel = $(data['html']).panelgridpanel({
		    position : self.children.length,
		    sizeChanged : function(){
			self._layout()
			self._initAddPanel()
		    }
		})
		self._addChild(panel)
		self._layout()
		self._initAddPanel()
	    })
	},
	_initAddPanel : function(){
	    var self = this
	    this.$addPanel = this.element.find(
		self.options['addPanelSelector'])
		.first()
		.addpanelpanel({
		    'panelAdded' : function(evt, data){ self._addPanel(evt, data) }
		})
	    console.log('Add panel is', this.$addPanel)
	},

	_create : function(){
	    var self = this
	    
	    this.$children = this.element.find(this.options['childrenSelector'])
	    this.children = []
	    this.appendedChildren = []
	    this.$children.each(
		function(){ self._addChild($(this)) }
	    )

	    this._layout()
	    this._initAddPanel()
	    
	    this.options['addPanelURL'] = this.element.data('add-panel-url')

	},

    }
)
$.raiwidgets.panelgrid.prototype.options = {
    
    childrenSelector : '.grid-panel',
    addPanelSelector : '.add-panel-panel',
    addPanelURL : ''
}

$.widget(
    'raiwidgets.checkall',
    {
	_create : function(){
	    this.selector = this.element.data('check-all-name')
	    this.$inputs = $('[name="'+this.selector+'"]')
	    var self = this
	    console.log('check all on ',this.element)
	    this.element.change(function(){
		self.$inputs.prop('checked', $(this).prop('checked'))
	    })

	    this.$inputs.change(function(){
		var state
		var oldState = null
		self.$inputs.each(function(){
		    if (oldState == null){
			oldState = $(this).prop('checked')
		    }
		    state = $(this).prop('checked')
		    if (state != oldState){
			self.element.prop('indeterminate', true)
			state = null
			return false
		    }
		    oldState = state
		})
		if (state != null){
		    self.element.prop('indeterminate', false)
		    self.element.prop('checked', state)
		}	
	    })
	    
	}
    }
)

$.widget(
    'raiwidgets.selectshownrows',
    {
	_create : function(){
	    var wn = 'select-shown-rows',
		self = this
	    
	    this.id = this.element.data(wn+'-id')
	    this.$table = this.element.parents('table').first()
	    this.choices = []
	    
	    this.$elements = this.$table.find('tbody [data-'+wn+'-id="'+this.id+'"]').each(
		function(){
		    var txt = $(this).text(),
			idx = self.choices.indexOf(txt)
		    
		    $(this).attr('data-'+wn+'-value', txt)
		    if (idx == -1)
			self.choices.push(txt)
		}
		
	    )

	    this.$dropdown = $('<div class="btn-group" />')
	    this.$btn = $('<button type="button" class="btn pl-0">'+this.element.text()+'</button>')
		.attr('data-toggle', 'dropdown')
		.attr('aria-haspopup', true)
		.attr('aria-expanded', false)
		.addClass('dropdown-toggle')
		.appendTo(this.$dropdown)
	    this.$ddMenu = $('<div class="dropdown-menu" />').appendTo(this.$dropdown)
	    $('<h6 class="dropdown-header">Angezeigte Elemente</h6>').appendTo(this.$ddMenu)
	    this.$form = $('<form class="py-1 px-2"/>').appendTo(this.$ddMenu)

	    var $wrapper, $label, $input, c
	    
	    for (c=0; c < this.choices.length; c++){
		
		$wrapper = $('<div class="custom-control custom-checkbox mb-1">').appendTo(this.$form)
		$input = $('<input type="checkbox" class="custom-control-input" />')
		    .attr('id', wn+'_'+this.uuid+'_'+c)
		    .attr('value', this.choices[c])
		    .prop('checked', true)
		    .appendTo($wrapper)
		    .change(
			function(evt){
			    evt.preventDefault()
			    var $elems = self.$elements.filter('[data-'+wn+'-value="'+$(this).val()+'"]')
			    if ($(this).prop('checked')){
				$elems.each(function(){
				    $(this).parents('tr').first().show(
					200,
					function(){self._adjustBgColor()}
				    )
				})
			    } else {
				$elems.each(function(){
				    $(this).parents('tr').first().hide(
					200,
					function(){self._adjustBgColor()}
				    )
				})
			    }
			    
			}
		    )
		$label = $('<label class="custom-control-label">'+this.choices[c]+'</label>')
		    .attr('for', wn+'_'+this.uuid+'_'+c)
		    .css({'font-size':'.875rem','text-transform':'none'})
		    .appendTo($wrapper)
	    }
	    this.element.html('')
	    this.element.append(this.$dropdown)
	    this.$btn.css(
		this.element.css([
		    'font-size', 'font-weight', 'text-transform', 'color',
		    'font-color'
		])
	    )
	},
	_adjustBgColor : function(){
	    var c = 0
	    this.$elements.each(
		function(){
		    var $tr = $(this).parents('tr').first()
		    if ($tr.is(':visible')){
			if (c%2==0){
			    $tr.css('background-color', '#fff')
			} else {
			    $tr.css('background-color', '#f2f2f2')
			}
			
			c++;
		    }
		}
	    )
	}
    }
)


/**
 *  A collection of functionalities used for the attendee-list-view of Courses. 
 *  Might not be very re-usable.
 */
$.widget(
    'raiwidgets.attendeelist',
    {
	_create : function(){
	    // called on the table
	    this.$tbody = this.element.find('tbody').first()
	    this.$thead = this.element.find('thead').first()
	    this.$rows = this.$tbody.find('tr')
	    this.$menu = this.$thead.find('.checkbox-menu').first()
	    this.$invisContainer = $('<div />').css({
		position: 'absolute',
		left : '-10000px',
		top : '-10000px',
		width : '1px',
		height : '1px'
	    }).insertBefore(this.element)

	    var self = this
	    this.$menu.find('button[data-action="post_form"]').each(
		function(){
		    var $btn = $(this)
		    $btn.click(function(){self._postForm($btn)})
		}
	    )
	    this.$tbody.find('input.row-check').each(
		function(){
		    $(this).change(function(){
			if ($(this).prop('checked')){
			    $(this).parents('tr').first().attr('data-checked', true)
			} else {
			    $(this).parents('tr').first().attr('data-checked', false)
			}
		    })
		    if ($(this).prop('checked')){
			$(this).parents('tr').first().attr('data-checked', true)
		    } else {
			$(this).parents('tr').first().attr('data-checked', false)
		    }
		}
	    )
	},
	_postForm : function($elem){
	    var $rows = this._getCheckedRows()
	    // clean up old content from invis container

	    this.$invisContainer.children().remove()
	    
	    if ($rows.length == 0){
		$R.infoDialog(
		    'Bitte Einträge auswählen',
		    $('<div><strong>Es sind keine Einträge ausgewählt.</strong><p>Bitte nutze die Kästchen auf der Seite der Tabelle um Einträge auszuwählen.</p></div>')
		)
		return
	    }
	    var fieldValues = JSON.parse($elem.data('field-values').replace(/'/g,'"')),
		formFieldNames = JSON.parse($elem.data('form-field-names').replace(/'/g,'"')),
		$form = $('<form method="POST" />')
		.appendTo(this.$invisContainer)
	    if ($elem.data('add-next') == true){

		var $path = $elem.data('add-next-value') ? $elem.data('add-next-value') : window.location.pathname
		$form.attr('action', $elem.data('form-url')+encodeURI('?next='+$path))
	    } else {
		$form.attr('action', $elem.data('form-url'))
	    }
	    
	    $rows.each(
		function(){
		    for (var c = 0; c < fieldValues.length; c++){
			var $row = $(this),
			    value = $row.find('[data-field-name="'+fieldValues[c]+'"]').first().data('field-value'),
			    $input = $('<input type="checkbox" checked />')
			    .attr('name', formFieldNames[c])
			    .val(value)
			    .appendTo($form)
			
		    }
		}
	    )
	    $('<input type="hidden" name="csrfmiddlewaretoken" value="'+$R.getCookie('csrftoken')+'" />').appendTo($form)
	    $($elem.find('.additional-form-data').first().html()).appendTo($form)
	    $form.attr('enctype','multipart/form-data')
	    $form.submit()
	},
	_getCheckedRows : function(){
	    // we cannot simply look for [data-checked=true ] since the checked status of the
	    // input might have been set via JS, which does not trigger the click function.
	    
	    this.$rows.filter(':visible').each(
		function(){
		    var $input = $(this).find('input.row-check').first()
		    $(this).attr('data-checked', $input.prop('checked'))
		}
	    )

	    return this.$rows.filter(':visible').filter('[data-checked="true"]')
	}
    }
)
$.widget(
    'raiwidgets.nuclideselect',
    {
	_create : function(){
	    this.addNuclideOption = $('<option value="+">Nuklid hinzufügen...</option>').appendTo(this.element)
	    var self = this
	    this.element.change(
		function(){
		    if ($(this).val() == '+'){
			self._showNuclideModal()
		    }
		}
	    )
	    // this.$modal = $('#genericModal')
	    // this.$modalHeader = this.$modal.find('.modal-header').first()
	    // this.$modalBody = this.$modal.find('.modal-body').first()
	    this.addURL = this.element.data('add-nuclide-url')
	    // this.$saveBtn = $('#btnSavegenericModal')
	    
	},
	_showNuclideModal : function(){
	    var self = this
	    this.$modal = $R.genericModal(
		{
		    title :          'Nuklid hinzufügen',
		    cancelBtn :      true,
		    saveBtn :        true,
		    applyBtn :       false,
		    saveLabel :      'Speichern',
		    cancelLabel :    'Abbrechen',
		    saveCallback :   function(){ self._saveNuclide() },
		    cancelCallback : function(){
			var $emptyOpt = self.element.find('option[value=""]'),
			    $firstOpt = self.element.find('option').first()
			if ($emptyOpt.length > 0){
			    $emptyOpt.prop('selected', true)
			} else {
			    $firstOpt.prop('selected', true)
			}
			
		    }
		}
	    )
	    $R.get(this.addURL).fail(

	    ).done(
		function(data){
		    self.$modal.setBody('<form id="newNuclideForm">'+data['html']+'</form>')
		    self.$modal.show()
		}
	    )

	},
	_saveNuclide : function(){
	    var self = this
	    $R.post(
		this.addURL,
		{
		    data : $('#newNuclideForm').serialize()
		}
	    ).done(
		function(data){
		    console.log(data)
		    if (data['errors'] == true){
			self.$modal.setBody('<form id="newNuclideForm">'+data['html']+'</form>')
		    } else {
			$('.nuclide-select').each(
			    function(){
				var $addOpt = $(this).find('option[value="+"]').first() 
				$('<option />').text(data['nuclide']).val(data['pk']).insertBefore($addOpt)
			    }
			)
			self.element.find('option[value="'+data['pk']+'"]').prop('selected', true)
			self.$modal.dismiss()
			
		    }
		    
		}
	    )
	}
    }
)
$(document).on('rubiontail.baseloaded', function(){
    setLoadStatus('aktiviere Widgets', function(){$R.Widgets.init()})
})

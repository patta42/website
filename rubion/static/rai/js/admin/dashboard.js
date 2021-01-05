"use strict";

$.widget(
    'raiwidgets.panelgridpanel',
    /* 
       A panel within the panel grid
     */
    {
	_create : function(){

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
		this.options['width'] = this.element.data('grid-width')
	    if (this.element.data('grid-height') !== undefined)
		this.options['height'] = this.element.data('grid-height')
	    this.$menu = this.element.find('.panel-menu').first()
	    
	    this._insertControls();
	},
	_insertControls : function(){
	    var $dropdown = $('<div />')
		.addClass('dropdown-menu')
		.attr('aria-labelled-by', 'btn_dd_'+this.uuid);

	    // size sub-menu-header
	    var $szHeader = $('<h6>Größe ändern</h6>')
		.addClass('dropdown-header')
		.appendTo($dropdown);

	    var self = this;
	    for (var rs = this.options['minRows']; rs <= this.options['maxRows']; rs++){
		for (var cs = this.options['minCols']; cs <= this.options['maxCols']; cs++){
		    $btn = $('<button>'+rs+'×'+cs+'</button>')
			.appendTo($dropdown)
			.attr('type','button')
			.data('grid-height', rs)
			.data('grid-width', cs)
			.addClass('dropdown-item size-btn');
		    if (
			this.options['width'] == cs
			    && this.options['height'] == rs
		    ){
			$btn.addClass('disabled')
			    .attr('aria-disabled', true)
			    .attr('tabindex',-1);
		    } 
		    $btn.click(function(evt){
			evt.preventDefault()
			$dropdown.find('.disabled.size-btn').removeClass('disabled');
			$(this).addClass('disabled');
			self._changeSize($(this).data('grid-height'), $(this).data('grid-width'))
		    });
		    
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
		.appendTo($iconContainer);
	    var $posMenu = this._getPositioningMenu();
	    for (let i in $posMenu){
		$dropdown.append($posMenu[i]);
	    }
	    var $closeBtn = $('<button type="button"><i class="fas fa-times"></i></button>')
		.addClass('btn btn-xs ml-2')
		.click(function(evt){self._close(evt)});
	    this.$menu.append($menuBtn)
	    this.$menu.append($dropdown)
	    this.$menu.append($closeBtn)
	},
	_getPositioningMenu : function(){
	    var self = this;
	    return [
		$('<h6>Position ändern</h6>')
		    .addClass('dropdown-header'),
		$('<button>nach links</button>')
		    .addClass('move-to-left-btn')
		    .attr('type','button')
		    .addClass('dropdown-item')
		    .click(function(){self._moveLeft()}),
		$('<button>nach rechts</button>')
		    .attr('type','button')
		    .addClass('dropdown-item')
		    .addClass('move-to-right-btn')
		    .click(function(){self._moveRight()})
	    ]
	},
	_changeSize : function(h, w){
	    this.element
		.attr('data-grid-height', h)
		.attr('data-grid-width', w)
	    this.options['width'] = w;
	    this.options['height'] = h;
	    this.element.css('float','left');
	    this._trigger('sizeChanged');
	},
	_moveLeft : function(evt){
	    if (this.options['position'] > 0){
		this._move(-1, evt);
	    }
	},
	_moveRight : function(evt) {
	    this._move(+1, evt);
	},
	_move : function(direction, evt){
	    this.element.css('float','left');
	    var oldPos = parseInt(this.options['position'])
	    this._trigger('positionChanged', evt, {direction : direction, pos : oldPos}); 
	},
	_close : function(evt){
	    this.element.hide()
	    this._trigger('panelClosed', evt, {
		panelId : this.getIdentifier(),
		position : this.options['position']
	    });
	},
	floatCheck : function(){
	    if (this.options['height' ] == 1){
		this.element.css('float', 'left');
		return
	    }
	    var width = 2*this.element.parents('.panel-grid-wrapper').first().width()/3;
	    if (this.element.position().left + this.element.outerWidth() >= width){
		this.element.css('float', 'right');
	    } else {
		this.element.css('float', 'left');
	    }
	},
	getIdentifier : function(){
	    return this.element.data('panel-identifier')
	}
    }
)

$.raiwidgets.panelgridpanel.prototype.options = {
    width : 1,
    height : 1,
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
    'raiwidgets.panelgridaddpanel',
    /* 
       The "add-panel"-panel
     */
    $.raiwidgets.panelgridpanel,
    {
	_create : function(){
	    this._super();
	    var self = this;
	    this.element.find('input[type=checkbox]').change(
		function (evt){
		    self._trigger('panelAdded', evt, {
			panelKey : $(this).attr('name')
		    })
		}
	    )
	    this.$emptyMessage = $('<li>Keine weiteren Panels vorhanden</li>')
		.addClass('list-group-item')
		.appendTo(this.element.find('ul.add-panel-panel').first())
		.hide()

	},
	_getPositioningMenu : function(){
	    // no positioning menu
	    return [];
	},
	_checkEmpty : function(){
	    if (this.element.find('input:visible').length == 0){
		this.$emptyMessage.show();
	    } else {
		this.$emptyMessage.hide();
	    }
	},
	panelShown : function(id){
	    this.element.find('input[name="'+id+'"]').parents('li').first().hide();
	    this._checkEmpty()
	},
	panelHidden : function(id){
	    this.element.find('input[name="'+id+'"]').parents('li').first().show().prop('checked', false);
	    this._checkEmpty()
	}
    }
)
$.widget(
    'raiwidgets.panelgrid',
    /* 
       Functionality of the panel grid on the dashboard of RUBIONtail.
     */
    {
	_create : function(){
	    this.$children = [];
	    this.options['addPanelURL'] = this.element.data('add-panel-url')
	    this.options['changeSettingsURL'] = this.element.data('change-psettings-url')
	    this.options['removePanelURL'] = this.element.data('remove-panel-url')

	    this.options['childOptions'] = {
		positionChanged : function(elem, evt, data){
		    self.onPositionChanged(elem, evt, data)
		},
		sizeChanged : function(evt){
		    self.onSizeChanged(evt)
		},
		panelClosed : function(evt, data){
		    self.onPanelClose(evt, data)
		}
		
	    }
	    var self = this;
	    
	    this.element.find(this.options['childSelector']).each(
		function(){
		    // initialize panelgridpanel widget and
		    // append child to array of children
		    if ($(this).data('panel-identifier') == 'rai.emptypanel'){
			self.$addPanel = $(this).panelgridaddpanel({
			    panelAdded : function(evt, data){
				self.onPanelAdded(evt, data)
			    }
			})
		    } else {
			self.$children.push(
			    $(this).panelgridpanel(self.options['childOptions'])
			)
		    }
		}
	    )
	    for (let i in this.$children){
		this.$addPanel.panelgridaddpanel(
		    'panelShown', this.$children[i].panelgridpanel('getIdentifier')
		)
	    }
	    this._sortChildren();
	    
	},
	_sortChildren : function(){
	    this.$children.sort(function(a,b){
		return a.panelgridpanel('option','position') > b.panelgridpanel('option','position')
	    })
	    this._reposition()
	},
	_reposition : function(){
	    for (let i in this.$children){
		console.log(this.$children[i].panelgridpanel)
		this.$children[i].panelgridpanel('option','position', i);
		this.element.append(this.$children[i]);
	    }
	    // put add panel at the end
	    this.$addPanel.appendTo(this.element);
	    // put clearfix at the very end
	    
	    this.element.find('.clearfix').appendTo(this.element);
	    for (let i in this.$children){
		this.$children[i].panelgridpanel('floatCheck');
	    }
	},
	onPanelClose : function(evt, data){
	    console.log(data)
	    var $elem  = this.$children.splice(data['position'], 1)[0],
		panelId = data['panelId'];
	    $elem.panelgridpanel('destroy')
	    $elem.remove();
	    this._reposition()
	    var self = this;
	    $R.post(this.options['removePanelURL'], {
		data : {
		    panelId : panelId
		}
	    }).done(function(){
		$R.message('success', 'Änderung gespeichert.')
		self.$addPanel.panelgridaddpanel('panelHidden', panelId)
	    })
	},
	onSizeChanged : function(evt){
	    for (let i in this.$children){
		this.$children[i].panelgridpanel('floatCheck');
	    }

	    var data = {
		'width' : $(evt.target).panelgridpanel('option','width'),
		'height' : $(evt.target).panelgridpanel('option','height'),
		'position' : $(evt.target).panelgridpanel('option','position'),
		'panelId' : $(evt.target).data('panel-identifier')
	    }
	    $R.post(this.options['changeSettingsURL'], {data:data}).done(
		$R.message('success', 'Größenänderung gespeichert.')
	    )
	},
	onPositionChanged : function(evt, data){
	    var pos = data['pos'];
	    var target = pos + data['direction'];
	    if (target < this.$children.length && target >= 0){
		this.$children = $R.swap(this.$children, pos, target);
	    }
	    this._reposition()
	    var d = { data : JSON.stringify([
		{
		    width : this.$children[target].panelgridpanel('option','width'),
		    height : this.$children[target].panelgridpanel('option','height'),
		    position : this.$children[target].panelgridpanel('option','position'),
		    panelId : this.$children[target].data('panel-identifier')
		},
		{
		    width : this.$children[pos].panelgridpanel('option','width'),
		    height : this.$children[pos].panelgridpanel('option','height'),
		    position : this.$children[pos].panelgridpanel('option','position'),
		    panelId : this.$children[pos].data('panel-identifier')
		}
	    ])};
	    
//	    $R.post(this.options['changeSettingsURL'], {data:data1}).done(
	    $R.post(this.options['changeSettingsURL'], {data:d}).done(
		$R.message('success', 'Positionsänderung gespeichert.')
	    )
//	    )

	},
	onPanelAdded : function(evt, data){
	    var self = this;
	    console.log(evt, data)
	    $R.post(this.options['addPanelURL'], {
		data : {
		    panelId : data['panelKey'],
		    position : self.$children.length,
		}
	    }).done(
		function(d){
		    if (d['status'] == 200){
			self.$children.push($(d['html']).panelgridpanel(
			    self.options['childOptions']
			).insertBefore(self.$addPanel));
			self.$children[self.$children.length-1].panelgridpanel('option','position', self.$children.length-1);
		    }
		    if (d['status'] == 403){
			$R.message('danger', d['message'], 0)
		    }
		    self.$addPanel.panelgridaddpanel('panelShown', d['panelId'])

		}
	    )
	    
	}
    }
)

$.raiwidgets.panelgrid.prototype.options = {
    childSelector : '.grid-panel'
}

$(document).on(
    'rubiontail.baseloaded',
    function(){
	$('.panel-grid-wrapper').panelgrid()
    }
)

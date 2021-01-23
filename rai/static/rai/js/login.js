$R = {}
$R.darken = function(r,g,b, frac){
    let rf = 1 - frac;
    return 'rgb('+Math.round(r*rf)+','+Math.round(g*rf)+','+Math.round(b*rf)+')';
}

$.widget(
    'raiwidgets.niceselect',
    {
	_options : {
	    buttonCommonCss : {
		display : 'block',
		width : '100%',
		textAlign : 'left',
		borderLeftColor : 'transparent',
		borderRightColor : 'transparent',
		borderBottomColor : 'transparent',
		borderTopColor : 'transparent',
		
	    }
	},
	_create : function(){
	    var self = this;
	    this.$openButton = $('<button type="button">'+this.getSelected().text()+'</button>');
	    this._options.buttonSharedCss = this.element.css([
		'backgroundColor',
		'paddingLeft', 'paddingRight','paddingTop',
		'paddingBottom','fontSize', 'marginLeft', 'marginRight','marginTop',
		'marginBottom','color',
		'borderLeftStyle', 'borderLeftWidth',
		'borderLeftColor','borderRighttStyle', 'borderRightWidth',
		'borderRightColor','borderTopStyle', 'borderTopWidth',
		'borderTopColor','borderBottomStyle', 'borderBottomWidth',
		'borderBottomColor'
	    ])
	    this.$openButton
		.css({
		    display: 'inline-block',
		    width: '100%',
		    textAlign : 'left'
		})
		.css(this._options.buttonSharedCss)
		.css(this.element.css([
		    'backgroundImage', 'backgroundRepeat',
		    'backgroundPosition',
		]))
		.insertBefore(this.element)
		.click(function(){self._toggleList()});
	    this.$invisContainer = $('<div>')
		.css({
		    position : 'absolute',
		    width : '0px',
		    height : '0px',
		    top : '-200wh',
		    left: '-200vw'
		})
		.appendTo(this.element.parents('form').first())
		.append(this.element)
	    this.$selection = $('<div>')
		.insertAfter(this.$openButton)
		.css({
		    position : 'relative',
		    height : '0px',
		    overflowY : 'visible',
		})
		.hide()
	    this._makeSelectionList()
	    
	},
	getSelected : function(){
	    return this.element.find('option:selected')
	},
	_makeSelectionList : function(){
	    var self = this;
	    this.element.find('option').each(
		function(){
		    var $btn = $('<button type="button"></button>')
			.css(self._options.buttonSharedCss)
			.css(self._options.buttonCommonCss)
			.text($(this).text())
			.data('value', $(this).val())
			.hover(
			    function(){
				$(this).css('backgroundColor', 'green')
			    },
			    function(){
				$(this).css('backgroundColor', self._options.buttonSharedCss.backgroundColor)
			    },
			)
			.appendTo(self.$selection)
			.click(function(evt){self._select(evt)})
		}
	    )
	},
	_toggleList : function(action){
	    if (action === undefined){
		action = this.$selection.is(':visible') ? 'close' : 'open'; 
	    }
	    var self = this;
	    if (action == 'close'){
		this.$openButton.css(
		    'backgroundColor', 'rgb(23, 54, 92)'
		)
		this.$selection.hide()
	    } else {
		this.$openButton.css(
		    'backgroundColor', $R.darken(23, 54, 92, .25)
		)
		this.$selection.show()
	    }
	},
	_select : function(evt){
	    this.element.find('option[value="'+$(evt.target).data('value')+'"]').first()
		.prop('selected', true)
	    this.$openButton.text($(evt.target).text())
	    this._toggleList('close')
	}
    }

)

$(document).ready(function(){
    $('select').niceselect()
})


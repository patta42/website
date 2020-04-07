$R.Widgets = {
    init : function(){
	// activate all widgets
	$('.type-and-select').each(function(){
	    new $R.Widgets.TypeAndSelect($(this));
	})
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
}

$(document).ready(function(){
    $R.Widgets.init()
})

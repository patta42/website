'use strict';

$.widget('raiwidgets.beamtimepanel', {
    monthnames : ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    daynames : ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'],
    options : {
	date : new Date(),
	display : 'w'
    },
    _create : function(){
	var sDate = $(this.element).data('beamtimepanel-date')
	if (sDate !== undefined){
	    var splitted = sDate.split('-');
	    this.options.date = new Date(splitted[0], parseInt(splitted[1], 10)-1, splitted[2]);
	}
	var oDisplayDuration = $(this.element).data('beamtimepanel-display');
	if (oDisplayDuration === "w" || oDisplayDuration === "d"){
	    this.options.display = oDisplayDuration;
	}
	this.currentDate = this.options.date;
	var oFetchURL = $('[data-beamtime-fetch-url]').first().data('beamtime-fetch-url');
	if (oFetchURL !== undefined){
	    this.options.fetchURL = oFetchURL;
	}
	this.$list = this.element.find('ul.beamtime-list');
	this.fetchURL = this.options.fetchURL;
	this._updateHTML();
	this.show();
    },
    _fetch : function( cb ){
	// cb is the callback called when .done() is is called
	$R.get(this.fetchURL,
	       {
		   data: {
		       'year' : this.currentDate.getFullYear(),
		       'month' : this.currentDate.getMonth()+1,
		       'day' : this.currentDate.getDate()
		   }
	       }
	      ).done(
	    function(data){cb(data);}
	)
    },
    _updateHTML : function(){
	// inserts the navigation
	var $head = this.element.find('h5.card-title').first();
	var self = this;
	var $prev = $('<button class="btn btn-secondary btn-sm mr-2" type="button"><i class="fas fa-angle-left"></i></button>')
	    .click(function(){
		self.show(-1);
	    });
	var $next = $('<button class="btn btn-secondary btn-sm ml-2" type="button"><i class="fas fa-angle-right"></i></button>')
	    .click(function(){
		self.show(+1);
	    });

	// enclose content of head in a <span>
	var content = $head.text();
	$head.text('');
	this.$dateDisplay = $('<span />').text(content).appendTo($head);
	$head.append($next).prepend($prev);
	var $body = this.element.find('.card-body').first().css('position', 'relative');
	this.$loading = $('<div />').css({
	    position : 'absolute',
	    left : 0,
	    top : 0,
	    width : '100%',
	    height : '100%',
	    backgroundColor : 'var(--gray50)',
	    display: 'none',
	    color: '#fff',
	    textAlign : 'center',
	    zIndex : 100
	}).prependTo($body);
	var $inner = $('<div><i class="fas fa-circle-notch fa-spin fa-8x"></i></div>').css({
	    display: 'flex',
	    justifyContent: 'center',
	    alignItems: 'center',
	    height: '100%',
	}).appendTo(this.$loading)
	    
    },
    show : function(off){
	if (off !== undefined){
	    this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), this.currentDate.getDate() + off);
	}
	this.$dateDisplay.text(
	    this.daynames[this.currentDate.getDay()] + ', ' +
		this.currentDate.getDate() + '. ' +
		this.monthnames[this.currentDate.getMonth()] + ' ' +
		this.currentDate.getFullYear()
	);
	this.$loading.show();
	this.$list.find('[data-toggle="popover"]').popover('dispose')
	var self = this;
	this._fetch(function(data){self.display(data)});
    },
    display : function(data){
	if (data.status == 200){
	    this.$list.html(data.html);
	    this.$list.find('[data-toggle="popover"]').popover({
		container: 'body',
		placement: 'top'
	    }).css({cursor : 'help'})
	    this.$loading.hide();
	    
	}
    }
});

$(document).on('rubiontail.baseloaded', function(){
    $('[data-panel-identifier="website.beamtime.cal"]').beamtimepanel()
})


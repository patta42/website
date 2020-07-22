

$R = {
    urlParam : function(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results==null) {
	    return null;
	}
	return decodeURI(results[1]) || 0;
    }
};

['Arguments', 'Function', 'String', 'Number', 'Date', 'RegExp'].forEach( 
    function(name) { 
        $R['is' + name] = function(obj) {
              return toString.call(obj) == '[object ' + name + ']';
    }; 
});

$R.generic = {
    Modal : (function(elem){
	
	var cls = function(elem){
	    var self = this;
	    
	    self.id = $(elem).attr('id');
	    self.$applyBtn = $('#btnApply' + self.id);
	    self.$saveBtn = $('#btnSave' + self.id);
	    self.$form = $(elem).find('form').first();
	    self.action = self.$form.attr('action');
	    self.save = function( hdl ){
		self.$saveBtn.click( function(){hdl(this, self.$form, self.action)} );
	    }
	    self.apply = function( hdl ){
		self.$applyBtn.click( function(){hdl(this, self.$form, self.action)} );
	    }
	    
	}
	return cls;
    })(),
    ModalFormHandling : (function(){
	
	var cls = function(){
	    var self = this;
	    self.modals = [];
	    $('.modal').each(function(){
		if ($(this).find('form').length == 0){
		    return
		}
		var modal = new $R.generic.Modal(this);
		modal.apply(function(btn, $form, action){
		    $form.find('input[name="csrfmiddlewaretoken"]').remove();
		    $form.attr('method', 'get');
		    $form.submit();
		});
		modal.save(function(btn, $form, action){
		    $form.attr('method', 'post');
		    $form.submit();
		});
		self.modals.push(modal);  
	    });
	}
	return cls;
    })()

};
$R.getCookie = function(name){
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Some shorthands for Ajax

$R._add_csrf = function(opts){
    if (opts.headers === undefined)
	opts.headers = {'X-CSRFToken' : $R.getCookie('csrftoken')}
    else {
	if (opts.headers['X-CSRFToken'] === undefined){
	    opts.headers['X-CSRFToken'] = $R.getCookie('csrftoken');
	}
    }
    return opts
}
$R.post = function(url, opts){
    if (opts === undefined){
	opts = {};
    }
    opts = $R._add_csrf(opts);
    opts.method = 'POST';
    opts.url = url;
    return $.ajax(opts)
}
$R.get = function(url, opts){
    if (opts === undefined){
	opts = {};
    }
    opts = $R._add_csrf(opts);
    opts.method = 'GET';
    opts.url = url;
    return $.ajax(opts)
}

$R.help = {
    instance : undefined,
    Message : ( function() {
	var cls = function(type, msg){
	    var self = this;
	    self.alertContainer = $('#alertContainer');
	    var msgBox = $(
		'<div class="alert alert-'+type+' role="alert">\n'
		    +msg+'\n'+
		    '  <button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
		    '    <span aria-hidden="true"><i class="fas fa-times"></i></span>\n'+
		    '  </button>\n'+
		    '</div>'
	    )
	    self.throwMsg = function(){
		self.alertContainer.append(msgBox);
	    }
	}
	return cls;
    })(),
    ErrorMessage : (function(){
	var msg = function(msg){
	    return new $R.help.Message('danger', msg);
	}
	return msg;
    })(),
    SuccessMessage : (function(){
	var msg = function(msg){
	    return new $R.help.Message('success', msg);
	}
	return msg;
    })(),
    
    HelpSystem : ( function () {
    	var cls = function(){
    	    var self = this;
	    var help_protocol = 'help::';
    	    var candidates = $('* [data-rai-help-uri]');
    	    if (candidates.length == 0){
    		console.error('The help system will not work here. No element with a data-rai-help-uri property in the DOM tree.');
    	    } else {
		self.help_uri = candidates.first().data('rai-help-uri');
	    }
	    $$ = (id) => ($('#'+id))
	    self.idContent = 'helpContent';
	    self.idEditor = 'helpEditor';

	    $C = (id) => ($$(self.idContent+id));
	    $E = (id) => ($$(self.idEditor+id));

	    self.modal = $$('helpModal');
	    self.$cComponents = {
		breadcrumb : $C('Container ol.breadcrumb').first(),
		editBtn : $C('EditBtn'),
		content : $C(''),
		container : $C('Container')
	    }
	    self.$eComponents = {
		editor : $E(''),
		textarea : $E(' textarea').first(),
		cancelBtn: $E('Cancel'),
		saveBtn: $E('Save'),
		prependPath: $E('TitlePrepend'),
		title: $E('Title')
	    }

	    $('a[href^="'+help_protocol+'"]').each( function (){
		var $link = $(this);
		$link.click( function (evt) {
		    evt.preventDefault();
		    self.showHelp(evt);
		    
		})
	    })

	    // hide editor
	    self.$eComponents.editor.hide();
	    
	    self.showHelp = function(evt){
		var help_path = $(evt.currentTarget).attr('href').slice(help_protocol.length);
		self.$eComponents.editor.data('help-path', help_path);
		$R.get(self.help_uri + help_path)
		    .done( function(data, textStatus, jqxhr){
			// we might get a 204 with not_found = True in the data.
			// This should be a 404, but that might be captured and
			// redirected from the locale middleware. Thus this workaround.
			if (jqxhr.status == 200){
			    if (data.not_found === true || data.is_empty === true){
				self.showCreatePage(data);
			    } else {
				self.showContent(data);
			    }
			}
			
		    })
		    .fail( function(jqxhr, textStatus, error) {
			console.log(jqxhr);
			console.log(textStatus);
			console.log(error);
			
			if (jqxhr.status == 404){
			    // in case of a 404, show a "why not create this page" hint
			    self.showCreatePage(
				jqxhr.responseJSON
			    )
			} else {
			    // in all other cases, report the error
			    $R.help.ErrorMessage(
				'<strong>Ein Fehler ist aufgetreten.</strong>'+
				    'Der Fehlercode war ' +
				    jqxhr.statusText +
				    ' (' +jqxhr.status+ ')')
				.throwMsg();
			
			}
		    })
	    }

	    self.showCreatePage = function(params){
		params['content_html'] = 
		    '<div class="alert alert-warning" role="alert">' +
		    '<h4 class="alert-heading">Schade!</h4>' +
		    '<p>Leider existiert zu diesem Thema noch keine Hilfeseite. Es wäre toll, wenn wir alle zusammen nach und nach die Hilfe füllen würden. Wenn du also ein wenig Hilfe zu diesem Thema leisten kannst, erstelle doch einfach diese Hilfeseite.</p>'+
		    '<p>Es ist nicht schlimm, wenn die Hilfe nur kurz ist oder nicht ganz richtig. Hilfeseiten könne jederzeit abgeändert werden.</p>'+
		    '<hr>'+
		    '<p class="mb-0 text-larger">Ja, ich möchte <a href="#" id="createPageLink" class="alert-link">diese Hilfeseite erstellen</a>!'+
		    '</p>'+
		    '</div>'
		self.showContent(params, true, function(){
		    $$('createPageLink').click(function(){
			self.showEditor();
		    })
		})
		
	    }
	    
	    self.showContent = function(content, show = true, callback = undefined){
		// show the content
		self.$cComponents.content.html(content.content_html);
		console.log(self.$eComponents.editor)
		self.$eComponents.textarea.val(content.content_markdown);
		if (content.editable === true){
		    self.$cComponents.editBtn.click(
			function(){
			    self.showEditor();
			}
		    ).show();
		    self.$eComponents.saveBtn.click(
			function(){
			    self.save();
			}
		    )
		    
		} else {
		    self.$cComponents.editBtn.off('click').hide();
		}
		self.$cComponents.breadcrumb.html('') // clear breadcrumb
		self.$eComponents.prependPath.html('') // clear path prepend 
		var li, link, path = '', key;

		// Link to root
		li = $('<li class="breadcrumb-item"></li>');
		link = $('<a href="help::' + path + '">Hilfe</a>').
		    click( function (evt) {
			evt.preventDefault();
			self.showHelp(evt);
			
		    })
		self.$eComponents.prependPath.text('Hilfe/');
		self.$cComponents.breadcrumb.append(li.append(link))
		
		for (var count = 0; count < content.breadcrumb.length; count++){
		    // we do not expect obejcts with multiple keys here
		    key = Object.keys(content.breadcrumb[count])[0];
		    path += key
		    li = $('<li class="breadcrumb-item"></li>');
		    link = $('<a href="help::' + path + '">'+content.breadcrumb[count][key]+'</a>').
			click( function (evt) {
			    evt.preventDefault();
			    self.showHelp(evt);
			    
			})
		    self.$cComponents.breadcrumb.append(li.append(link));
		    self.$eComponents.prependPath.text(
			self.$eComponents.prependPath.text()+content.breadcrumb[count][key]+'/'
		    )
		    path = path + ':'
		}
		li = $(
		    '<li class="breadcrumb-item active" aria-current="page">'+
			content.title +
			'</li>'
		);
		self.$cComponents.breadcrumb.append(li)
		
		if (show){
		    self.showContentContainer(callback);
		}
		
	    }
	    self.toggle = function(hide, show, callback = undefined){
		var height = self.modal.height();
		self.modal.css('height', height);
		hide.slideUp(300, function(){
		    if (callback === undefined){
			show.slideDown(300);
		    } else {
		console.log(callback)
			show.slideDown(300, function(){ callback() });
		    }
		})
	    }
	    self.showEditor = function(callback = undefined){
		self.toggle(self.$cComponents.container, self.$eComponents.editor, callback)
	    }
	    self.showContentContainer = function(callback = undefined){
		self.toggle(self.$eComponents.editor, self.$cComponents.container, callback)
	    }

	    self.save = function(){
		var E = self.$eComponents;
		var data = {
		    content: E.textarea.val(),
		    title: E.title.val(),
		    identifier: E.editor.data('help-path')
		}
		$R.post(
		    self.help_uri + E.editor.data('help-path') +'/',
		    { data : data }
		).done(
		    function(data, textStatus, jqxhr){
			self.modal.modal('hide');
			if (data.msg !== undefined){
			    $R.help.SuccessMessage(data.msg).throwMsg();
			}
		    }
		    
		).fail(
		    function(jqxhr, textStatus, error){
			console.log(jqxhr);
			console.log(textStatus);
			console.log(error);
		    }
		)
	    }
	    
	    self.$eComponents.cancelBtn.click(
		function(){
		    self.showContentContainer();
		}
	    )
    	}
    	return cls;
    })()
}

$R.selectElementText= function(el, win) {
    var win = win || window;
    var doc = win.document, sel, range;
    if (win.getSelection && doc.createRange) {
        sel = win.getSelection();
        range = doc.createRange();
        range.selectNodeContents(el);
        sel.removeAllRanges();
        sel.addRange(range);
    } else if (doc.body.createTextRange) {
        range = doc.body.createTextRange();
        range.moveToElementText(el);
        range.select();
    }
}


// A generic function to show a dialog
$R.dialog = function(opts){
    var defaults = {
	title : 'Just a modal',
	titleIcon : 'fas fa-info-circle',
	titleFontColor : 'text-primary',
	content : 'Some foo with bar',
	saveButton : true,
	cancelButton : true,
	applyButton : true,
	canCancel : true,
	saveButtonLabel : 'Save',
	cancelButtonLabel : 'Cancel',
	applyButtonLabel : 'Apply',
	onCancel : null,
	onApply : null,
	onSave : null
    }

    var settings = $.extend({}, defaults, opts)
    var $dm = $('#dialogModal'),
	$title = $('#dialogModalTitle'),
	$header = $dm.find('.modal-header').first(),
	$body = $dm.find('.modal-body').first(),
	$footer = $dm.find('.modal-footer').first(),
	$applyBtn = $('#btnApplydialogModal'),
	$saveBtn =  $('#btnSavedialogModal'),
	$cancelBtn = $footer.find('button[data-dismiss="modal"]').first(),
	$closeBtn = $header.find('button[data-dismiss="modal"]').first()

    // destroy any previous modal instances

    if($dm.data('bs.modal') !== undefined){
	$dm.modal('dispose')
    }

    // build content

    var makeContent = function(setting, $parent){
	if (settings[setting] != null){
	    if ($R.isString(settings[setting])){
		$parent.append($('<span>'+settings[setting]+'</span>'))
	    } else {
		$parent.append(settings[setting])
	    }
	}
    }

    
    // Icon 
    
    if (settings['titleIcon'] != null){
	$title.append($('<span class="mr-2"><i class="'+settings['titleIcon']+'"></i></span>'))
    } else {
	$title.append(settings['titleIcon'])
    }
    

    // title
    makeContent('title', $title)
    makeContent('content', $body)
    makeContent('saveButtonLabel', $saveBtn.html(''))
    makeContent('cancelButtonLabel', $cancelBtn.html(''))
    makeContent('applyButtonLabel', $applyBtn.html(''))

    settings['saveButton'] ? $saveBtn.show() : $saveBtn.hide()
    settings['applyButton'] ? $applyBtn.show() : $applyBtn.hide()
    settings['cancelButton'] ? $cancelBtn.show() : $cancelBtn.hide()
    if (settings['canCancel'] === false){
	$cancelBtn.hide()
	$closeBtn.hide()
    }

    $saveBtn.click(
	function(){
	    $dm.modal('hide')
	    if (settings['onSave'] != null){
		settings['onSave']()
	    }
	}
    )
    $applyBtn.click(
	function(){
	    $dm.modal('hide')
	    if (settings['onApply'] != null){
		settings['onApply']()
	    }
	}
    )
    $cancelBtn.click(
	function(){
	    $dm.modal('hide')
	    if (settings['onCancel'] != null){
		settings['onCancel']()
	    }
	}
    )
    $closeBtn.click(
	function(){
	    $dm.modal('hide')
	    if (settings['onCancel'] != null){
		settings['onCancel']()
	    }
	}
    )
    if (settings['titleFontColor']){
	$title.removeClass('text-primary').addClass(settings['titleFontColor'])
    }
    
    $dm.modal()
}

$R.infoDialog = function(title, content){
    $R.dialog({
	canCancel : false,
	title : title,
	content : content,
	saveButton : false,
	applyButtonLabel : 'OK'
    })
}
$R.errorDialog = function(title, content){
    $R.dialog({
	canCancel : false,
	title : title,
	content : content,
	saveButton : false,
	applyButtonLabel : 'OK',
	titleFontColor : 'text-danger',
	titleIcon : 'fas fa-exclamation-triangle'
    })
}

$R.okCancelDialog = function(title, content, onOK, onCancel){
    $R.dialog({
	title:title,
	content:content,
	onApply: onOK,
	onCancel : onCancel,
	titleIcon: 'fas fa-question-circle',
	applyButtonLabel : 'OK',
	cancelButtonLabel : 'Abbrechen',
	saveButton: false
    })
}
$R.observeDOM = (function(){
  var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

  return function( obj, callback ){
    if( !obj || obj.nodeType !== 1 ) return; // validation

    if( MutationObserver ){
      // define a new observer
      var obs = new MutationObserver(function(mutations, observer){
          callback(mutations);
      })
      // have the observer observe foo for changes in children
      obs.observe( obj, { childList:true, subtree:true });
    }
    
    else if( window.addEventListener ){
      obj.addEventListener('DOMNodeInserted', callback, false);
      obj.addEventListener('DOMNodeRemoved', callback, false);
    }
  }
})();

$R._domInsertionCallbacks = [];

$R.addDomInsertionCallback = function(fnc){
    $R._domInsertionCallbacks.push(fnc)
}

$R.genericModal = function(opts){
    
    var defaults = {
	body :             '',
	title :            'Generic modal',
	saveBtn :          true,
	cancelBtn :        true,
	applyBtn :         true,
	saveLabel :        'Speichern',
	cancelLabel :      'Abbrechen',
	applyLabel :       'Anwenden',
	saveCallback :     null,
	applyCallback :    null,
	cancelCallback :   null,
	closeButton :      false,
	size :             ''
    }
    if (opts === undefined){
	var opts = {};
    }
    console.log(opts)
    var settings =    $.extend({}, defaults, opts),
	id =          'genericModal',
	$modal =      $('#genericModal'),
	$modalBody =  $modal.find('.modal-body').first(),
	$modalTitle = $modal.find('.modal-title').first(),
	btns = {
	    $cancelBtn :  $('#btnCancel'+id),
	    $saveBtn :    $('#btnSave'+id),
	    $applyBtn :   $('#btnApply'+id)
	}

    var api = {
	setBody : function(html){
	    $modalBody.html(html)
	},
	setTitle : function(html){
	    $modalTitle.html(html)
	},
	show : function(){
	    $modal.modal('show')
	
	},
	hide : function(){
	    $modal.modal('hide')
	},
	dismiss : function(){
	    $modal.on('hidden.bs.modal', function(){
		$modalTitle.html('')
		$modalBody.html('')
		btns['$saveBtn'].off('click')
		btns['$cancelBtn'].off('click')
		btns['$applyBtn'].off('click')
	    })
	    $modal.modal('hide')
	}
    }

    var init = function(){
	console.log(api,'init')
	// initialize modal
	if($modal.data('bs.modal') === undefined){
	    $modal.modal()
	}

	// fill with content
	api.setBody(settings['body'])
	api.setTitle(settings['title'])

	// init buttons
	//  -- unregister callbacks first 

	for (var btn of ['save', 'cancel', 'apply']){
	    var $btn = btns['$'+btn+'Btn']
	    $btn.off()
	    $btn.data('btn-type', btn)
	    if (settings[btn+'Btn']){
		$btn.show()
		$btn.html(settings[btn+'Label'])
		
		if (settings[btn+'Callback'] !== null){
		    $btn.click(settings[btn+'Callback'])
		}
	    } else {
		$btn.hide()
	    }
	    
	}
	

	
    }
    init()

    return api

}

$R.message = function(type, content, duration){
    if (duration === undefined){
	duration = 2000
    }
    var $container = $('#alertContainer'),
	$msg = $('<div class="alert">'+content+'</div>')
	.addClass('alert-'+type)
	.hide()
	.appendTo($container)
	.show(200)
    window.setTimeout(
	function(){
	    $msg.hide(200, function(){$msg.remove()}) 
	}
	, duration
    )
}
$(document).on(
    'rubiontail.baseloaded',
    function(){
	var bodyChanged = function(m){ 
	    var addedNodes = [], removedNodes = [];

	    m.forEach(record => record.addedNodes.length & addedNodes.push(...record.addedNodes))
	    for (var count = 0; count < $R._domInsertionCallbacks.length; count++){
		addedNodes.forEach( elem => $R._domInsertionCallbacks[count](elem))
	    }
	    //m.forEach(record => record.removedNodes.length & removedNodes.push(...record.removedNodes))
	    
//	    console.clear();
//	    console.log('Added:', addedNodes, 'Removed:', removedNodes);
	}
	var body = document.getElementById('body')
	$R.observeDOM(body, bodyChanged)
	window.setLoadStatus(
	    'Initiiere Hilfesystem', 
	    function(){
		$R.help.instance = new $R.help.HelpSystem();
	    }
	)
	window.setLoadStatus(
	    'Initiiere bearbeitbares Menu',
	    function(){
		$('.sidebar-sticky').sortable({
		    handle : '.sortable-grip',
		    items: '.rai-main-menu-container',
		    axis : 'y',
		    update : function(evt, ui){
	     		var count = 0, data = {}, group_order = [];
			var widget = ui.item.parents('.sidebar-sticky').first()
			var url = widget.data('admin-menu-settings-url')
	     		widget.find('.rai-main-menu-container').each(function(){
	     		    group_order.push($(this).data('admin-menu-container-name'))
	     		})
			data['group_order'] = JSON.stringify(group_order)
			data['user'] = $('body').first().data('rai-user_pk')
	    		$R.post(url, {
			    data : data
			}).done(
			    function(data){
				console.log(data)
			    }
			)
			
			
		    }
		})
		$('.user-editable').editablecontent()
		
	    }
	)
    }
)

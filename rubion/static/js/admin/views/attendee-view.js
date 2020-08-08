$.widget(
    'attendeeview.importresults',
    {
	_create : function(){
	    var self = this
	    this.importUrl = this.element.data('import-url')
	    this.editUrl = this.element.data('edit-url')
	    this.element.click(
		function(){
		    self._openModal()
		}
	    )
	    this.studentIds = []
	    $('[data-attendee-field="student_id"]').each(
		function(){
		    $(this).attr('data-studentid', $(this).text())
		    self.studentIds.push($(this).text())
		}
	    )
	},
	_openModal : function(){
	    this.gmodal = $R.genericModal({
		title : 'Klausurergebnis importieren',
		saveLabel : 'Datei hochladen',
		applyBtn : false,
		saveCallback : function(){self._upload()}
	    })
	    this.gmodal.show()
	    var self = this
	    $R.get(this.importUrl, {})
		.fail()
		.done(function(data){
		    self.gmodal.setBody('<form enctype="multipart/form-data">'+data['html']+'</form>')
		    
		    self._initFileUploadForm()
		})
	    this.$saveBtn = this.gmodal.getButton('save')
	    this.$saveBtn.prop('disabled', true)
	    
	},
	_initFileUploadForm : function(){
	    bsCustomFileInput.init()
	    var $body = this.gmodal.getBody(),
		self = this
	    this.$file = $body.find('input[type="file"]').first()
	    
	    this.$file.change(
		function(){
		    self.$saveBtn.prop('disabled', false)
		}
	    )
	},
	_upload : function(){
	    var $form = this.gmodal.getBody().find('form'),
		formData = new FormData($form[0]),
		$upload = $('<div class="upload" />').css({
		    'position' : 'relative',
		    'border' : 'thin solid #000',
		    'height' : '2rem'

		}).insertAfter($form),
		$uploadCounter = $('<span />').css({
		    'position' : 'absolute',
		    'left' : '50%',
		    'top' : '50%',
		    'zIndex' : '100',
		    'transform' : 'translate(-50%, -50%)'
		}).appendTo($upload),
		$uploadBar = $('<div />').css({
		    'position' : 'absolute',
		    'left' : '0px',
		    'top' : '0px',
		    'height' : '100%',
		    'width' : '0%',
		    'background-color' : 'var(--input-border-color)'
		}).appendTo($upload),
		self = this
	    
	    $form.hide()
	    
	    // 	'position': 'absolute',
	    // 	'height': '0px',
	    // 	'top' : '-10000px',
	    // 	'left' : '-10000px',
	    // })
	    
	    $R.post(
		this.importUrl,
		{
		    data : formData,
		    processData : false,
		    contentType : false,
		    xhr : function(){
			var xhr = $.ajaxSettings.xhr()
			xhr.upload.addEventListener(
			    'progress',
			    function(e){
				if (e.lengthComputable){
				    var p = Math.round(100 * e.loaded/e.total) 
				    $uploadCounter.html(p+ ' %')
				    $uploadBar.css('width',p+'%')
				}
			    },
			    false
			)
			xhr.upload.addEventListener(
			    'load',
			    function(e){
				$uploadCounter.html('100 %')
			    },
			    false
			)

			return xhr
		    }

		}
	    ).fail()
		.done(function(data){
		    self.tableData = data['html']
		    self.gmodal.dismiss(function(){self._showTable()})
		    
		})
		
	    
	},
	_showTable : function(){
	    var $table = $(this.tableData),
		nSelectedCols = 0,
		maxSelectedCols = 2
	    
	    
	    this.gmodal = $R.genericModal({
		title : 'Spalten mit Matrikelnummer und Note durch Klicken auswählen',
		applyBtn : false,
		body : $table,
		size : 'xxl',
		scroll : true,
		saveCallback : function(){self._save($table)}
	    })
	    var self = this,
		indexes = []
	    $table.find('th, td').each(function(){
		if($(this).text() !='' && self.studentIds.indexOf($(this).text()) > -1){
		    $(this).addClass('match')
		    indexes.push($(this).index())
		}
	    })
	    var uIndexes = Array.from(new Set(indexes))
	    if (uIndexes.length == 1){
		var index = uIndexes[0]-1
		$table.find('tr').each(function() {
		    $(this).find('td')
			.eq(index)
			.attr('data-selected-col', nSelectedCols)
		    
		    
		    $(this).find('th')
			.eq(index+1)
			.attr('data-selected-col', nSelectedCols)
		    
		})
		$table.find('[data-selected-col]').css({
		    'background-color':'var(--highlight-background-color)'
		})
		nSelectedCols++;
	    }

	    var saveBtn = this.gmodal.getButton('save').prop('disabled', true)
	    
	    $table.find('th, td').click(
		
		function(evt){
		    $table.find('th, td').css({'background-color':'#fff'})
		    var index = $(this).index()-1;
		    if($(this).is('[data-selected-col]')){
			var selectedCol = $(this).data('selected-col')
			$table.find('tr').each(function() {
			    $(this).find('td')
				.eq(index)
				.removeAttr('data-selected-col')
			    $(this).find('th')
				.eq(index+1)
				.removeAttr('data-selected-col')
			});
			if (selectedCol < maxSelectedCols-1){
			    $table.find('[data-selected-col]').each(
				function(){
				    if ($(this).data('selected-col') > selectedCol){
					$(this).data('selected-col', $(this).data('selected-col')-1)
				    } 
				}
			    )
			}
			nSelectedCols--;
		    } else {
			if (nSelectedCols >= maxSelectedCols){
			    $table.find('[data-selected-col="0"]')
				.removeAttr('data-selected-col')
			    $table.find('[data-selected-col]').each(
				function(){
				    $(this).attr('data-selected-col', $(this).data('selected-col')-1)
				}
			    )
			    nSelectedCols--;
			}
			$table.find('tr').each(function() {
			    $(this).find('td')
				.eq(index)
				.attr('data-selected-col', nSelectedCols)
			    
			    
			    $(this).find('th')
				.eq(index+1)
				.attr('data-selected-col', nSelectedCols)
			    
			});
			nSelectedCols++;
			
			
		    }
		    $table.find('[data-selected-col').css({
			'background-color':'var(--highlight-background-color)'
		    })
		    if (nSelectedCols == maxSelectedCols){
			saveBtn.prop('disabled', false)
		    }
		}
	    )
	    this.gmodal.show()
	    this.$table = $table
	},
	_save : function(){
	    var self = this
	    this.$table.find('[data-selected-col="0"]').each(
		function(){
		    var $td1 = $(this),
			$tr = $(this).closest('tr'),
			$td2 = $tr.find('[data-selected-col="1"]').first(),
			id, mark
		    if (self.studentIds.indexOf($td1.text()) > -1){
			id = $td1.text()
			mark = $td2.text()
		    } else {
			if (self.studentIds.indexOf($td2.text()) > -1){
			    id = $td2.text()
			    mark = $td1.text()
			}
		    }

		    if (id === undefined){
			return
		    }
		    $('[data-studentid="'+id+'"]').first()
			.closest('tr')
			.find('[data-ajax-field="result"]')
			.first().val(mark).trigger('change')
		    
		}
	    )
	    this.gmodal.dismiss()
	}
    }
)
$.widget(
    'attendeeview.unifycourses',
    {
	_create : function(){
	    var self = this
	    this.element.click(function(){
		self._openModal()
	    })
	    this.$table = $('table.attendee-list').first()
	    this.url = this.$table.data('attendee-edit-url')
	},
	_openModal : function(){
	    var self = this,
		$table = $('<table style="width:100%"/>'),
		$thead = $('<thead />').appendTo($table),
		$headrow = $('<tr />').appendTo($thead),
		$tbody = $('<tbody />').appendTo($table);
	    
	    
	    ['Name, Vorname', 'Fach bisher', 'Fach neu'].forEach(
		(elem) => $headrow.append($('<th>'+elem+'</th>'))
	    )
		
	    
	    $('[data-attendee-field="student_course"]').each(
		function(){
		    var $tr = $(this).parents('tr'),
			pk = $tr.data('attendee-pk'),
			$row = $('<tr />').data('attendee-pk', pk),
			
			name = $tr.find('[data-attendee-field="attendee-name"]').text(),
			origCourse = $(this).text(),
			studentId = $tr.find('[data-attendee-field="student_id"]').text(),
			$inputRow = $('<td />'),
			$input = $('<input class="form-control" name="student_course_'+pk+'"/>').appendTo($inputRow),
			newCourse = origCourse
		    
		    
		    $row.append('<td>'+name+'<br /><span class="text-muted">'+studentId+'</span></td>').append('<td>'+origCourse+'</td>')


		    if(origCourse.toLowerCase().indexOf('biochem') >= 0){
			newCourse = 'Biochemie'
		    } else {
			if(origCourse.toLowerCase().indexOf('physik') >= 0 || origCourse.toLowerCase().indexOf('physic') >= 0){
			    newCourse = 'Physik'
			}
		    }
		    $input
			.val(newCourse)
			.attr('data-old-value', origCourse)
			.change(function(evt){
			    var newVal = $(evt.target).val(),
				oldVal = $(evt.target).data('old-value')

			    if (newVal  != oldVal){
				$row.css('background-color','var(--danger-background-color)')
			    } else {
				$row.css('background-color','#fff')
			    }
			})
		    if (newCourse != origCourse){
			$row.css('background-color', 'var(--danger-background-color)')
			// $input.css('background-color', 'var(--danger-background-color)')
			// $input.css('color', 'var(--danger-color)')
			// $input.css('border-color', 'var(--danger-color)')
			
		    }
		    $row.append($inputRow)
		    
		    $row.appendTo($tbody)
		    
		}
	    )
	    this.gmodal = $R.genericModal({
		'title' : 'Studienfächer angleichen',
		'size' : 'lg',
		body : $table,
		applyCallback : function(){self._apply()},
		saveCallback : function(){self._save()},
		cancelCallback : function(){self._cancel()}
	    })
	    this.gmodal.show()
	},
	_cancel : function(){
	    this.gmodal.dismiss()
	},
	_save : function () {
	    this._apply()
	    this.gmodal.dismiss()
	},
	_apply : function(){
	    var $body = this.gmodal.getBody(),
		$inputs = $body.find('input'),
		self = this
	    $inputs.each(
		function(){
		    var $this = $(this)
		    if ($this.val() !== $this.data('old-value')){
			var pk = $this.parents('tr').first().data('attendee-pk')
			
			$R.post(self.url, {
			    data : {
				pk : pk,
				field : 'student_course',
				'student_course' : $this.val()
			    }
			}).fail()
			    .done(function(data){
				var $row = self.$table
				    .find('tr[data-attendee-pk="'+pk+'"]')
				    .first()
				var $field = $row
				    .find('[data-attendee-field="student_course"]')
				    .first()
				$field.text(data['object']['student_course'])
				$R.message(
				    'success',
				    'Fach von '
					+$row.find('[data-attendee-field="attendee-name"]')
					.first()
					.text()
					+' geändert'
				)
			    })
		    }
		}
	    )
	    
	}
    }
)


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
	    var self = this;
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
	    if ($elem.data('post-method') == 'ajax-receive-file'){
		this.modal = $R.waitDialog({
		    onShown : function(){self._sendRequest($elem, $form)}
		})
	    } else {
		$form.submit()
	    }
	},
	_sendRequest : function($elem, $form){
	    var request = new XMLHttpRequest();
	    request.open('POST', $elem.data('form-url'), true);
	    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
	    request.responseType = 'blob';
	    var self = this
	    request.onload = function() {
		// Only handle status code 200
		if(request.status === 200) {
		    // Try to find out the filename from the content disposition `filename` value
		    var disposition = request.getResponseHeader('content-disposition');
		    var matches = /filename=(.+)$/.exec(disposition);
		    var filename = (matches != null && matches[1] ? matches[1] : 'file.pdf');
		    
		    // The actual download
		    var blob = new Blob([request.response], { type: 'application/pdf' });
		    var link = document.createElement('a');
		    link.href = window.URL.createObjectURL(blob);
		    link.download = filename;
		    
		    document.body.appendChild(link);
		    
		    link.click();
		    self.modal.close();
		    document.body.removeChild(link);
		}
		
		// some error handling should be done here...
	    };
	    
	    request.send($form.serialize());
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

$(document).on(
    'rubiontail.baseloaded',
    function(){
	$('#attendeViewUnifyCourses').unifycourses()
	$('#attendeViewImportResult').importresults()
	$('.attendee-list').attendeelist()

    }
)
$(document).on('rubiontail.baseloaded', function(){
    console.log('Fertig geladen')
    $('#loadscreen').fadeOut(200, function(){$('#loadscreen').remove()})
})

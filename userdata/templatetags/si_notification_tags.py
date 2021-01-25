from django import template
#

register = template.Library()

@register.filter
def si_list(obj):
    '''Liste der Unterweisungen (übersetzt)'''
    
    from django.utils.translation import get_language 
    s = ''
    lang = get_language()
    for si in obj:
        if lang == 'en':
            s+= si['instruction'].title_en_short
        else:
            s+= si['instruction'].title_de_short
        s+='\n'
    return s

@register.filter
def si_list_dashes(obj):
    '''Liste der Unterweisungen mit Strich am Anfang (übersetzt)'''
    from django.utils.translation import get_language 
    s = ''
    lang = get_language()
    for si in obj:
        if lang == 'en':
            s+= '- '+si['instruction'].title_en_short
        else:
            s+= '- '+si['instruction'].title_de_short
        s+='\n'
    return s
@register.filter
def si_list_dates(obj):
    '''Liste der Unterweisungen mit Ablaufdatum (übersetzt)'''
    from django.utils.translation import get_language 
    s = ''
    lang = get_language()
    fs = '{:.<60}.{:.>19}'


    for si in obj:

        if si['valid_until']:
            if lang == 'en':
                validity = si['valid_until'].strftime(' %Y-%m-%d')
            else:
                validity = si['valid_until'].strftime(' %d.%m.%Y')
        else:
            validity = ' --'
        if lang == 'en':

            s+= fs.format(si['instruction'].title_en_short[0:58]+' ', validity)
        else:
            s+= fs.format(si['instruction'].title_de_short[0:58]+' ', validity)

        s+='\n'
    return s
    

# @register.filter
# def si_name(obj):
#     '''Bezeichnung der Unterweisung'''
#     return obj.title_de

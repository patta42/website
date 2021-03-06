from wagtail.core import hooks

REGISTERED_ITEMS = {}

for fn in hooks.get_hooks('register_rai_item'):
    item, new_subitem = fn()
    subitems = REGISTERED_ITEMS.pop(item, [])
    subitems.append(new_subitem)
    REGISTERED_ITEMS.update({item: subitems})

    
def registered_rai_items_as_choices(flat = False):
    choices = []
    for main_id, components in REGISTERED_ITEMS.items():
        sub_choices = []
        for component in components:
            item = ('{}.{}'.format(main_id, component['id']), component['label'])
            if flat:
                choices.append(item)
            else:
                sub_choices.append(item)
        if not flat:
            choices.append((main_id, sub_choices))
    return choices

def registered_rai_items_as_flat_choices():
    return registered_rai_items_as_choices(flat = True)


REGISTERED_DECORATIONS = {}

for fn in hooks.get_hooks('rai_decoration'):
    rai_model_id, decoration = fn()
    decorations_for_model = REGISTERED_DECORATIONS.get(rai_model_id, {})
    decorations_for_model.update(decoration)
    REGISTERED_DECORATIONS.update({rai_model_id : decorations_for_model})

def get_decorator_for(rai_model_id, decorated_model_id):
    decorations_for_rai = REGISTERED_DECORATIONS.get(rai_model_id, None)
    if decorations_for_rai:
        return decorations_for_rai.get(decorated_model_id, None)
    return None

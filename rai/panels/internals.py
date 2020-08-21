from wagtail.core import hooks

REGISTERED_PANELS = {}

for fn in hooks.get_hooks('rai_front_panel'):
    REGISTERED_PANELS.update(fn())

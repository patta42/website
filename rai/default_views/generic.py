from django.views.generic import TemplateView

class RAIView(TemplateView):
    """ 
    A generic view for RAI which implements rendering the admin menu.
    Does *not* require a RAIAdmin definition
    """
    def get_main_admin_menu(self):
        items = []
        for fn in hooks.get_hooks('rai_menu_group'):
            item = fn()
            components = [];
            for Component in item.components:
                component = Component()
                components.append({
                    'label' : component.menu_label,
                    'icon' : component.menu_icon,
                    'icon_font' : component.menu_icon_font,
                    'url' : component.get_default_url()
                })
                    
            items.append({
                'label' : item.menu_label,
                'components' : components
            })
            
        return render_to_string(
            'rai/menus/main_admin_menu.html',
            {
                'items' : items
            }
        )
    
    def get_context_data(self, **kwargs):
        """
        adds the main admin menu to the Context object
        """
        context = super().get_context_data(**kwargs)
        context['main_admin_menu'] = self.get_main_admin_menu()
        return context



class RAIAdminView(RAIView):
    """
    A view which requires a RAIAdmin definition and an active RAIAction object

    Furthermore, implements some simple media interface for adding view-specific js and css.
    [Note: The latter might already be implemented in the TemplateView, I'm not sure.]
    """
    
    raiadmin = None
    active_action = None
    media = {
        'js'  : [],
        'css' : []
    }
    inline_media = {
        'js'  : [],
        'css' : []
    }

    def get_context_data(self, **kwargs):
        """
        adds the media to the Context object
        in 'media', file names are stored which should be inserted in the template via {% static %}
        in 'inline_media', inline definitions are stored which should be enclosed in <style></style> or <script></script>
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'media' : self.media,
            'inline_media' : self.inline_media
        })

        return context



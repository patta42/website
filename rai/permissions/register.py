from pprint import pprint

from django.utils.translation import ugettext as _

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, DeleteAction
from rai.base import RAIModelAdmin, RAIAdminGroup
import rai.edit_handlers as eh
from rai.permissions.edit_handlers import PermissionSelectionInlinePanel, PermissionForm
from rai.permissions.models import RAIGroup, RAIPermission
from rai.widgets import RAISelectMultipleSelectionLists, RAISelect 

from rai.default_views import EditView

class PermissionEditView(EditView):
    def save_post_hook(self, request, form):
        saved_something = False
        for key, formset in self.formsets.items():
            if key == 'permissions':
                instances = formset.save(commit = False)
                for instance in instances:
                    instance.group = self.obj
                    instance.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                saved_something = True
            else:
                formset.save()
                saved_something = True
                    
        if form.has_changed():
            form.save()
            saved_something = True

        if saved_something:
            self.success_message('Die Daten wurden aktualisiert.')
        else:
            self.info_message('Die Daten enthielten keine Änderung und wurden nicht gespeichert.')


        
        
group_edit_handler = eh.RAIPillsPanel(
    [
        eh.RAIObjectList([
           PermissionSelectionInlinePanel('permissions', 'rai_id','value', heading='Definition der Berechtigungen', allow_add = True, can_delete = True)
        ], heading = 'Berechtigungen'),
        eh.RAIObjectList([
            eh.RAIFieldPanel('members', widget = RAISelectMultipleSelectionLists)
        ], heading ='Mitglieder'),
        eh.RAIObjectList([
            eh.RAIFieldPanel('name'),
            eh.RAIFieldPanel('description'),
        ], heading = 'Beschreibung')
        
    ]
)

class RAIGroupListAction(ListAction):
    list_item_template = 'rai/permissions/rai_groups/list/item-in-list.html'


class RAIGroupCreateAction(CreateAction):
    edit_handler = group_edit_handler


class RAIGroupEditAction(EditAction):
    edit_handler = group_edit_handler

    
class RAIGroupDetailAction(DetailAction):
    edit_handler = group_edit_handler


class RAIGroup(RAIModelAdmin):
    model = RAIGroup
    menu_label = _('Gruppen')
    menu_icon = 'user-friends'
    menu_icon_font = 'fas'
    group_actions = [RAIGroupListAction, RAIGroupCreateAction]
    item_actions = [RAIGroupEditAction, RAIGroupDetailAction, DeleteAction]
    default_action = ListAction
    identifier = 'permissions'
    editview = PermissionEditView
    
class RAIPermissionsGroup(RAIAdminGroup):
    components = [
        RAIGroup
    ]
    menu_label = _('Permission settings')

    

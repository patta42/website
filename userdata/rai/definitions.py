from django.template.loader import render_to_string

from rai.edit_handlers.generic import RAIEditHandler

class StaffUserInfoPanel(RAIEditHandler):
    template_name = 'userdata/staffuser/rai/edit_handlers/staff-info-panel.html'
    def render(self):
        return render_to_string(
            self.template_name,
            {'self' : self}
        )

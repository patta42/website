from rai.panels.base import FrontPanel

from userinput.models import WorkGroup

from wagtail.core.models import PageRevision

class WorkgroupApplicationPanel(FrontPanel):
    template = 'userinput/workgroup/panels/application.html'
    identifier = 'userinput.workgroup.application'

    title = 'Anträge auf Einrichtung einer AG'
    desc = 'Listet die offenen Anträge auf Einrichtung einer AG'

    max_cols = 2
    max_rows = 2

    def get_context(self):
        context = super().get_context()

        wg = WorkGroup.objects.all()
        pr = PageRevision.objects.filter(submitted_for_moderation = True).filter(page__in = wg)

        context['groups'] = pr
        
        return context

    
class ProjectApplicationPanel(FrontPanel):
    template = 'userinput/project/panels/application.html'
    identifier = 'userinput.project.application'

    title = 'Projektanträge'
    desc = 'Listet die offenen Projektanträge'

    max_rows = 2

    
    
class UserStatsPanel(FrontPanel):
    template = 'userinput/generic/panels/user-stats.html'
    identifier = 'userinput.stats'

    title = 'Nutzerstatistik'
    desc = 'Listet die Anzahl der Nutzer und Arbeitsgruppen im zeitlichen Verlauf'

    max_cols = 2

    def __init__(self, rows= 1, cols = 2, position = None, **kwargs):
        super().__init__(rows, cols, position, **kwargs)
    

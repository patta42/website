from django.conf.urls import url, include
from django.views.decorators.cache import never_cache

from rai.views import HomeView

from wagtail.admin.decorators import require_admin_access
from wagtail.core import hooks
from wagtail.utils.urlpatterns import decorate_urlpatterns

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='rai_home'),
]

# Import additional urlpatterns from any apps that define a register_rai_urls hook
for fn in hooks.get_hooks('register_rai_url'):
    urls = fn()
    if urls:
        urlpatterns += urls

urlpatterns = decorate_urlpatterns(urlpatterns, require_admin_access)



from rai.base import rai_register
from rai.notifications.register import RAINotificationsGroup
from rai.permissions.register import RAIPermissionsGroup

import rai.comments.register
import rai.files.register
import rai.help.register
import rai.mail.register
import rai.markdown.register
import rai.panels.register
import rai.settings.register

rai_register(RAINotificationsGroup)
rai_register(RAIPermissionsGroup)



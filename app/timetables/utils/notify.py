import logging

from timetables.utils import settings


log = logging.getLogger(__name__)

NOTIFIER_KEY = "NOTIFIER"
DEFAULT_NOTIFIER = "timetables.utils.notify.BasicNotifier"
NOTIFICATION_METHODS_KEY = "NOTIFICATION_METHODS"


__notifier = None

# I'm assuming we're only ever wanting one notifier, we could extend this to 
# something like get_notifier(name).
def get_notifier():
    global __notifier
    if __notifier is None:
        notifier_cls = settings.get_callable(NOTIFIER_KEY,
                default=DEFAULT_NOTIFIER)
        
        # Get a list of the NotificationMethod classes to use, and instanciate
        # each of them.
        notification_methods = [method() for method in
                settings.get_callable_list(NOTIFICATION_METHODS_KEY,
                        default=[])]
        
        # Instantiate the notifier, passing a list of notification methods for
        # it to delegate to
        __notifier = notifier_cls(notification_methods)
    
    return __notifier

class BasicNotifier(object):
    """
    The bog standard notifier implementation. Synchronously calls each
    notification method on the caller's thread.
    """
    def __init__(self, notification_methods):
        self._notification_methods = list(notification_methods)
    
    def notify(self, obj, **kwargs):
        handled = False
        for notification_method in self._notification_methods:
            if notification_method.can_handle(obj):
                notification_method.dispatch(obj, **kwargs)
                handled = True
        
        if not handled:
            log.warn("No notification methods handled object: %s" % obj)

# An alternate Notifier implementation might use a task queue to asynchronously
# run notifications...

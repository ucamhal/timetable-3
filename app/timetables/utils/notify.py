import logging

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models import Q

from timetables.utils import settings
from timetables.models import Event, Thing


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


# NotificationMethod types
class EmailNotificationMethod():
        
    def can_handle(self, obj):
        """
        Check that obj is of type Event or represents an event series
        """
        if isinstance(obj, Event): # event
            return True
        if isinstance(obj, Thing): # thing - test if event series
            if obj.type == 'series': # TODO
                return True
        return False
    
    
    def dispatch(self, obj, **kwargs):
        """
        Gets list of users who have added obj to their personal timetable.
        Construct list of user CRS IDs.
        Construct notification subject / message based on obj type.
        Pass all to email().
        """
        
        # events
        if isinstance( obj, Event ):
            id_event = obj.id
            ids_users = Thing.objects.filter( Q(type = "user") & Q(sources__event = id_event) ).values_list('name', flat=True) # get list of usernames of users who have added the specified event
            recipients = User.objects.filter( username__in = ids_users ).values_list('email', flat=True) # get list of user e-mails
            
            # TODO - get new details about the event. Need e-mail template from PJH
            
            subject = "Update to event "+obj.title
            message = "The event "+obj.title+" has been updated."
        
        # event series
        if isinstance( obj, Thing ):
            if obj.type == 'series':
                return False # TODO
            
        self.email(recipients, subject, message)
            
        
    def email(self, recipients, subject, message):
        """
        Sends an e-mail to the specified recipients.
        Recipients should be list of full e-mails.
        """
        
        email = EmailMessage(
            subject, # subject
            message, # body
            to = [settings.get("DEFAULT_TO_EMAIL", default="noreply@example.com")], # to
            bcc = recipients, # bcc all recipients
        )
        
        email.send()

from django.conf import settings

from django.contrib.auth.models import User

from django.core.mail import EmailMessage

from django.db.models import Q

from timetables.models import Event, Thing



class Notify():
        
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
            to = [settings.DEFAULT_TO_EMAIL], # to
            bcc = recipients, # bcc all recipients
        )
        
        email.send()
        
"""
Defines API importers, which take ModuleData and put it into the database
"""

import datetime

from timetables.api.util import APILogger, TIMEZONE, DataValidationException
from timetables.models import Event, EventSource, EventSourceTag, Thing

class APIImporter(object):
    """
    Takes a ModuleData and processes it, updating the database
    as required. Requires a user to verify their permissions
    """

    def __init__(self, user, logger=None):
        self.user = user
        if logger is not None:
            self.logger = logger
        else:
            self.logger = APILogger()

        self.thing_list = Thing.objects.all()
        self.event_list = Event.objects.all()
        self.event_source_list = EventSourceTag.objects.all()

    def add_module_data(self, module):
        """
        Adds the data in module to the database. Performs
        a check to ensure that user has the appropriate permission.
        Will not create Things above the module level.
        """
        try:
            module.is_valid()
        except DataValidationException as err:
            self.logger.log(
                'failed',
                'module',
                'Module data not valid {0}'.format(err)
            )
            return

        path = module['path']

        # find the parent of the module
        try:
            parent_thing = self.thing_list.get(pathid=Thing.hash(path[:-1]))
        except Thing.DoesNotExist:
            self.logger.log(
                'failed',
                'module',
                'The path {0} does not exist'.format(path[:-1])
            )
            return

        # check for permission
        if not parent_thing.can_be_edited_by(self.user.username):
            self.logger.log(
                'denied',
                'module',
                'You do not have permission to modify {0}'.format(path[:-1])
            )
            return

        self.process_module_dict(module)


    def process_module_dict(self, module):
        """
        Processes a ModuleData dict and updates the database
        """

        path = module['path']
        try:
            db_module = self.thing_list.get(
                pathid=Thing.hash(path+module['shortname'])
            )
        except Thing.DoesNotExist:
            db_module = None

        is_deleting_module = module.is_being_deleted()

        if db_module is None:
            if is_deleting_module:
                # wanted to delete it, doesn't exist, nothing to do
                return
            db_module = self.create_module(
                path,
                module['name'],
                module['shortname']
            )
            if db_module is None:
                # something went wrong creating the module (no need to report
                # it as the logger should already contain the details)
                return

        # check if we want to delete it
        if is_deleting_module:
            self.delete_module(db_module)
            return

        # create a list of child sources
        module_sources = []
        matching_source_tags = self.event_source_list.filter(
            thing=db_module,
            annotation='home'
        )

        for tag in matching_source_tags:
            # check it was imported via the api
            if 'importid' in tag.eventsource.metadata:
                module_sources.append(
                    (tag.eventsource, tag.eventsource.metadata['importid'])
                )

        for source in module['seriesList']:
            db_source = self.process_source_dict(
                module_sources, db_module, source
            )
            if db_source is not None:
                module_sources.append(
                    (db_source, db_source.metadata['importid'])
                )



    def process_source_dict(self, module_sources, db_module, source):
        """
        Processes a SeriesData dict and updates the database
        """

        is_deleting_source = source.is_being_deleted()
        db_source = None

        # check if the source is already in the data
        for existing_source in module_sources:
            if existing_source[1] == source['externalid']:
                db_source = existing_source[0]
                break

        # update/add/delete the source
        if db_source is not None:
            if is_deleting_source:
                self.delete_source(db_source)
                return
            else:
                self.update_source(db_source, source)
        else:
            # doesn't exist
            if is_deleting_source:
                return
            else:
                db_source = self.add_source(db_module, source)

        for event in source['events']:
            self.process_event_dict(db_source, event)

        return db_source


    def process_event_dict(self, db_source, event):
        """
        Processes a EventData dict and updates the database
        """
        if event.is_being_deleted():
            # delete it if it exists
            self.delete_event(
                db_source,
                event
            )
        else:
            self.add_or_update_event(
                db_source,
                event
            )

    def create_module(self, path, name, shortname):
        """
        Creates a module in the database. Will not create Things above
        module level, and will fail if the path is not unique.
        """

        # find the parent (remove end slash)
        try:
            parent = self.thing_list.get(pathid=Thing.hash(path[:-1]))
        except Thing.DoesNotExist:
            self.logger.log(
                'failed',
                'module',
                'Could not find path {0}'.format(path[:-1])
            )
            return
        except Thing.MultipleObjectsReturned:
            self.logger.log(
                'failed',
                'module',
                'Path {0} was not unique'.format(path[:-1])
            )
            return

        db_module = Thing(
            fullname=name,
            type='module',
            parent=parent,
            name=shortname
        )

        self.logger.log('insert', 'module', name)
        db_module.save()

        return db_module


    def delete_module(self, db_module):
        """
        Deletes a module from the database. Also deletes all event
        sources attached to the module.
        """

        self.logger.log('delete', 'module', db_module.fullname)

        # clear the module of all of its sources (and their events)
        matching_source_tags = self.event_source_list.filter(
            thing=db_module
        ).prefetch_related('eventsource')

        for tag in matching_source_tags:
            db_source = tag.eventsource
            self.delete_source(db_source)

        db_module.delete()


    def update_source(self, db_source, source):
        """
        Verifies that source and db_source differ, and updates
        db_source if they do.
        """

        has_name_data = 'name' in source
        has_lecturer_data = ('lecturer' in source and
                            source['lecturer'] is not None)
        has_location_data = ('location' in source and
                            source['location'] is not None)

        has_db_people = 'people' in db_source.metadata
        has_db_location = 'location' in db_source.metadata

        if has_lecturer_data and has_db_people:
            lecturer_changed = (
                db_source.metadata['people'] != source['lecturer']
            )
        else:
            lecturer_changed = has_lecturer_data and not has_db_people

        if has_location_data and has_db_location:
            location_changed = (
                db_source.metadata['location'] != source['location']
            )
        else:
            location_changed = has_location_data and not has_db_location

        name_changed = has_name_data and (db_source.title != source['name'])

        if name_changed or lecturer_changed or location_changed:
            db_source.title = source['name']

            if has_lecturer_data:
                db_source.metadata['people'] = source['lecturer']
            if has_location_data:
                db_source.metadata['location'] = source['location']

            db_source.save()

            self.logger.log('update', 'source', source['name'])

        return db_source


    def add_source(self, db_module, source):
        """
        Adds an event source to the database. Also adds the
        source tag to connect it to db_module, using
        annotation 'home'
        """

        db_source = EventSource(
            title=source['name'],
            sourcetype='importapi'
        )

        db_source.metadata['importid'] = source['externalid']

        if 'lecturer' in source and source['lecturer'] is not None:
            db_source.metadata['people'] = source['lecturer']

        if 'location' in source and source['location'] is not None:
            db_source.metadata['location'] = source['location']

        self.logger.log('insert', 'source', source['name'])
        db_source.save()

        # add the source tag
        source_tag = EventSourceTag(
            thing=db_module,
            eventsource=db_source,
            annotation='home'
        )
        self.logger.log(
            'insert',
            'sourcetag',
            db_module.name+' > '+db_source.title
        )
        source_tag.save()

        return db_source


    def delete_source(self, db_source):
        """
        Deletes a source from the database. Will also delete
        all child events that have this as their source. For
        logging clarity, reports the deletion of the source
        before deletion of the children.
        """

        child_events = self.event_list.filter(source=db_source)

        self.logger.log('delete', 'source', db_source.title)
        for event in child_events:
            self.logger.log('delete', 'event', event.title)
            event.delete()

        db_source.delete()


    def delete_event(self, db_source, event):
        """
        Deletes the event specified. The event is identified by
        it's uid (with the import- prefix) and its source.
        """

        event_uid = event.get_internal_id()

        try:
            matching_event = self.event_list.get(
                uid=event_uid,
                source=db_source
            )
        except Event.MultipleObjectsReturned:
            self.logger.log(
                'failed',
                'event',
                'Multiple events found with uid {0}'.format(event_uid)
            )
            return
        except Event.DoesNotExist:
            return

        self.logger.log('delete', 'event', matching_event.title)
        matching_event.delete()


    def add_or_update_event(self, db_source, event):
        """
        Checks if an event exists identified (by uid with import-
        prefix and by source) and updates it or adds it as
        appropriate. Will only update if the new data differs from
        the current data.
        """

        event_uid = event.get_internal_id()

        try:
            db_event = self.event_list.get(uid=event_uid, source=db_source)
        except Event.DoesNotExist:
            db_event = None
        except Event.MultipleObjectsReturned:
            self.logger.log(
                'failed',
                'event',
                'Event uid {0} was not unique'.format(event_uid)
            )
            return

        start_time = TIMEZONE.localize(
            datetime.datetime.combine(event['date'], event['start'])
        )
        end_time = TIMEZONE.localize(
            datetime.datetime.combine(event['date'], event['end'])
        )

        # check for existence
        if db_event is None:
            # add a new event
            db_event = Event(
                start=start_time,
                end=end_time,
                title=event['name'],
                location=event['location'],
                uid=event_uid,
                source=db_source,
                status=0
            )
            db_event.metadata['people'] = event['lecturer']
            db_event.metadata['type'] = event['type']
            self.logger.log('insert', 'event', event['name'])
            db_event.save()
        else:
            # check if an update is required
            if('people' not in db_event.metadata or
                'type' not in db_event.metadata or
                db_event.start != start_time or
                db_event.end != end_time or
                db_event.title != event['name'] or
                db_event.location != event['location'] or
                db_event.uid != event_uid or
                db_event.source != db_source or
                db_event.status != 0 or
                db_event.metadata['people'] != event['lecturer'] or
                db_event.metadata['type'] != event['type']
               ):
                # update it
                db_event.start = start_time
                db_event.end = end_time
                db_event.title = event['name']
                db_event.location = event['location']
                db_event.uid = event_uid
                db_event.source = db_source
                db_event.status = 0
                db_event.metadata['people'] = event['lecturer']
                db_event.metadata['type'] = event['type']
                self.logger.log('update', 'event', event['name'])
                db_event.save()

        return db_event

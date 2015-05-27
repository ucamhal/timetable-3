from timetables.models import Event, NestedSubject, Thing, EventSource


class TraversalException(Exception):
    pass


class ValidationException(TraversalException):
    pass


class InvalidStructureException(TraversalException):
    pass


class IllegalStateException(TraversalException):
    pass


class Traverser(object):
    def __init__(self, obj):
        self.obj = obj
        self.validate_obj()

    def validate_obj(self):
        pass

    def step_up(self):
        return self._step(self.get_parent())

    def _step(self, parent):
        try:
            traverser, parent = parent
            return traverser(parent)
        except ValidationException as e:
            raise InvalidStructureException(
                "Couldn't traverse up from {}".format(self.get_name()),
                self.obj,
                e.args,
            )

    def get_value(self):
        return self.obj

    def get_name(self):
        return self.name


class ThingTraverserMixin(object):
    def validate_obj(self):
        if not isinstance(self.obj, Thing):
            raise ValidationException("Expected a Thing instance", self.obj)

    def get_parent_thing(self):
        parent = self.obj.parent
        if parent is None:
            raise InvalidStructureException("Thing has no parent", parent)
        return parent


class EventTraverser(Traverser):
    name = "event"

    def validate_obj(self):
        super(EventTraverser, self).validate_obj()
        if not isinstance(self.obj, Event):
            raise ValidationException("Expected an Event instance", self.obj)

    def get_parent(self):
        series = self.obj.source
        if series is None:
            raise InvalidStructureException("Event has no series", self.obj)
        return (SeriesTraverser, series)


class SeriesTraverser(Traverser):
    name = "series"

    def validate_obj(self):
        super(SeriesTraverser, self).validate_obj()
        if not isinstance(self.obj, EventSource):
            raise ValidationException(
                "Expected an EventSource instance", self.obj)

    def get_parent(self):
        return next(self.get_parents())

    def walk_parents(self):
        """
        Enumerate all traversers for all parent modules of the current series.
        """
        for parent in self.get_parents():
            yield self._step(parent)

    def get_parents(self):
        series = self.obj
        tags = list(series.eventsourcetag_set.filter(annotation="home"))

        if(len(tags) == 0):
            raise ValidationException(
                "Orphaned series with no module encountered", series.pk)

        for tag in tags:
            module = tag.thing

            if module.type != "module":
                raise ValidationException(
                    "Series attached to non-module thing", series.pk)
            yield (ModuleTraverser, module)


class ModuleTraverser(ThingTraverserMixin, Traverser):
    name = "module"

    def validate_obj(self):
        super(ModuleTraverser, self).validate_obj()
        if not self.obj.type == "module":
            raise ValidationException("Expected type to be 'module'", self.obj)

    def get_parent(self):
        obj = self.get_parent_thing()

        if obj.type == "part":
            return (PartTraverser, obj)
        return (SubpartTraverser, obj)


class SubpartTraverser(ThingTraverserMixin, Traverser):
    name = "subpart"

    def validate_obj(self):
        super(SubpartTraverser, self).validate_obj()
        if not self.obj.type in NestedSubject.NESTED_SUBJECT_TYPES:
            msg = "Expected type to be one of: {}".format(
                NestedSubject.NESTED_SUBJECT_TYPES)
            raise ValidationException(msg, self.obj)

    def get_parent(self):
        obj = self.get_parent_thing()
        return (PartTraverser, obj)


class PartTraverser(ThingTraverserMixin, Traverser):
    name = "part"

    def validate_obj(self):
        super(PartTraverser, self).validate_obj()
        if not self.obj.type == "part":
            raise ValidationException("Expected type to be 'part'", self.obj)

    def get_parent(self):
        obj = self.get_parent_thing()
        return (TriposTraverser, obj)


class TriposTraverser(ThingTraverserMixin, Traverser):
    name = "tripos"

    def validate_obj(self):
        super(TriposTraverser, self).validate_obj()
        if not self.obj.type == "tripos":
            raise ValidationException("Expected type to be 'tripos'", self.obj)

    def get_parent(self):
        raise IllegalStateException("Triposes have no parent")

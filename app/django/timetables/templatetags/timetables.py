from __future__ import absolute_import

from django import template

import json, logging
from django.template.base import Node, Variable, TemplateDoesNotExist
from django.template import loader
from django.template.context import Context

LOG = logging.getLogger(__name__)
register = template.Library()

@register.filter(name="json")
def json_encode(object):
    """JSON encodes the input value, returning JSON string."""

    try:
        json_string = json.dumps(object)
    except:
        LOG.exception("|json filter: Error JSON encoding object: %s" % object);
        json_string = "null /* error encoding JSON */"

    # In order to prevent HTML/JS injection attacks when including user 
    # controlled JSON content in <script> tags, we need to escape closing tag 
    # sequences in JSON strings, otherwise an attacker could insert a literal 
    # "</script> HTML HERE" sequence in a JSON string. 
    # See: http://www.w3.org/TR/html4/appendix/notes.html#h-B.3.2.1

    # Escape the sequence </ with the equivalent unicode code points.
    return json_string.replace("</", "\u003C\u002F")

class IncludeThingTemplateNode(Node):
    def __init__(self, template_name, context_thing):
        self.template_name = template_name
        self.context_thing = Variable(context_thing)

    def render(self, context):
        thing = self.context_thing.resolve(context)
        try:
            template = loader.get_template(self.template_name % (thing.type,))
        except TemplateDoesNotExist:
            template = loader.get_template(self.template_name % ("default",))
        template_context = Context(dict_=context)
        template_context.update({
            'thing': thing
        })
        return template.render(template_context)

@register.tag
def include_thing_template(parser, token):
    tag, template_name, context_thing = token.split_contents()
    return IncludeThingTemplateNode(template_name[1:-1], context_thing)
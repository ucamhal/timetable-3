from __future__ import absolute_import

from django import template

import json, logging

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
'''
Holds utility methods relating to http specific to timetables protcols.
Created on Aug 2, 2012

@author: ieb
'''

import logging
log = logging.getLogger(__name__)
del logging

class ContextKeys(object):
    '''
    Contains constants used in contexts
    '''

    CURRENT_PAGE = "current_page"
    PAGE = "page"
    SORT = "sort"
    SORT_ORDER = "sort_order"
    SEARCH_QUERY = "search_term"


class HttpParameters(object):
    '''
    Contains constants used as parameters in POSTs and GETs
    '''

    DESC = "d" # Descending order
    ASC = "u" # Ascending order
    SEARCH_QUERY = "q"
    SORT = "s"
    SORT_ORDER = "o"
    PAGE = "page"
    AJAX_REQUEST = "ajax-request" 


class Request(object):

    @staticmethod
    def build_tree(request, this_list_name, list_name, list_names, mappings):
        '''
        Recurses to build a tree from the POST.
        Assuming that the base of the tree is identified multiple POST parameters with the same name, that
        contain the ids of each fields set. The fields within that set take the form <fieldname>_<set_id>.
        Field names fall into 2 categories, those that contain values and those that contain lists of child ids.
        For each field name that contains a list of child ids, this method is called recursively.
        For each field name that contains a value, the value is stored.

        To use:
        call with the request
        the name of the parameter containing IDs that define the children in the current map
        the name that that parameter represents in  the mappings
        a list of names, define the parameter name at each level (there may be more than one at each level).
        And the mappings

        eg
        if groups contain series contain events
        build_tree(request, "group","group",["series","event"],{"group": [fields in each group], "series" : [field in each series], "event" : [ fields in each event ])

        the post might be like this:
        "group" : g1
        "group" : g2
        "group" : g3
        "group" : g4
        "title_g1" : "Title of Group 1"
        "title_g2" : "Title of Group 1"
        "title_g3" : "Title of Group 1"
        "title_g4" : "Title of Group 1"
        "series_g1" : s1
        "series_g1" : s2
        "series_g1" : s3
        "series_g2" : s4
        "series_g2" : s5
        "series_g3" : s6
        "series_g4" : s7
        "series_g4" : s8
        "stitle_s1" : "Title Series 1 from group 1"
        "stitle_s2" : "Title Series 2 from group 1"
        "stitle_s3" : "Title Series 3 from group 1"
        "stitle_s4" : "Title Series 4 from group 2"
        "stitle_s5" : "Title Series 5 from group 2"
        "stitle_s6" : "Title Series 6 from group 3"
        "stitle_s7" : "Title Series 7 from group 4"
        "stitle_s8" : "Title Series 8 from group 4"

        build_tree(request, "group","group",["series"],{"group": [ "title" ], "series" : [ "stitle" ]})

        result is
        {
          "g1" : {
            "title" : "Title of Group 1",
             "series_" : {
                     "s1" : {
                        "stitle" : "Title Series 1 from group 1"
                     },
                     "s2" : {
                        "stitle" : "Title Series 2 from group 1"
                     },
                     "s3" : {
                        "stitle" : "Title Series 3 from group 1"
                     }
                }
          "g2" : {
            "title" : "Title of Group 2",
             "series_" : {
                     "s4" : {
                        "stitle" : "Title Series 4 from group 2"
                     },
                     "s5" : {
                        "stitle" : "Title Series 5 from group 2"
                     }
                }
          "g3" : {
            "title" : "Title of Group 3",
             "series_" : {
                     "s6" : {
                        "stitle" : "Title Series 6 from group 3"
                     }
                }
          "g4" : {
            "title" : "Title of Group 4",
             "series_" : {
                     "s7" : {
                        "stitle" : "Title Series 7 from group 4"
                     },
                     "s8" : {
                        "stitle" : "Title Series 8 from group 4"
                     }
                }
          }

        The numbers do not have to be in sequence, but they must be unique for the form and listed in the field that defines the sub list.

        :param request:
        :param this_list_name: The parameter containing a list of child ids
        :param list_names: The prefix for further children
        :param mappings: A map of mappings between the list_names and the form parameters in that set
        :return a dict containing all the tree from this level down:
        '''
        container = {}
        log.info("Loading child list %s " % this_list_name )
        for eid in request.POST.getlist(this_list_name,[]):
            log.info("Processing Child %s " % eid )
            container[eid] = {}
            for n in mappings[list_name]:
                log.info("Processing Value %s_%s " % (n,eid))
                container[eid][n] = request.POST.get('%s_%s' % (n,eid),None)
            if len(list_names) > 0:
                next_set = list_names[0]
                if isinstance(next_set, list):
                    for n in next_set:
                        container[eid]['%s_' % n] = Request.build_tree(request, '%s_%s' % (n, eid), n, list_names[1:], mappings)
                else:
                    container[eid]['%s_' % next_set] = Request.build_tree(request, '%s_%s' % (next_set, eid), next_set, list_names[1:], mappings)
        return container

    @classmethod
    def get_default(cls, d, k, default=None):
        '''
        Get d[k] provided it exists and is not "", else return default
        :param d:
        :param k:
        :param default:
        '''
        try:
            if d[k] != "":
                return d[k]
        except:
            pass                            
        return default
    

    @classmethod
    def check(cls, d, k):
        '''
        Check if d[k] is "1"
        :param d:
        :param k:
        '''
        try:
            return d[k] == "1"
        except:
            pass
        return False


    

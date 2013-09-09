import re
import base64

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.template import RequestContext

from timetables.forms import APIFileForm
from timetables.models import Thing
from timetables.api import api
from timetables.api.util import DataValidationException

def userHasAccess(user, path):
    # can this user admin the Thing with that full path
    # this is set in the users page up to the level before module

    path = re.sub('/$', '', path)  # remove end slash
    
    try:
        thing = Thing.objects.get(pathid=Thing.hash(path))
    except Thing.DoesNotExist:
        return False
    except Thing.MultipleObjectsReturned:
        return False

    return thing.can_be_edited_by(user.username)

def do_xml_import(request):
    """
    Handles an XML import. Returns the summary of the API.

    The user must be an administrator to import anything,
    and must have permission to access the paths in the XML
    file
    """

    if(request.user.is_authenticated() and request.user.is_staff):
        user = request.user
    else:
        return render(request,'administrator/no-permissions.html')

    if request.method == 'POST':
        form = APIFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger = api.add_data(user, request.FILES['file'])
            context = {'summary': logger.summary()}
            status = 500 if logger.failed else 200
            status = 403 if logger.denied else status
            return render(request, 'administrator/apiresponse.html', context, status=status)
    else:
        form = APIFileForm()

    return render_to_response('administrator/upload.html', {'form': form}, context_instance=RequestContext(request))

# post import has to be csrf exempt in order to allow other servers to do POST requests
@csrf_exempt
def do_post_import(request):
    """
    Handles a POST import. Returns the summary of the API
    """

    user = doBasicHTTPAuth(request)
    if(user is None):
        return requestAuthResponse()
    else:
        logger = api.add_data_post(user, request.POST)
        context = {'summary': logger.summary()}
        status = 500 if logger.failed else 200
        status = 403 if logger.denied else status

        return render(request, 'administrator/apiresponse.html', context, status=status)

def do_xml_export(request, path):
    """
    Exports an XML file of the Thing in the url path.
    Checks if the user is currently logged in. If not, uses
    HTTP Basic Auth and Django to authorise the user. This
    should allow it to work from inside and outside the
    admin interface.
    """

    # double check to remove trailing slash
    path = re.sub('/$','',path)

    if request.user.is_authenticated():
        user = request.user
    else:
        user = doBasicHTTPAuth(request)

    if(user is None):
        return requestAuthResponse()
    else:
        if(userHasAccess(user,path)):
            # split up the path, assuming it is tripos/[tripos]/[part]/([subject])
            pathComponents = path.split('/')
            if(len(pathComponents) > 2):
                tripos = pathComponents[1]
                part = pathComponents[2]
                subject = pathComponents[3] if (len(pathComponents) == 4) else None
            else:
                return HttpResponse('<error>Unable to break down path (too many elements)</error>', status=400)

            # get the export xml
            try:
                result = api.output_xml_file(tripos, part, subject)
            except DataValidationException as err:
                # handle errors during xml export (eg bad data in our database
                # or the generated file didn't validate for whatever reason
                return HttpResponse('Error: {0}'.format(err), status=500)

            return HttpResponse(result, content_type="application/xml")
        else:
            # this will also be reported when the path does not exist
            return HttpResponse('<error>You (%s) do not have access to /%s</error>'% (user, path), status=403)

def doBasicHTTPAuth(request):
    """
    Performs a Django login from basic http auth credentials.
    Returns the user on success, or None on failure

    Based on http://djangosnippets.org/snippets/243/
    """
    # force https
    #if not request.is_secure():
    #    return None

    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                
                # do actual auth here (returns the user or None)
                return authenticate(username=uname, password=passwd)

def requestAuthResponse():
    """
    Returns an HttpResponse requesting API login credentials
    """

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % 'Timetable API'
    return response

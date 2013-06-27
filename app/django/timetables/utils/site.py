from django.contrib.sites.models import Site

def get_site_url_from_request(request):
    # Find out the http protocol
    http_protocol = "http://"
    if (request.is_secure()):
        http_protocol = "https://"

    domain = Site.objects.get_current().domain
    return http_protocol + domain

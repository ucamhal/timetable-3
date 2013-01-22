from django import shortcuts


def cookie_policy(request):
    return shortcuts.render(request, "cookie-policy.html")

def privacy_policy(request):
    return shortcuts.render(request, "privacy-policy.html")

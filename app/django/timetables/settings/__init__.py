import os
import warnings


# Detect using this settings package as a settings module. This is
# incorrect, one of the modules in this package should be specified instead.
if os.environ.get("DJANGO_SETTINGS_MODULE") == __name__:
    msg = (
        "It seems that you're using {0} as your DJANGO_SETTINGS_MODULE. "
        "This is almost certainly not right, as {0} is a package which "
        "contains settings modules, not a settings module itself. You "
        "probably need to export DJANGO_SETTINGS_MODULE to \"{0}.local\"."
        .format(__name__)
    )
    warnings.warn(msg, RuntimeWarning)

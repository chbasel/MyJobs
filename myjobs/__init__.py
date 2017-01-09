"""
myjobs
"""

import sys

__version_info__ = {
    'major': 0,
    'minor': 0,
    'micro': 2,
    'releaselevel': 'final',
    'serial': 1
}


def get_version():
    """
    Return the formatted version information
    """
    vers = ["%(major)i.%(minor)i" % __version_info__, ]

    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)

__version__ = get_version()


def hide_production_solr_from_tests():
    """
    This code here to protect production/staging systems from errant
    unit tests. Including this code as a PROJECT_APP __init__.py
    based on information found here:

    http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
    """
    import settings
    import default_settings

    settings.HAYSTACK_CONNECTIONS.clear()
    settings.HAYSTACK_CONNECTIONS.update(default_settings.TEST_HAYSTACK_CONNECTIONS)

if "test" in ''.join(sys.argv) or "jenkins" in sys.argv:
    hide_production_solr_from_tests()

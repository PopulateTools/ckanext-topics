# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.lib.search as search
import ckan.model as model

from ckan.common import c
from ckan.common import config

def reindex_packages_with_changed_topic(topic_or_subtopic_text):

    context = {
        'model': model,
        'session': model.Session,
        'user': c.user,
        'auth_user_obj': c.userobj
    }

    data_dict = {
        'q': topic_or_subtopic_text,
        'rows': 1000,
        'include_private': True
    }

    packages = t.get_action('package_search')(context, data_dict)['results']

    packages_names = map(lambda p: p['name'], packages)

    for package_name in packages_names:
        search.rebuild(package_name)


def user_is_admin(username):
    user = t.get_action('user_show')(context={}, data_dict={'id': username})

    if (user == None):
        return False

    return user['sysadmin']

def available_locales():
    return t.aslist(config.get('ckan.locales_offered', ['es', 'en', 'eu']))

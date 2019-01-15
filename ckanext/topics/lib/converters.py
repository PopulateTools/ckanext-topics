# encoding: utf-8

from six import string_types

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as t
import ckan.lib.navl.dictization_functions as df
import ckanext.topics.lib.validators as validators
import re

from ckan.common import _


def convert_to_custom_topic_tags(vocab):
    def callable(key, data, errors, context):
        received_tags = data.get(key)

        # HACK: instead of list, we get the string representation of the list
        received_tags = re.sub("^\[u'|'\]|',|u'", "", received_tags).split()

        print "[DEBUG] Received tags:" + str(received_tags)

        new_tags = []

        # try:
        if not type(received_tags) is list:
            received_tags = [received_tags]
        for tag_id in received_tags:
            tag_name = t.get_action('tag_show')({}, { 'id': tag_id, 'vocabulary_id': parsed_vocab(vocab) })['name']
            new_tags.append(tag_name)
        # except:
        #     new_tags = []

        print "[DEBUG] Tags for creation:" + str(new_tags)

        if not new_tags:
            new_tags = []
        if isinstance(new_tags, string_types):
            new_tags = [new_tags]

        # get current number of tags
        n = 0
        for k in data.keys():
            if k[0] == 'tags':
                n = max(n, k[1] + 1)

        v = model.Vocabulary.get(parsed_vocab(vocab))
        if not v:
            raise df.Invalid(_('Tag vocabulary "%s" does not exist') % parsed_vocab(vocab))
        context['vocabulary'] = v

        for num, tag in enumerate(new_tags):
            data[('tags', num + n, 'name')] = tag
            data[('tags', num + n, 'vocabulary_id')] = v.id
    return callable


def parsed_vocab(vocab):
    return re.sub("custom_topic\[\]", "custom_topics", vocab)

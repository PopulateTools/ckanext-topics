# encoding: utf-8

from six import string_types

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as t
import ckan.lib.navl.dictization_functions as df
import ckanext.topics.lib.validators as validators

from ckan.common import _

import logging
log = logging.getLogger(__name__)

def convert_to_custom_topic_tags(vocab):
    def callable(key, data, errors, context):
        log.info("convert_to_custom_topic_tags#callable with key: " + str(key) + ", vocab: " + vocab)

        tag_id = data.get(key)
        try:
            tag_name = t.get_action('tag_show')({}, { 'id': tag_id, 'vocabulary_id': vocab })['name']
            new_tags = [ tag_name ]
        except:
            new_tags = []

        log.info("New tags will be: " + str(new_tags))

        if not new_tags:
            return
        if isinstance(new_tags, string_types):
            new_tags = [new_tags]

        log.info("PuntoA")

        # get current number of tags
        n = 0
        for k in data.keys():
            if k[0] == 'tags':
                n = max(n, k[1] + 1)

        log.info("PuntoB")

        v = model.Vocabulary.get(vocab)
        if not v:
            raise df.Invalid(_('Tag vocabulary "%s" does not exist') % vocab)
        context['vocabulary'] = v

        log.info("PuntoC")

        # pete aqúi
        # for tag in new_tags:
        #     validators.topic_tag_in_vocabulary_validator(tag, context)

        log.info("PuntoD")

        for num, tag in enumerate(new_tags):
            data[('tags', num + n, 'name')] = tag
            data[('tags', num + n, 'vocabulary_id')] = v.id
    return callable
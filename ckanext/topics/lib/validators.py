# encoding: utf-8

import ckan.logic as logic

from itertools import count
import logging
log = logging.getLogger(__name__)

def topic_tag_in_vocabulary_validator(value, context):
    model = context['model']
    session = context['session']
    vocabulary = context.get('vocabulary')
    if vocabulary:
        query = session.query(model.Tag)\
            .filter(model.Tag.vocabulary_id==vocabulary.id)\
            .filter(model.Tag.name==value)\
            .count()
        if not query:
            raise Invalid(_('Tag %s does not belong to vocabulary %s') % (value, vocabulary.name))
    return value

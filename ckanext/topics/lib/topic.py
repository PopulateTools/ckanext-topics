# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.model as model
import ckan.lib.helpers as h

from ckan.model import Tag
from ckanext.topics.lib.alphabetic_index import AlphabeticIndex
from ckanext.topics.lib.tools import *


class Topic(object):

    @classmethod
    def find(cls, topic_id_or_name):
        topic_info = t.get_action('tag_show')(data_dict={ 'id': topic_id_or_name, 'vocabulary_id': cls.vocabulary_id(), 'include_datasets': False })
        topic_name = topic_info['name']
        topic = {
            'id': topic_info['id'],
            'index': cls.topic_index(topic_name),
            'name': topic_name,
            'display_name': cls.topic_display_name(topic_name),
            'vocabulary_id': topic_info['vocabulary_id']
        }

        return topic

    @classmethod
    def find_by_index(cls, index):
        for topic in cls.all():
            if (topic['index'] == index):
                return topic
        return None

    @classmethod
    def all(cls):
        topics = []

        for topic_name in cls.all_names():
            topic = cls.find(topic_name)
            topics.append(topic)

        return topics

    @classmethod
    def all_names(cls):
        try:
            tag_list = t.get_action('tag_list')
            return tag_list(data_dict={'vocabulary_id': 'custom_topics'})
        except t.ObjectNotFound:
            return []

    @classmethod
    def destroy(cls, context, topic_id_or_name):
        t.get_action('tag_delete')(context, { 'id': topic_id_or_name, 'vocabulary_id': Topic.vocabulary_id() })

    # @classmethod
    # def update_topic_index(cls, topic, new_index):
    #     new_name = new_index + '_' + topic['display_name']

    #     session = model.Session
    #     matched_tag = session.query(Tag).filter(Tag.id == topic['id']).first()
    #     matched_tag.name = new_name
    #     model.Session.commit()

    @classmethod
    def update_position(cls, topic_id, new_position):
        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.id == topic_id).first()
        matched_tag.name = str(new_position)
        model.Session.commit()

    @classmethod
    def update_name(cls, topic_id, name_translations={}):
        for locale in available_locales():
            t.get_action('term_translation_update')({}, {
                'term': topic_id,
                'term_translation': name_translations[locale],
                'lang_code': locale
            })


    @classmethod
    def vocabulary_id(cls):
        vocabulary = t.get_action('vocabulary_show')(data_dict={'id': 'custom_topics'})
        return vocabulary['id']

    @classmethod
    def topic_index(cls, topic_name):
        splitted_name = topic_name.split('_')
        return splitted_name[0]

    @classmethod
    def topic_display_name(cls, topic_name):
        splitted_name = topic_name.split('_')
        return splitted_name[len(splitted_name) - 1]

    @classmethod
    def get_new_topic_index(cls):
        topics = cls.all()

        if (len(topics) == 0):
            return '0'

        last_free_position = 0
        for topic in topics:
            last_free_position = max(last_free_position, int(topic['name']))

        return str(last_free_position + 1)

    @classmethod
    def count(cls):
        return len(cls.all_names())

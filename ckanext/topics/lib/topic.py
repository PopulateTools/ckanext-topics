# -*- coding: utf-8 -*-

import re

import ckan.plugins.toolkit as t
import ckan.model as model
import ckan.lib.helpers as h

from ckan.model import Tag
from ckanext.topics.lib.tools import *
from sqlalchemy.exc import IntegrityError


class TopicPositionDuplicated(Exception):
    pass


class Topic(object):

    @classmethod
    def find(cls, topic_id_or_name):
        topic_info = t.get_action('tag_show')(data_dict={ 'id': topic_id_or_name, 'vocabulary_id': cls.vocabulary_id(), 'include_datasets': False })

        # BUG: for some reason CKAN returns tags from other vocabularies
        if (topic_info['vocabulary_id'] != cls.vocabulary_id()):
            raise t.ObjectNotFound

        topic_name = topic_info['name']
        topic = {
            'id': topic_info['id'],
            'name': topic_name,
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

    @classmethod
    def update_position(cls, topic_id, new_position):
        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.id == topic_id).first()
        matched_tag.name = str(new_position)
        try:
            model.Session.commit()
        except IntegrityError as e:
            raise TopicPositionDuplicated

    @classmethod
    def update_name(cls, topic_id, name_translations={}):
        for locale in available_locales():
            if name_translations[locale]:
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
    def get_new_topic_index(cls):
        topics = cls.all()

        if (len(topics) == 0):
            return 0

        last_free_position = 0
        for topic in topics:
            last_free_position = max(
                last_free_position,
                Topic.parse_tag_dict(topic)['position']
            )

        return last_free_position + 1

    @classmethod
    def count(cls):
        return len(cls.all_names())

    @classmethod
    def build_tag_name(cls, position):
        return 'custom_topic_' + str(position)

    @classmethod
    def build_tag_dict(cls, position):
        return {
            'name': cls.build_tag_name(position),
            'vocabulary_id': cls.vocabulary_id()
        }

    @classmethod
    def parse_tag_dict(cls, tag_dict):
        tag_dict['position'] = int(re.sub('custom_topic_', '', tag_dict['name']))

        return tag_dict

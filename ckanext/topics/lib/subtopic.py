# -*- coding: utf-8 -*-

import re

import ckan.plugins.toolkit as t
import ckan.model as model

from ckan.model import Tag

from ckanext.topics.lib.topic import Topic
from sqlalchemy.exc import IntegrityError


class Subtopic(object):

    @classmethod
    def find(cls, subtopic_id_or_name):
        subtopic_info = t.get_action('tag_show')(data_dict={ 'id': subtopic_id_or_name, 'vocabulary_id': cls.vocabulary_id(), 'include_datasets': False })

        # BUG: for some reason CKAN returns tags from other vocabularies
        if (subtopic_info['vocabulary_id'] != cls.vocabulary_id()):
            raise t.ObjectNotFound

        subtopic_name = subtopic_info['name']
        subtopic = {
            'id': subtopic_info['id'],
            'name': subtopic_name,
            'vocabulary_id': subtopic_info['vocabulary_id']
        }
        return subtopic

    @classmethod
    def all(cls):
        subtopics = []

        for subtopic_name in cls.all_names():
            subtopic = cls.find(subtopic_name)
            subtopics.append(subtopic)

        return subtopics

    @classmethod
    def all_names(cls):
        try:
            return t.get_action('tag_list')(data_dict={'vocabulary_id': 'custom_subtopics'})
        except t.ObjectNotFound:
            return []

    @classmethod
    def by_topic(cls, topic_id):
        topic = Topic.find(topic_id)
        subtopics = []

        for raw_subtopic in cls.all():
            if (cls.parse_tag_dict(raw_subtopic)['parent_id'] == topic['id']):
                subtopics.append(raw_subtopic)

        return subtopics

    @classmethod
    def destroy(cls, context, subtopic_id_or_name):
        t.get_action('tag_delete')(context, { 'id': subtopic_id_or_name, 'vocabulary_id': cls.vocabulary_id() })

        # TODO: reindex facets and datasets with this subtopic

    @classmethod
    def update_position(cls, subtopic_id, parent_id, new_position):
        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.id == subtopic_id).first()
        matched_tag.name = str(new_position) + '_' + parent_id
        try:
            model.Session.commit()
        except IntegrityError as e:
            raise TopicPositionDuplicated

    @classmethod
    def get_free_position(cls, topic_id):
        subtopics = cls.by_topic(topic_id)

        if (len(subtopics) == 0):
            return '0'

        last_free_position = 0
        for subtopic in subtopics:
            subtopic_position = Subtopic.parse_tag_dict(subtopic)['position']
            last_free_position = max(last_free_position, subtopic_position)

        return str(last_free_position + 1)

    @classmethod
    def vocabulary_id(cls):
        vocabulary = t.get_action('vocabulary_show')(data_dict={'id': 'custom_subtopics'})
        return vocabulary['id']

    @classmethod
    def build_tag_name(cls, position, parent_id):
        return 'custom_subtopic_' + str(position) + '_' + str(parent_id)

    @classmethod
    def build_tag_dict(cls, position, parent_id):
        return {
            'name': cls.build_tag_name(position, parent_id),
            'vocabulary_id': cls.vocabulary_id()
        }

    @classmethod
    def parse_tag_dict(cls, tag_dict):
        attrs = re.sub('custom_subtopic_', '', tag_dict['name']).split('_')

        tag_dict['position'] = int(attrs[0])
        tag_dict['parent_id'] = attrs[1]

        return tag_dict

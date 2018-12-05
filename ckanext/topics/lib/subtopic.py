# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.model as model

from ckan.model import Tag

from ckanext.topics.lib.topic import Topic
from ckanext.topics.lib.alphabetic_index import AlphabeticIndex
from ckanext.topics.lib.subtopic_decorator import SubtopicDecorator


class Subtopic(object):

    @classmethod
    def find(cls, subtopic_id_or_name):
        subtopic_info = t.get_action('tag_show')(data_dict={ 'id': subtopic_id_or_name, 'vocabulary_id': cls.vocabulary_id(), 'include_datasets': False })
        subtopic_name = subtopic_info['name']
        subtopic = {
            'id': subtopic_info['id'],
            'name': subtopic_name,
            'display_name': cls.subtopic_display_name(subtopic_name),
            'vocabulary_id': subtopic_info['vocabulary_id'],
            'index': cls.subtopic_index(subtopic_name),
            'topic_id': cls.subtopic_topic_id(subtopic_name)
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
            subtopic = SubtopicDecorator(raw_subtopic)
            if (subtopic.parent_id == topic['id']):
                subtopics.append(raw_subtopic)

        return subtopics

    @classmethod
    def destroy(cls, context, subtopic_id_or_name):
        t.get_action('tag_delete')(context, { 'id': subtopic_id_or_name, 'vocabulary_id': cls.vocabulary_id() })

        # TODO: reindex facets and datasets with this subtopic

    # @classmethod
    # def update_subtopic_index(cls, subtopic, new_index):
    #     topic = Topic.find(subtopic['topic_id'])

    #     new_name = topic['index'] + '_' + new_index + '_' + subtopic['display_name']

    #     session = model.Session
    #     matched_tag = session.query(Tag).filter(Tag.name == subtopic['name']).first()
    #     matched_tag.name = new_name
    #     model.Session.commit()

        # TODO: reindex facets and datasets with this subtopic

    @classmethod
    def update_position(cls, subtopic_id, parent_id, new_position):
        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.id == subtopic_id).first()
        matched_tag.name = str(new_position) + '_' + parent_id
        model.Session.commit()

    @classmethod
    def update_subtopic_topic_index(cls, subtopic, new_topic_index):
        topic = Topic.find(subtopic['topic_id'])

        new_name = new_topic_index + '_' + subtopic['index'] + '_' + subtopic['display_name']

        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.name == subtopic['name']).first()
        matched_tag.name = new_name
        model.Session.commit()

        # TODO: reindex facets and datasets with this subtopic

    @classmethod
    def get_free_position(cls, topic_id):
        subtopics = cls.by_topic(topic_id)

        if (len(subtopics) == 0):
            return '0'

        last_free_position = 0
        for subtopic in subtopics:
            subtopic_position = int(subtopic['name'].split('_')[0])
            last_free_position = max(last_free_position, subtopic_position)

        return str(last_free_position + 1)

    @classmethod
    def vocabulary_id(cls):
        vocabulary = t.get_action('vocabulary_show')(data_dict={'id': 'custom_subtopics'})
        return vocabulary['id']

    @classmethod
    def subtopic_topic_index(cls, subtopic_name):
        splitted_name = subtopic_name.split('_')
        return splitted_name[0]

    @classmethod
    def subtopic_topic_id(cls, subtopic_name):
        topic_index = cls.subtopic_topic_index(subtopic_name)
        topic = Topic.find_by_index(topic_index)
        if topic:
            return topic['id']

    @classmethod
    def subtopic_index(cls, subtopic_name):
        splitted_name = subtopic_name.split('_')
        return splitted_name[1]

    @classmethod
    def subtopic_display_name(cls, subtopic_name):
        splitted_name = subtopic_name.split('_')
        return splitted_name[len(splitted_name) - 1]

    # @classmethod
    # def get_new_subtopic_index(cls, topic_id_or_name):
    #     topic_subtopics = cls.by_topic(topic_id_or_name)

    #     if (len(topic_subtopics) == 0):
    #         return AlphabeticIndex.first_letter()

    #     biggest_letter_idx = ' ' # All lowercase letters are 'bigger' than blankspace

    #     for subtopic in topic_subtopics:
    #         biggest_letter_idx = max(biggest_letter_idx, subtopic['index'])

    #     return AlphabeticIndex.next_letter(biggest_letter_idx)

    @classmethod
    def topic_subtopics_count(cls, topic_id_or_name):
        return len(cls.by_topic(topic_id_or_name))

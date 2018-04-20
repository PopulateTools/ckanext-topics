# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

import dateutil.parser as date_parser

from ckan.common import c
from ckanext.topics.lib.topic import Topic
from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.tools import user_is_admin
from collections import OrderedDict


def current_user_is_admin():
    return user_is_admin(c.user)


def custom_topics():
    return Topic.all()


def custom_subtopics():
    return Subtopic.all()


def topic_display_name(topic_name):
    # same behavior for subtopic
    return Topic.topic_display_name(topic_name)


def get_topic_name(topic_id):
    topic = Topic.find(topic_id)
    if (topic != None):
        return topic['display_name']


class TopicsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    ## IDatasetForm

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(TopicsPlugin, self).create_package_schema()

        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(TopicsPlugin, self).update_package_schema()

        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(TopicsPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        # Add our custom country_code metadata field to the schema.
        schema.update({
            'custom_topic': [
                toolkit.get_converter('convert_from_tags')('custom_topics'),
                toolkit.get_validator('ignore_missing')
            ],
            'custom_subtopic': [
                toolkit.get_converter('convert_from_tags')('custom_subtopics'),
                toolkit.get_validator('ignore_missing')
            ]
        })

        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_resource('fanstatic', 'topics')

    ## ITemplateHelpers

    def get_helpers(self):
        return {
            'get_topic_name': get_topic_name,
            'custom_topics': custom_topics,
            'custom_subtopics': custom_subtopics,
            'topic_display_name': topic_display_name,
            'current_user_is_admin': current_user_is_admin
        }

    ## IFacets

    def dataset_facets(self, facets_dict, package_type):
        return OrderedDict([
            ('vocab_custom_topics', 'Topics'),
            ('vocab_custom_subtopics', 'Subtopics'),
            ('tags', toolkit._('Tags')),
            ('res_format', toolkit._('Formats')),
            ('organization', toolkit._('Organizations'))
        ])

    ## IRoutes

    def after_map(self, map):
        topic_controller = 'ckanext.topics.controllers.topic:TopicController'

        map.connect('topic_index', '/topic', controller=topic_controller, action='index')
        map.connect('topic_new', '/topic/new', controller=topic_controller, action='new')
        map.connect('topic_update', '/topic/update', controller=topic_controller, action='update')
        map.connect('topic_edit', '/topic/edit', controller=topic_controller, action='edit')
        map.connect('topic_create', '/topic/create', controller=topic_controller, action='create')
        map.connect('topic_destroy', '/topic/destroy', controller=topic_controller, action='destroy')

        subtopic_controller = 'ckanext.topics.controllers.subtopic:SubtopicController'

        map.connect('subtopic_new', '/subtopic/new', controller=subtopic_controller, action='new')
        map.connect('subtopic_update', '/subtopic/update', controller=subtopic_controller, action='update')
        map.connect('subtopic_edit', '/subtopic/edit', controller=subtopic_controller, action='edit')
        map.connect('subtopic_create', '/subtopic/create', controller=subtopic_controller, action='create')
        map.connect('subtopic_destroy', '/subtopic/destroy', controller=subtopic_controller, action='destroy')

        return map

    ## Others

    def _modify_package_schema(self, schema):
        schema.update({
            'custom_topic': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('custom_topics')
            ],
            'custom_subtopic': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('custom_subtopics')
            ]
        })
        return schema
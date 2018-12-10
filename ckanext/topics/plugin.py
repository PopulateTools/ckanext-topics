# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

import ckan.plugins as p
import ckan.plugins.toolkit as t
import ckan.model as model

import dateutil.parser as date_parser

from ckan.common import c
from ckanext.topics.lib.topic import Topic
from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.topic_decorator import TopicDecorator
from ckanext.topics.lib.topic_decorator import SubtopicDecorator
from ckanext.topics.lib.tools import user_is_admin
from ckanext.topics.lib.tools import available_locales
from ckanext.topics.lib.converters import convert_to_custom_topic_tags
from collections import OrderedDict

import ckan as ckan
import ckan.logic as logic
import ckan.lib.dictization.model_save as model_save
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.helpers as h

_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access


def current_user_is_admin():
    return user_is_admin(c.user)


def custom_topics():
    collection = []
    for topic in Topic.all():
        collection.append(TopicDecorator(topic))

    return collection


def custom_subtopics():
    collection = []
    for subtopic in Subtopic.all():
        collection.append(SubtopicDecorator(subtopic))

    return collection


def topic_subtopics(topic_id):
    topic_subtopics = []
    for subtopic in Subtopic.by_topic(topic_id):
        topic_subtopics.append(SubtopicDecorator(subtopic))

    return topic_subtopics


# Tags arrive with the id replaced per the corresponding term translation
def topic_name_from_tags(tags):
    return topic_id_from_tags(tags)


# Tags arrive with the id replaced per the corresponding term translation
def subtopic_name_from_tags(tags):
    return subtopic_id_from_tags(tags)


def topic_id_from_tags(tags):
    for tag in tags:
        if (tag['vocabulary_id'] == Topic.vocabulary_id()):
            return tag['id']

    return None


def subtopic_id_from_tags(tags):
    for tag in tags:
        if (tag['vocabulary_id'] == Subtopic.vocabulary_id()):
            return tag['id']

    return None


def topic_name_from_facet_item(facet_item):
    tag = logic.get_action('tag_show')({}, { 'id': facet_item['name'], 'vocabulary_id': Topic.vocabulary_id() })
    topic = Topic.find(tag['id'])

    return TopicDecorator(topic).name


def subtopic_name_from_facet_item(facet_item):
    tag = logic.get_action('tag_show')({}, { 'id': facet_item['name'], 'vocabulary_id': Subtopic.vocabulary_id() })
    subtopic = Subtopic.find(tag['id'])

    return SubtopicDecorator(subtopic).name


def topic_create(context, data_dict):
    model = context['model']

    _check_access('tag_create', context, data_dict)

    schema = context.get('schema') or \
        ckan.logic.schema.default_create_tag_schema()
    data, errors = _validate(data_dict, schema, context)
    # if errors:
    #     raise ValidationError(errors)

    tag = model_save.tag_dict_save(data_dict, context)

    if not context.get('defer_commit'):
        model.repo.commit()

    log.debug("Created tag '%s' " % tag)

    return model_dictize.tag_dictize(tag, context)


def extract_term_translation(term_translations, locale):
    for term_translation in term_translations:
        if locale == term_translation['lang_code']:
            return term_translation['term_translation']

    # fallback
    if len(term_translations) > 0:
        return term_translations[0]['term_translation']


def subtopic_parent_name(subtopic_decorator):
    topic_id = subtopic_decorator.parent_id
    topic = TopicDecorator(Topic.find(topic_id))
    return topic.name


# Accepts facet name as argument, if it corresponds with a topic or subtopic returns
# its name. Otherwise returns None
def topic_facet_name(tag_id):
    topic = Topic.find(tag_id)

    if topic:
        return TopicDecorator(topic).name

    subtopic = Subtopic.find(tag_id)

    if subtopic:
        return SubtopicDecorator(subtopic).name

    return None


class TopicsPlugin(p.SingletonPlugin, t.DefaultDatasetForm):

    p.implements(p.IDatasetForm)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IValidators)

    ## IActions
    def get_actions(self):
        return {
            'topic_create': topic_create
        }

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
        schema['tags']['__extras'].append(t.get_converter('free_tags_only'))

        # Add our custom country_code metadata field to the schema.
        schema.update({
            'custom_topic': [
                t.get_converter('convert_from_tags')('custom_topics'),
                t.get_validator('ignore_missing')
            ],
            'custom_subtopic': [
                t.get_converter('convert_from_tags')('custom_subtopics'),
                t.get_validator('ignore_missing')
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
        t.add_template_directory(config_, 'templates')
        t.add_resource('fanstatic', 'topics')

    ## ITemplateHelpers

    def get_helpers(self):
        return {
            'custom_topics': custom_topics,
            'custom_subtopics': custom_subtopics,
            'topic_subtopics': topic_subtopics,
            'topic_facet_name': topic_facet_name,
            'current_user_is_admin': current_user_is_admin,
            'extract_term_translation': extract_term_translation,
            'subtopic_parent_name': subtopic_parent_name,
            'available_locales': available_locales,
            'topic_id_from_tags': topic_id_from_tags,
            'subtopic_id_from_tags': subtopic_id_from_tags,
            'topic_name_from_tags': topic_name_from_tags,
            'subtopic_name_from_tags': subtopic_name_from_tags,
            'topic_name_from_facet_item': topic_name_from_facet_item,
            'subtopic_name_from_facet_item': subtopic_name_from_facet_item
        }

    ## IFacets

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['vocab_custom_topics'] = t._('Topics')
        facets_dict['vocab_custom_subtopics'] = t._('Subtopics')

        return facets_dict


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

    ## IValidators

    def get_validators(self):
        return {
            'convert_to_custom_topic_tags': convert_to_custom_topic_tags
        }

    ## Others

    def _modify_package_schema(self, schema):
        schema.update({
            'custom_topic': [
                t.get_validator('ignore_missing'),
                t.get_converter('convert_to_tags')('custom_topics')
            ],
            'custom_subtopic': [
                t.get_validator('ignore_missing'),
                t.get_converter('convert_to_tags')('custom_subtopics')
            ]
        })
        return schema

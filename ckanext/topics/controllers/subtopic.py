# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.model as model
import ckan.lib.base as base

from ckan.model import Tag
from ckan.common import _

from ckanext.topics.lib.topic import Topic
from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.tools import *
from ckanext.topics.lib.alphabetic_index import AlphabeticIndex


class SubtopicController(t.BaseController):

    def __before__(self, action, **env):
        super(SubtopicController, self).__before__(action, **env)
        current_username = t.c.user

        if (current_username == None) or not user_is_admin(current_username):
            base.abort(403, _('Not authorized to see this page'))

    def new(self):
        topic_id = t.request.params['topic_id']
        topic    = Topic.find(topic_id)

        extra_vars = {
            'subtopic': { 'topic_id': topic_id },
            'controller_action': 'create'
        }

        return t.render('subtopic/edit.html', extra_vars=extra_vars)

    def create(self):
        context = { 'user': t.c.user }

        params = t.request.params
        topic_id = params['subtopic_topic_id']
        display_name = params['subtopic_display_name']

        if (Subtopic.topic_subtopics_count(topic_id) >= AlphabeticIndex.max_items()):
            t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

        topic = Topic.find(topic_id)

        subtopic_index = Subtopic.get_new_subtopic_index(topic_id)

        name = topic['index'] + '_' + subtopic_index + '_' + display_name

        result = t.get_action('tag_create')(context, { 'name': name, 'vocabulary_id': Subtopic.vocabulary_id() })

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def edit(self):
        subtopic_id = t.request.params['id']
        subtopic = Subtopic.find(subtopic_id)

        extra_vars = {
            'subtopic': subtopic,
            'controller_action': 'update'
        }

        return t.render('subtopic/edit.html', extra_vars=extra_vars)

    def update(self):
        params = t.request.params

        topic_id = params['subtopic_topic_id']
        topic = Topic.find(topic_id)

        subtopic_id = params['subtopic_id']
        subtopic = Subtopic.find(subtopic_id)

        old_name = subtopic['name']
        new_index = params['subtopic_index']
        new_name = topic['index'] + '_' + new_index + '_' + params['subtopic_display_name']

        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.name == subtopic['name']).first()
        matched_tag.name = new_name
        model.Session.commit()

        reindex_packages_with_changed_topic(old_name)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def destroy(self):
        context = { 'user': t.c.user }

        params = t.request.params

        subtopic_id = t.request.params['id']
        subtopic    = Subtopic.find(subtopic_id)

        old_name = subtopic['name']

        Subtopic.destroy(context, subtopic_id)

        # Update indexes of following subtopics
        destroyed_index = subtopic['index']
        for subtopic in Subtopic.all():
            if subtopic['index'] > destroyed_index:
                new_subtopic_index = AlphabeticIndex.previous_letter(subtopic['index'])
                Subtopic.update_subtopic_index(subtopic, new_subtopic_index)

        reindex_packages_with_changed_topic(old_name)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')
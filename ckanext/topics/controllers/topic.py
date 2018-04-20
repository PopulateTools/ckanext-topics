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


class TopicController(t.BaseController):

    def __before__(self, action, **env):
        super(TopicController, self).__before__(action, **env)

        current_username = env['environ']['REMOTE_USER']

        if (current_username == None) or not user_is_admin(current_username):
            base.abort(403, _('Not authorized to see this page'))

    def index(self):
        topics = Topic.all()
        subtopics = Subtopic.all()

        for topic in topics:
            topic['subtopics'] = []
            for subtopic in subtopics:
                if (topic['id'] == subtopic['topic_id']):
                   topic['subtopics'].append(subtopic)

        extra_vars = { 'topics': topics }

        return t.render('topic/index.html', extra_vars=extra_vars)

    def new(self):
        extra_vars = { 'topic': {}, 'controller_action': 'create' }

        return t.render('topic/edit.html', extra_vars=extra_vars)

    def create(self):
        context = { 'user': t.c.user }

        if (Topic.count() >= AlphabeticIndex.max_items()):
            t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

        display_name = t.request.params['topic_display_name']
        full_name = str(Topic.get_new_topic_index()) + '_' + display_name

        t.get_action('tag_create')(context, { 'name': full_name, 'vocabulary_id': Topic.vocabulary_id() })

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def edit(self):
        topic_id = t.request.params['id']
        topic    = Topic.find(topic_id)

        extra_vars = {
            'topic': topic,
            'subtopics': Subtopic.by_topic(topic_id),
            'controller_action': 'update'
        }

        return t.render('topic/edit.html', extra_vars=extra_vars)

    def update(self):
        params = t.request.params
        topic_id = params['topic_id']
        topic    = Topic.find(topic_id)

        old_index = topic['index']
        new_index = params['topic_index']
        old_topic_name = topic['name']
        new_name  = new_index + '_' + params['topic_display_name']

        if (old_index != new_index):
            subtopics = Subtopic.by_topic(topic_id)
            for subtopic in subtopics:
                Subtopic.update_subtopic_topic_index(subtopic, new_index)

        session = model.Session
        matched_tag = session.query(Tag).filter(Tag.id == topic['id']).first()
        matched_tag.name = new_name
        model.Session.commit()

        reindex_packages_with_changed_topic(old_topic_name)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def destroy(self):
        context = { 'user': t.c.user }

        topic_id = t.request.params['id']
        topic    = Topic.find(topic_id)

        old_topic_name = topic['name']

        # destroy topic and related subtopics
        for subtopic in Subtopic.by_topic(topic['id']):
            Subtopic.destroy(context, subtopic['id'])

        Topic.destroy(context, topic['id'])

        destroyed_index = topic['index']

        # update indexes of following topics and subtopics
        for topic in Topic.all():
            if topic['index'] > destroyed_index:
                topic_subtopics = Subtopic.by_topic(topic['id'])

                # decrement topic index
                new_topic_index = AlphabeticIndex.previous_letter(topic['index'])
                Topic.update_topic_index(topic, new_topic_index)

                # decrement subtopics topic index
                for subtopic in topic_subtopics:
                    Subtopic.update_subtopic_topic_index(subtopic, new_topic_index)

        reindex_packages_with_changed_topic(old_topic_name)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')
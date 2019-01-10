# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h

from ckan.model import Tag
from ckan.common import _, c, json

from ckanext.topics.lib.topic import Topic, TopicPositionDuplicated
from ckanext.topics.lib.topic_decorator import TopicDecorator
from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.tools import *


class TopicController(t.BaseController):

    def __before__(self, action, **env):
        super(TopicController, self).__before__(action, **env)

        current_username = env['environ']['REMOTE_USER']

        if (current_username == None) or not user_is_admin(current_username):
            base.abort(403, _('Not authorized to see this page'))

    def index(self):
        topics = []
        subtopics = Subtopic.all()

        for raw_topic in Topic.all():
            topic = TopicDecorator(raw_topic)
            topic.load_subtopics(sorted=True)
            topics.append(topic)

        topics.sort(key=lambda topic: topic.position)

        extra_vars = { 'topics': topics }

        return t.render('topic/index.html', extra_vars=extra_vars)

    def new(self):
        topic = TopicDecorator({ 'position': Topic.get_new_topic_index() })
        extra_vars = { 'topic': topic, 'controller_action': 'create' }

        return t.render('topic/edit.html', extra_vars=extra_vars)

    def create(self):
        params = t.request.params
        context = { 'user': t.c.user }
        position = params['topic_position']
        error = None

        # create topic
        try:
            tag = t.get_action('topic_create')(context, Topic.build_tag_dict(position))
            names = {}
            for locale in available_locales():
                names[locale] = params['topic_name_' + locale]

            Topic.update_name(tag['id'], names)
        except TopicPositionDuplicated as e:
            error = _('Position is already taken')

        if error:
            h.flash_error(error)
        else:
            h.flash_success(_('Topic created successfully'))


        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def edit(self):
        topic_id = t.request.params['id']
        topic    = TopicDecorator(Topic.find(topic_id))

        extra_vars = { 'topic': topic, 'controller_action': 'update' }

        return t.render('topic/edit.html', extra_vars=extra_vars)

    def update(self):
        params = t.request.params
        topic = TopicDecorator(Topic.find(params['topic_id']))
        topic_old_name = topic.tag_name
        error = None

        # update topic
        names = {}
        for locale in available_locales():
                names[locale] = params['topic_name_' + locale]

        Topic.update_name(topic.id, names)

        try:
            Topic.update_position(topic.id, params['topic_position'])
            reindex_packages_with_changed_topic(topic_old_name)
        except TopicPositionDuplicated as e:
            error = _('Position is already taken')

        if error:
            h.flash_error(error)
        else:
            h.flash_success(_('Topic updated successfully'))

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='edit', id=topic.id)

    def destroy(self):
        context = { 'user': t.c.user }

        topic_id = t.request.params['id']
        topic = TopicDecorator(Topic.find(topic_id))
        topic_old_name = topic.tag_name
        destroyed_position = topic.position

        # destroy topic and related subtopics
        for subtopic in Subtopic.by_topic(topic.id):
            Subtopic.destroy(context, subtopic['id'])

        Topic.destroy(context, topic.id)
        reindex_packages_with_changed_topic(topic_old_name)

        # TODO: destroy term translations (no API available)

        # update indexes of following topics
        for topic in Topic.all():
            topic = TopicDecorator(topic)

            if int(topic.position) > int(destroyed_position):
                new_topic_position = int(topic.position) - 1
                Topic.update_position(topic.id, new_topic_position)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

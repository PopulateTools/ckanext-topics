# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h

from ckan.model import Tag
from ckan.common import _

from ckanext.topics.lib.topic import Topic, TopicPositionDuplicated
from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.tools import *
from ckanext.topics.lib.alphabetic_index import AlphabeticIndex
from ckanext.topics.lib.subtopic_decorator import SubtopicDecorator

from sqlalchemy.exc import IntegrityError


class SubtopicController(t.BaseController):

    def __before__(self, action, **env):
        super(SubtopicController, self).__before__(action, **env)
        current_username = t.c.user

        if (current_username == None) or not user_is_admin(current_username):
            base.abort(403, _('Not authorized to see this page'))

    def new(self):
        topic_id = t.request.params['topic_id']
        topic    = Topic.find(topic_id)

        subtopic = SubtopicDecorator({ 'parent_id': topic['id'], 'position': Subtopic.get_free_position(topic_id) })
        extra_vars = { 'subtopic': subtopic, 'controller_action': 'create' }

        return t.render('subtopic/edit.html', extra_vars=extra_vars)

    def create(self):
        context = { 'user': t.c.user }
        params = t.request.params
        error = None

        topic_id = params['subtopic_parent_id']
        topic = Topic.find(topic_id)

        # create tag
        try:
            tag = t.get_action('topic_create')(
                context,
                Subtopic.build_tag_dict(params['subtopic_position'], topic['id'])
            )

            # create name translations
            for locale in available_locales():
                term_translation = params['subtopic_name_' + locale]
                if term_translation:
                    t.get_action('term_translation_update')({}, {
                        'term': tag['id'],
                        'term_translation': term_translation,
                        'lang_code': locale
                    })
        except TopicPositionDuplicated as e:
            error = _('Position is already taken')

        if error:
            h.flash_error(error)
        else:
            h.flash_success(_('Subtopic created successfully'))

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def edit(self):
        subtopic_id = t.request.params['id']
        subtopic = SubtopicDecorator(Subtopic.find(subtopic_id))

        extra_vars = {
            'subtopic': subtopic,
            'controller_action': 'update'
        }

        return t.render('subtopic/edit.html', extra_vars=extra_vars)

    def update(self):
        params = t.request.params
        error = None

        topic_id = params['subtopic_parent_id']
        topic = Topic.find(topic_id)

        subtopic_id = params['subtopic_id']
        subtopic = SubtopicDecorator(Subtopic.find(subtopic_id))
        subtopic_old_name = subtopic.tag_name

        # update record
        for locale in available_locales():
            term_translation = params['subtopic_name_' + locale]
            if term_translation:
                t.get_action('term_translation_update')({}, {
                    'term': subtopic.id,
                    'term_translation': params['subtopic_name_' + locale],
                    'lang_code': locale
                })
        try:
            Subtopic.update_position(subtopic.id, subtopic.parent_id, params['subtopic_position'])
            reindex_packages_with_changed_topic(subtopic_old_name)
        except IntegrityError as e:
            error = _('Position is already taken')

        if error:
            h.flash_error(error)
        else:
            h.flash_success(_('Subtopic updated successfully'))

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

    def destroy(self):
        context = { 'user': t.c.user }
        params = t.request.params

        subtopic_id = t.request.params['id']
        subtopic = SubtopicDecorator(Subtopic.find(subtopic_id))
        subtopic_old_name = subtopic.tag_name

        Subtopic.destroy(context, subtopic_id)
        reindex_packages_with_changed_topic(subtopic_old_name)

        # update positions of following subtopics
        destroyed_position = int(subtopic.position)
        for subtopic in Subtopic.by_topic(subtopic.parent_id):
            subtopic = SubtopicDecorator(subtopic)
            subtopic_pos = int(subtopic.position)
            if subtopic_pos > destroyed_position:
                new_position = subtopic_pos - 1
                Subtopic.update_position(subtopic.id, subtopic.parent_id, new_position)

        t.redirect_to(controller='ckanext.topics.controllers.topic:TopicController', action='index')

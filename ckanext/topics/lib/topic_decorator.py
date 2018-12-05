# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.lib.helpers as h

from ckanext.topics.lib.subtopic import Subtopic
from ckanext.topics.lib.subtopic_decorator import SubtopicDecorator


class TopicDecorator(object):

    def __init__(self, topic_dict):
        if 'id' in topic_dict:
            self.id = topic_dict['id']
            self.search_results_url = h.url_for(controller='package', action='search', vocab_custom_topics=self.id)
        else:
            self.id = None
            self.search_results_url = None

        if self.id:
            self.name_term_translations = t.get_action('term_translation_show')({}, { 'terms': [self.id] })
        else:
            self.name_term_translations = []

        self.name = None
        for term_translation in self.name_term_translations:
            if h.lang() == term_translation['lang_code']:
                self.name = term_translation['term_translation']
        if self.name == None and len(self.name_term_translations) > 0:
            self.name = self.name_term_translations[0]['term_translation']

        self.subtopics = []

        if 'name' in topic_dict:
            self.position = topic_dict['name']
        if 'position' in topic_dict:
            self.position = topic_dict['position']

    # must be called explicitly to avoid performance problems
    def load_subtopics(self):
        self.subtopics = [] # ensure not loading twice
        for subtopic in Subtopic.by_topic(self.id):
            self.subtopics.append(SubtopicDecorator(subtopic))


    def to_s(self):
        return "[TopicDecorator] id: " + self.id + " name: " + self.name + " subtopics_count: " + str(len(self.subtopics))

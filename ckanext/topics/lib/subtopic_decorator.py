# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as t
import ckan.lib.helpers as h

from ckanext.topics.lib.subtopic import Subtopic


class SubtopicDecorator(object):

    def __init__(self, subtopic_dict):
        if 'id' in subtopic_dict:
            self.id = subtopic_dict['id']
        else:
            self.id = None

        if 'name' in subtopic_dict:
            self.search_results_url = h.url_for(controller='package', action='search', vocab_custom_subtopics=subtopic_dict['name'])
        else:
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

        # position and parent_id are stored in the same attribute
        if 'name' in subtopic_dict:
            attrs = Subtopic.parse_tag_dict(subtopic_dict)
            self.position = attrs['position']
            self.parent_id = attrs['parent_id']
        else:
            self.position = None
            self.parent_id = None

        # for initializing new records
        if 'parent_id' in subtopic_dict:
            self.parent_id = subtopic_dict['parent_id']
        if 'position' in subtopic_dict:
            self.position = int(subtopic_dict['position'])

        if self.position and self.parent_id:
            self.tag_name = Subtopic.build_tag_name(self.position, self.parent_id)
        else:
            self.tag_name = None

    def to_s(self):
        return "[SubopicDecorator] id: " + str(self.id) + " name: " + str(self.name) + " parent_id: " + str(self.parent_id) + " position: " + str(self.position)

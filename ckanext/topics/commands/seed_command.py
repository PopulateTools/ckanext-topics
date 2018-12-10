# encoding: utf-8

import sys

import ckan.logic as logic
import ckan.plugins.toolkit as t

from ckan.lib.cli import CkanCommand
from ckanext.topics.lib.topic import Topic
from ckanext.topics.lib.subtopic import Subtopic


class SeedCommand(CkanCommand):
    '''Tasks related to users.
    Usage:
        seed_command create_tag_vocabularies
            Creates necessary tag vocabularies
        seed_command create_sample_topics
            Creates a sample hierarchy of topics and subtopics

    The commands should be run from the ckanext-topics directory and expect
    a development.ini file to be present. Most of the time you will
    specify the config explicitly though::
        paster --plugin=ckanext-topics seed_command create_tag_vocabularies -c /etc/ckan/default/<config_file>.ini
        paster --plugin=ckanext-topics seed_command create_sample_topics -c /etc/ckan/default/<config_file>.ini
    '''

    usage = __doc__
    summary = usage.split('\n')[0]

    def command(self):
        self._load_config()

        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'create_tag_vocabularies':
            self.create_tag_vocabularies()
        elif cmd == 'create_sample_topics':
            self.create_sample_topics()
        else:
            print 'Command %s not recognized' % cmd

    def create_tag_vocabularies(self):
        print "\n[SEED] Creating tag vocabularies..."

        vocabularies_names = ['custom_topics', 'custom_subtopics']
        context = {}

        for vocabulary_name in vocabularies_names:
            print "Creating vocabulary " + vocabulary_name
            print logic.get_action('vocabulary_create')(context, { 'name': vocabulary_name })

        print "\n[SEED] Tag vocabularies created"

    def create_sample_topics(self):
        print "\n[SEED] Creating sample topics..."

        subtopics_vocabulary = Subtopic.vocabulary_id()

        sample_topics = [
            {
                'position': 0,
                'name': { 'es': u'Economía', 'en': u'Economy', 'eu': u'Ekonomia' }
            },
            {
                'position': 1,
                'name': { 'es': u'Ecología', 'en': u'Ecology', 'eu': u'Ekologia' }
            }
        ]

        for topic in sample_topics:
            result = logic.get_action('topic_create')({}, Topic.build_tag_dict(topic['position']))
            for lang_code, name in topic['name'].iteritems():
                if name:
                    logic.get_action('term_translation_update')({}, {
                        'term': result['id'],
                        'term_translation': name,
                        'lang_code': lang_code
                    })

        economy_topic_id = logic.get_action('tag_show')({}, { 'id': Topic.build_tag_name(0), 'vocabulary_id': Topic.vocabulary_id() })['id']
        ecology_topic_id = logic.get_action('tag_show')({}, { 'id': Topic.build_tag_name(1), 'vocabulary_id': Topic.vocabulary_id() })['id']

        sample_subtopics = [
            {
                'position': 0,
                'parent_id': economy_topic_id,
                'name': { 'es': u'Microeconomía', 'en': u'Microeconomy', 'eu': u'Mikroekonomia' }
            },
            {
                'position': 1,
                'parent_id': economy_topic_id,
                'name': { 'es': u'Macroeconomía', 'en': u'Macroeconomy', 'eu': u'Macroeconomy' }
            },
            {
                'position': 0,
                'parent_id': ecology_topic_id,
                'name': { 'es': u'Bosques', 'en': u'Forests', 'eu': u'Basoak' }
            },
            {
                'position': 1,
                'parent_id': ecology_topic_id,
                'name': { 'es': u'Océanos', 'en': u'Oceans', 'eu': u'Ozeanoak' }
            }
        ]

        for subtopic in sample_subtopics:
            result = logic.get_action('topic_create')({}, Subtopic.build_tag_dict(
                subtopic['position'],
                subtopic['parent_id']
            ))
            for lang_code, name in subtopic['name'].iteritems():
                logic.get_action('term_translation_update')({}, {
                    'term': result['id'],
                    'term_translation': name,
                    'lang_code': lang_code
                })

        print "\n[SEED] Sample topics created"

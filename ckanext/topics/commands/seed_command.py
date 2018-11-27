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

        sample_topics = [
            { 'name': 'a_Economy', 'subtopics':  ['a_a_Microeconomy', 'a_b_Macroeconomy'] },
            { 'name': 'b_Ecology', 'subtopics':  ['b_a_Forests', 'b_b_Oceans'] }
        ]
        context = {}

        for topic_data in sample_topics:
            print logic.get_action('tag_create')(context, { 'name': topic_data['name'], 'vocabulary_id': Topic.vocabulary_id() })
            for subtopic in topic_data['subtopics']:
                print logic.get_action('tag_create')(context, { 'name': subtopic, 'vocabulary_id': Subtopic.vocabulary_id() })

        print "\n[SEED] Sample topics created"

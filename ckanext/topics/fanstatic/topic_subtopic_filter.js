// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
'use strict';

ckan.module('topic_subtopic_filter', function ($) {
  return {
    initialize: function () {

      $('#field-custom_topic').select2({
        placeholder: ' - ',
        allowClear: true,
        minimumResultsForSearch: 8
      });

      $('#field-custom_subtopic').select2({
        matcher: function(term, text, option) {
          return option.attr('js-parent-topic-id') === selectedTopicId();
        },
        placeholder: ' - ',
        allowClear: true,
        minimumResultsForSearch: 8
      });

      $('#field-custom_topic').on('change.select2', function (e) {
        $('#field-custom_subtopic').select2('val', '');
      });

    }
  };
});

function selectedTopicId() {
  var topicSelector = $('#field-custom_topic');
  return topicSelector.find(':selected').attr('js-topic-id');
}

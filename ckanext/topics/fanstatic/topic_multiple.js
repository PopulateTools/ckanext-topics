// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
'use strict';

ckan.module('topic_multiple', function ($) {
  return {
    initialize: function () {

      $('#field-custom_topic').select2({
        allowClear: true,
        minimumResultsForSearch: 8
      });
    }
  };
});

/* global $ */
/* global createTags */

$(document).ready(function() {
  var validTags = [];
  $('#p-tags').hide();
  $('#p-tags').tagit({
    allowSpaces: true,
    showAutocompleteOnFocus: !createTags,
    tagSource: function(search, showChoices) {
      var value = $('.tagit-new > input').val();
      var searchData = {value: value};
      var that = this;

      $.ajax({
        type: 'GET',
        url: '/prm/view/records/get-tags',
        data: searchData,
        success: function(data) {
          var jdata = $.parseJSON(data);
          validTags = jdata;
          showChoices(that._subtractArray(jdata, that.assignedTags()));
        }
      });
    },
    beforeTagAdded: function(event, ui) {
      ui.tag.hide();

      if(!ui.duringInitialization && !createTags && validTags.indexOf(ui.tagLabel) === -1) {
        ui.tag.text('');
      } else {
        $.ajax({
          type: 'GET',
          url: '/prm/view/records/get-tag-color',
          data: {'name': ui.tagLabel},
          success: function(data) {
            var jdata = $.parseJSON(data);
            if(jdata.length > 0) {
              ui.tag.css('background-color', '#' + jdata[0]);
            }
            ui.tag.show();
          }
        });
      }
    },
    afterTagAdded: function(event, ui) {
      if(!ui.duringInitialization && !createTags && validTags.indexOf(ui.tagLabel) === -1) {
        var $tags = $('#p-tags');
        var words = $tags.val().split(',');

        $tags.val(words.splice(0, words.length - 1).join(','));
      }
      if ($('#addTags').hasClass('disabled')) {
        $('#addTags').removeClass('disabled');
      };
    },
    afterTagRemoved: function(event, ui) {
      if (!( $('#addTags').hasClass('disabled') || $('#p-tags').val())) {
        $('#addTags').addClass('disabled');
      }
    },
    autocomplete: {
      delay: 0,
      minLength: 1,
      autoFocus: false,
      close: function() {
        if (document.activeElement !== this) {
          $("#p-tags").tagit("createTag", this.value);
        }
      }
    },
    placeholderText: 'Add Tag'
  });
});

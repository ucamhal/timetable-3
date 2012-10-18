define(['jquery', 'underscore'], function ($, _) {
	"use strict";

	var InputArea = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(InputArea.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector),
			});

			$('a#advancedOptions, #advancedSearch input[type="submit"], #advancedSearch a.close', this.$el).click(function () {
				if ($('#advancedSearch').is(':visible') === true) {
					$('#advancedSearch').slideUp('fast');
				} else {
					$('#advancedSearch').slideDown('fast');
				}
			});

			$('select', this.$el).change(function (event) {
				self.updateHash();
			});
		},

		updateHash: function () {
			$.bbq.pushState({
				course: $("select#iAmInput", this.$el).val(),
				part: $("select#courseSelect", this.$el).val()
			});
		},

		updateSelectedCourse: function (selectedCourse) {
			$("select#iAmInput", this.$el).val($("select#iAmInput option:contains('" + selectedCourse + "')", this.$el).attr('value'));
		},

		updateSelectedPart: function (selectedPart) {
			$("select#courseSelect", this.$el).val(selectedPart);
		},

		updatePartOptions: function (selectedCourseOption) {
			var parts = $("select#iAmInput option:contains('" + selectedCourseOption + "')", this.$el).data("levels"),
				partsLength = parts.length,
				i;

			if(parts !== this.activeParts) {
				this.activeParts = parts;
				$("select#courseSelect", this.$el).empty();
				for(i = 0; i < partsLength; i += 1) {
					$("select#courseSelect", this.$el).append("<option value=\"" + parts[i].subject_id + "\">" + parts[i].level_name + "</option>");
				}
				$("select#courseSelect", this.$el).trigger('change');
			}
		}
	});

	return InputArea;
});
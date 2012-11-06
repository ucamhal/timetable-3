define([
	"jquery",
	"underscore"
], function ($, _) {
	"use strict";
	
	var BaseInputArea = function () {

	};

	_.extend(BaseInputArea.prototype, {

		baseInitialize: function () {

			var self = this;

			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector)
			});

			$('select#iAmInput, select#courseSelect', this.$el).change(function (event) {
				self.updateThingPathHash(self.getThingPathFromSelectedOption($(this)));
			});

			if(typeof $.bbq.getState('path') === 'undefined') {
				$('select#iAmInput', this.$el).trigger('change');
			}

		},

		getThingPathFromSelectedOption: function ($select) {
			if (_.isArray($("option:selected", $select).data("levels"))) {
				return $("option:selected", $select).data("levels")[0]["fullpath"];
			} else {
				return $select.val();
			}
		},

		updateSelectBoxes: function () {
			var $selectedCourseOption = this.getSelectedOptionFromThingPath($("#iAmInput", this.$el)),
				parts = $selectedCourseOption.data("levels"),
				partsLength = parts.length,
				i;
			
			$("#iAmInput").val($selectedCourseOption.val());

			if (parts !== this.activeParts) {
				this.activeParts = parts;
				$("select#courseSelect", this.$el).empty();
				for (i = 0; i < partsLength; i += 1) {
					$("select#courseSelect", this.$el).append("<option value=\"" + parts[i].fullpath + "\">" + parts[i].level_name + "</option>");
				}

				if (typeof $.bbq.getState('path') === 'undefined' || $.bbq.getState('path') !== $("select#courseSelect", this.$el).val()) {
					$("select#courseSelect", this.$el).val($.bbq.getState('path'));
					$("select#courseSelect", this.$el).trigger('change');
				}
			}
		},

		getSelectedOptionFromThingPath: function ($select) {
			return $("option", $select).filter(function (i, element) {
				return _.any($(element).data("levels"), function (obj) {
					return obj.fullpath === $.bbq.getState('path');
				});
			});
		},

		updateThingPathHash: function (value) {
			$.bbq.pushState({
				path: value
			});
		}

	});

	return BaseInputArea;

});
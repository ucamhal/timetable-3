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
				$el: $(this.selector)
			});

			this.updateHash();

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
				course: $('select#iAmInput', this.$el).val(),
				part: $('select#courseSelect', this.$el).val()
			});
		}
	});

	return InputArea;
});
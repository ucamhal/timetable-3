define(['jquery', 'underscore'], function ($, _) {
	"use strict";

	var CalendarHeading = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(CalendarHeading.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector, this.parent.$el)
			});

			$('#calendarData a', this.$el).click(function (event) {
				switch ($(this).text()) {
				case '<':
					self.parent.content.showPrev();
					break;
				case '>':
					self.parent.content.showNext();
					break;
				}
			});

			$('.nav a', this.$el).click(function (event) {
				if ($(this).parent().is('.active') === false) {
					$('#calendarHolder .nav li').removeClass('active');
					$(this).parent().addClass('active');
					self.updateHash();
				}

				event.preventDefault();
			});

			self.updateHash();
		},

		updateHash: function () {
			$.bbq.pushState({
				calendarView: $('.nav li.active a', this.$el).text().toLowerCase()
			});
		}
	});

	return CalendarHeading;
});
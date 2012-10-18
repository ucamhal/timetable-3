define(['jquery', 'underscore', 'fullcalendar'], function ($, _) {
	"use strict";

	var CalendarContent = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(CalendarContent.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				activeView: 'agendaWeek',
				$el: $(this.selector, this.parent.$el)
			});

			this.$el.fullCalendar({
				defaultView: this.activeView,
				allDaySlot: false,
				minTime: 7,
				maxTime: 20,
				header: false,
				columnFormat: {
					week: 'ddd dd/M'
				}
			});
		},

		showNext: function () {
			this.$el.fullCalendar('next');
		},

		showPrev: function () {
			this.$el.fullCalendar('prev');
		},

		setView: function (view) {
			this.activeView = view;
			this.$el.fullCalendar('changeView', view);
		}
	});

	return CalendarContent;
});
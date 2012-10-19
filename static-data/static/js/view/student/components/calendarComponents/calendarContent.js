define(['jquery', 'underscore', 'fullcalendar'], function ($, _) {
	"use strict";

	var CalendarContent = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(CalendarContent.prototype, {
		initialize: function () {
			var sourcepath = $("#userinfo").attr("userid");
			if ( ! sourcepath ) {
				sourcepath = $("#thinginfo").attr("fullpath");		
			} else {
				sourcepath = 'user/' + sourcepath; 
			}
			_.defaults(this, {
				selector: 'body',
				activeView: 'agendaWeek',
				$el: $(this.selector, this.parent.$el)
			});

			this.$el.fullCalendar({
				defaultView: this.activeView,
				events: '/' +sourcepath+'.cal.json',
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
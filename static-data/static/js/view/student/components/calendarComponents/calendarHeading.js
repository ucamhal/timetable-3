define(["jquery", "underscore"], function ($, _) {
	"use strict";

	var CalendarHeading = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(CalendarHeading.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector, this.parent.$el),
				activeView: "agendaWeek"
			});

			$("#calendarData a", this.$el).live("click", function (event) {
				switch ($(this).text()) {
				case "<":
					self.parent.content.showPrev();
					break;
				case ">":
					self.parent.content.showNext();
					break;
				}

				self.updateTerm();
				self.updateTimeIndication();
			});

			$(".nav a", this.$el).live("click", function (event) {
				self.updateCalendarViewHashTo($(this).text().toLowerCase());
				event.preventDefault();
			});

			if (typeof $.bbq.getState("calendarView") === "undefined") {
				self.updateCalendarViewHashTo("week");
			}
		},

		setView: function (viewToSet) {
			this.activeView = viewToSet;
			$("#calendarData > div", this.$el).hide();
			$("#calendarData ." + viewToSet, this.$el).show();
			$(".nav li", this.$el).removeClass("active").filter("." + viewToSet).addClass("active");
			this.updateTerm();
			this.updateTimeIndication();
		},

		updateTerm: function () {
			var activeTerm = this.parent.content.getActiveTerm(),
				textToChange = "No term active";

			if (activeTerm) {
				textToChange = _(activeTerm).capitalize() + " Term";
			}

			$("#calendarData > div > h4", this.$el).text(textToChange);
		},

		updateTimeIndication: function () {
			var textToChange,
				activeWeekInTerm;

			switch (this.activeView) {
			case "month":
			case "list":
				var activeDate = this.parent.content.getActiveDate(),
					activeMonth = this.parent.content.getFullMonthFromDate(activeDate),
					activeYear = this.parent.content.getYearFromDate(activeDate);
				$(".month .calendarNavigation ul h4, .list .calendarNavigation ul h4", this.$el).text(_(activeMonth).capitalize() + " " + activeYear);
				//activeMonth = this.parent.content.getFullYearFromDate(this.parent.content.getActiveDate());
				break;
			case "agendaWeek":
				textToChange = "Outside term";
				activeWeekInTerm = this.parent.content.getActiveWeekInCurrentTerm();

				if (activeWeekInTerm) {
					textToChange = "Week " + activeWeekInTerm;
				}

				$(".agendaWeek .calendarNavigation ul h4", this.$el).text(textToChange);
				break;
			}

		},

		updateCalendarViewHashTo: function (state) {
			$.bbq.pushState({
				calendarView: state
			});
		}
	});

	return CalendarHeading;
});
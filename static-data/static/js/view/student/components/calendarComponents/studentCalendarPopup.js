define([
	"jquery",
	"underscore",
	"view/student/components/calendarComponents/baseCalendarPopup"
], function ($, _, BaseCalendarPopup) {

	var StudentCalendarPopup = function (opts) {
		_.extend(this, opts);
		this.initialize();
		this.baseInitialize();
	}

	_.extend(StudentCalendarPopup.prototype, BaseCalendarPopup.prototype);
	_.extend(StudentCalendarPopup.prototype, {
		initialize: function () {
			_.defaults(this, {
				$el: $(".calendarEventInfo.dontDisplayMe.student").clone().removeClass("dontDisplayMe")
			});

			$("span.courseDatePattern", this.$el).text(this.parent.getFullDayFromDate(this.calEvent._start) + " " + this.parent.getTwelveHourTimeFromDate(this.calEvent._start));

			$("span.courseLocation", this.$el).text((function (location) {
				var locationText = location;
				if (typeof location === "undefined" || location.length <= 0) {
					locationText = "No location specified.";
				}
				return locationText;
			}(this.calEvent.location)));

			$("span.courseLecturer", this.$el).text((function (lecturers) {
				var lecturersText = "",
					lecturersLength = lecturers.length,
					i;
				if (lecturersLength > 0) {
					if (lecturersLength === 1) {
						lecturersText = lecturers[0];
					} else {
						for (i = 0; i < lecturersLength; i += 1) {
							lecturersText += lecturers[i];

							if (i !== lecturersLength - 1) {
								lecturersText += ", ";
							}
						}
					}
				} else {
					lecturersText = "No lecturers specified.";
				}
				return lecturersText;
			}(this.calEvent.lecturer)));

			$("h5", this.$el).text(this.calEvent.title);
		},

		linkClickHandler: function () {
			console.log("student click");
		}
	});

	return StudentCalendarPopup;

});
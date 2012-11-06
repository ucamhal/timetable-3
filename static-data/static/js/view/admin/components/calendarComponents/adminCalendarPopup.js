define([
	"jquery",
	"underscore",
	"view/base/components/calendarComponents/baseCalendarPopup"
], function ($, _, BaseCalendarPopup) {
	"use strict";

	var AdminCalendarPopup = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(AdminCalendarPopup.prototype, BaseCalendarPopup.prototype);
	_.extend(AdminCalendarPopup.prototype, {
		initialize: function () {

			_.bindAll(this, "insertForm");
			_.bindAll(this, "linkClickHandler");
			_.defaults(this, {
				$el: $(".calendarEventInfo.dontDisplayMe.admin").clone().removeClass("dontDisplayMe")
			});

			$("div.progress div", this.$el).text("Loading event data...");

			// Fetch pre-populated form for the clicked event
			// FIXME: get event id...
			$.get(this.editFormPath, this.insertForm);
		},

		getStrippedTimeStringFromTimepickerValue: function (value) {
			return value.replace(/(:| |PM|AM)/gi, "");
		},

		getHourFromTimepickerValue: function (value) {
			var timeString = this.getStrippedTimeStringFromTimepickerValue(value);
			if (timeString[0] + timeString[1] === "12") {
				return "00";
			}
			return timeString[0] + timeString[1];
		},

		getMinutesFromTimepickerValue: function (value) {
			var timeString = this.getStrippedTimeStringFromTimepickerValue(value);
			return timeString[2] + timeString[3];
		},

		getAmPmFromTimepickerValue: function (value) {
			if (value.search(/AM/gi) >= 0) {
				return 0
			}
			return 1;
		},

		getInputValueForTimeObject: function (timeObject) {
			var inputValue = "";

			if (timeObject.hour === "00") {
				timeObject.hour = "12";
			}

			inputValue += timeObject.hour + ":" + timeObject.minutes + " ";

			inputValue += (function () {
				if(timeObject.amPm === 0) {
					return "AM";
				}

				return "PM";
			}());

			return inputValue;
		},

		insertForm: function (form) {
			var $form = $(form),
				self = this;

			// kill any existing forms
			this.$el.find("form").remove();
			// insert the fetched form into the dialog.
			this.$el.find(".progress").after($form);

			$("*", this.$el).show();
			$(".progress", this.$el).hide();
			$form.find(".timepicker-default").timepicker({defaultTime: "value"});
			$form.find(".datepicker").datepicker();
			this.$scrollReference.trigger("scroll");

			$("input.timepicker-default", $form).change(function () {
				
				var fromHour = self.getHourFromTimepickerValue($("input#editFromEventTime").val()),
					fromMinutes = self.getMinutesFromTimepickerValue($("input#editFromEventTime").val()),
					fromAmPm = self.getAmPmFromTimepickerValue($("input#editFromEventTime").val()),

					toHour = self.getHourFromTimepickerValue($("input#editEventToTime", self.$el).val()),
					toMinutes = self.getMinutesFromTimepickerValue($("input#editEventToTime", self.$el).val()),
					toAmPm = self.getAmPmFromTimepickerValue($("input#editEventToTime", self.$el).val()),

					changeTo;

				if ($(this).attr("id") === "editFromEventTime") {

					changeTo = {
						amPm: toAmPm,
						minutes: toMinutes,
						hour: toHour
					};

					if (fromAmPm > toAmPm) {
						changeTo.amPm = fromAmPm;
					}

					if (fromAmPm === toAmPm && Number(fromHour) > Number(toHour)) {
						changeTo.hour = fromHour;
					}

					if (fromAmPm === toAmPm && fromHour === toHour && Number(fromMinutes) > Number(toMinutes)) {
						changeTo.minutes = fromMinutes;
					}

					$("input#editEventToTime", $form).val(self.getInputValueForTimeObject(changeTo));


				} else {

					changeTo = {
						amPm: fromAmPm,
						minutes: fromMinutes,
						hour: fromHour
					};

					if (toAmPm < fromAmPm) {
						changeTo.amPm = toAmPm;
					}

					if (toAmPm === fromAmPm && Number(toHour) < Number(fromHour)) {
						changeTo.hour = toHour;
					}

					if (toAmPm === fromAmPm && toHour === fromHour && Number(toMinutes) < Number(fromMinutes)) {
						changeTo.minutes = toMinutes;
					}

					$("input#editFromEventTime", $form).val(self.getInputValueForTimeObject(changeTo));
				}
			});

			$form.data("submit", function () {
				var formData = $form.serialize();
				return $.post(self.editFormPath, formData, function (data) {

					if (_.isObject(data)) {
						// Form submit was OK
						// Update the calendar event 
						_.extend(self.calEvent, data);
						self.parent.$el.fullCalendar("updateEvent", self.calEvent);
					} else {
						// Form was returned w/ errors, redisplay
						self.insertForm(data);
					}
				});
			});
		},

		linkClickHandler: function (event) {
			var self = this,
				$form,
				jqxhr;

			switch ($(event.currentTarget).text().toLowerCase()) {
			case "save":
				$form = $("form", this.$el);
				jqxhr = $form.data("submit")();

				$form.hide();

				$(".progress", this.$el).show().find("div").text("Saving event...");
				this.$scrollReference.trigger("scroll");

				jqxhr.always(function () {
					$("*", self.$el).show();
					$(".progress", self.$el).hide();
					self.$scrollReference.trigger("scroll");
				}).fail(function () {
					// called if POST fails
					console.error("oh noes! form submit failed");
					$form.show();
				});
				break;
			case "remove event":
				console.log("remove event");
				break;
			case "cancel":
				this.remove();
				break;
			}

			event.preventDefault();
		}
	});

	return AdminCalendarPopup;

});
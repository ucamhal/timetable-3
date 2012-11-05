define([
	"jquery",
	"underscore",
	"view/student/components/calendarComponents/baseCalendarPopup"
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
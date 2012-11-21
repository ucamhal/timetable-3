define([
	"jquery",
	"underscore"
], function ($, _) {
	"use strict";

	var EventField = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(EventField.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				initialValue: this.getValue(),
				value: this.initialValue,
				editable: false,
				changed: false,
				disabled: false,
				editEnabled: false
			});

			_.bindAll(this, "focusInHandler");
			_.bindAll(this, "focusOutHandler");
			_.bindAll(this, "dateDataChangedHandler");

			if (this.$el.hasClass("secondStepped") === true) {
				this.$el.focusin(this.focusInHandler);

				if (this.$el.hasClass("secondSteppedOut") === true) {
					this.$el.focusout(this.focusOutHandler);
				}
			}
			
			if (this.getType() === "eventDateTime") {

				_.addEventListener(this.$el, "dataChanged", this.dateDataChangedHandler);

				this.fromTime = this.initialFromTime = new Date(2012, 1, 1, $(".eventDateTimeFromFields input.hours").val(), $(".eventDateTimeFromFields input.minutes").val()),
				this.toTime = this.initialToTime = new Date(2012, 1, 1, $(".eventDateTimeToFields input.hours").val(), $(".eventDateTimeToFields input.minutes").val());
				this.duration = this.initialDuration = this.initialToTime - this.initialFromTime;

				$(".datePatternDialog a.close", this.$el).click(function () {
					self.$el.focusout();
				});

				$(".eventDateTimeFromFields input, .eventDateTimeToFields input", this.$el).change(function (event, original) {

					var $hourInput,
						hourInputValue,
						currentValue = $(this).val(),
						type = (function ($target) {
							if ($target.parent().parent().hasClass("eventDateTimeFromFields")) {
								return "from";
							}
							return "to";
						}($(this))),
						fromTime,
						$ulParent = $(this).parent().parent();

					if (currentValue.length === 1) {
						$(this).val("0" + currentValue);
					}

					if ($(this).hasClass("minutes")) {
						$hourInput = $("input.hours", $(this).parent().parent());
						hourInputValue = Number($hourInput.val());

						if ($(this).val() === "60") {
							hourInputValue += 1;
							$hourInput.val(hourInputValue);
							$hourInput.trigger("change");
							$(this).val("00");
						} else if (Number($(this).val()) < 0) {
							hourInputValue -= 1;
							$hourInput.val(hourInputValue);
							$hourInput.trigger("change");
							$(this).val("45");
						}
					} else if ($(this).hasClass("hours")) {
						hourInputValue = Number($(this).val());
						if (hourInputValue > 23) {
							$(this).val("00");
						} else if (hourInputValue < 0) {
							$(this).val("23");
						}
					}
					
					if (type === "from") {
						self.fromTime.setMinutes($("input.minutes", $ulParent).val());
						self.fromTime.setHours($("input.hours", $ulParent).val());
						self.toTime = new Date(self.fromTime.valueOf() + self.duration);
						
						$(".eventDateTimeToFields input.hours", self.$el).val(self.toTime.getHours()).trigger("change", false);
						$(".eventDateTimeToFields input.minutes", self.$el).val(self.toTime.getMinutes()).trigger("change", false);
					} else if (original !== false) {
						self.toTime.setMinutes($(".eventDateTimeToFields input.minutes", self.$el).val());
						self.toTime.setHours($(".eventDateTimeToFields input.hours", self.$el).val());
						self.duration = self.toTime - self.fromTime;
					}
				});
			}

			$("input, select", this.$el).change(function (event) {
				console.log("data changed handler");
				_.dispatchEvent(self.$el, "dataChanged");
				console.log(self.dataChanged());
			});

			$("input", this.$el).keyup(function (event) {
				if (self.dataChanged() === true) {
					_.dispatchEvent(self.$el, "dataChanged");
				}
			});

			this.$el.click(function (event) {
				if (self.$el.hasClass("secondStepped") === false && self.editEnabled === false) {
					self.selectInput = true;
				}
				_.dispatchEvent(self.$el, "fieldClicked");
			});
		},

		setDisabled: function (disabled) {
			this.disabled = disabled;
			$("input, select", this.$el).attr("disabled", disabled);
		},

		dateDataChangedHandler: function () {
			$(".dataInput > p", this.$el).html(this.generateDateStringFromDatePatternDialogValues());
		},

		generateDateStringFromDatePatternDialogValues: function () {
			return "W " + $(".eventDateTimeWeek", this.$el).val() + " in " + _.capitalize($(".eventDateTimeTerm", this.$el).val()) + ", on " + _.capitalize($(".eventDateTimeDay", this.$el).val().substr(0, 3)) + " " + $(".eventDateTimeFromFields input.hours", this.$el).val() + ":" + $(".eventDateTimeFromFields input.minutes", this.$el).val() + "-" + $(".eventDateTimeToFields input.hours", this.$el).val() + ":" + $(".eventDateTimeToFields input.minutes", this.$el).val();
		},

		toggleInitialFocusClass: function (focus) {
			var focus = typeof focus === "undefined" ? !this.hasClass("initialFocus") : focus;
			this.$el.toggleClass("initialFocus", focus);
		},

		toggleFocusClass: function (focus) {
			var focus = typeof focus === "undefined" ? !this.hasChanged("focus") : focus;
			this.$el.toggleClass("focus", focus);
		},

		focusInHandler: function (event) {
			if (this.disabled === false) {
				this.toggleInitialFocusClass(true);
				this.toggleFocusClass(true);
			}
		},

		focusOutHandler: function (event) {
			if (this.disabled === false) {
				this.toggleFocusClass(false);
			}
		},

		dataChanged: function () {
			return this.getValue().toLowerCase() !== this.initialValue.toLowerCase();
		},

		getValue: function () {
			switch (this.getType()) {
			case "eventTitle":
			case "eventLocation":
			case "eventLecturers":
				return {
					inputValue: $("input", this.$el).val()
				};
				break;
			case "eventType":
				return {
					selectValue: $("select", this.$el).val()
				};
				break;
			case "eventDateTime":
				return {
					week: $(".eventDateTimeWeek", this.$el).val(),
					term: $(".eventDateTimeTerm", this.$el).val(),
					day: $(".eventDateTimeDay", this.$el).val(),
					fromHour: $(".eventDateTimeFromFields .hours", this.$el).val(),
					fromMinutes: $(".eventDateTimeFromFields .minutes", this.$el).val(),
					toHour: $(".eventDateTimeToFields .hours", this.$el).val(),
					toMinutes: $(".eventDateTimeToFields .minutes", this.$el).val()
				};
				break;
			}
			return {};
		},

		getType: function () {
			var self = this;
			return this.type || (function () {
				var possibleTypes = [
					"eventTitle",
					"eventLocation",
					"eventLecturers",
					"eventType",
					"eventDateTime"
				];

				self.type = _.find(possibleTypes, function (item) {
					return self.$el.hasClass(item);
				});
				return self.type;
			}());
		},

		setValue: function (value) {
			switch (this.getType()) {
			case "eventTitle":
			case "eventLocation":
			case "eventLecturers":
				$("input", this.$el).val(value.inputValue);
				break;
			case "eventType":
				$("select", this.$el).val(value.selectValue);
				break;
			case "eventDateTime":
				$(".eventDateTimeWeek", this.$el).val(value.week);
				$(".eventDateTimeTerm", this.$el).val(value.term);
				$(".eventDateTimeDay", this.$el).val(value.day);
				$(".eventDateTimeFromFields .hours", this.$el).val(value.fromHour);
				$(".eventDateTimeFromFields .minutes", this.$el).val(value.fromMinutes);
				$(".eventDateTimeToFields .hours", this.$el).val(value.toHour);
				$(".eventDateTimeToFields .minutes", this.$el).val(value.toMinutes);
				break;
			}
		},

		toggleEditEnabledState: function (editEnabled, updateUI, revertData) {
			var self = this;

			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			revertData = typeof revertData === "undefined" ? false : revertData;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			if (this.selectInput === true) {
				this.selectInput = false;
				$("input, select", this.$el).focus().select();
			}

			if (this.editEnabled === false) {
				this.toggleInitialFocusClass(false);
				this.toggleFocusClass(false);
			} else {
				if (this.getType() === "eventDateTime") {
					this.toggleInitialFocusClass(true);
				}
			}

			if (revertData === true) {
				this.revertData();
			}
		},

		revertData: function () {
			this.setValue(this.initialValue);

			if (this.getType() === "eventDateTime") {
				$(".dataInput > p", this.$el).html(this.generateDateStringFromDatePatternDialogValues());
			}
		}
	});

	return EventField;
});
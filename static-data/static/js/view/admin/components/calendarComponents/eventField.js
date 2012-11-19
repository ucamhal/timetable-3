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
				initialValue: $(".dataValue", this.$el).text(),
				value: $(".dataValue", this.$el).text(),
				editable: false,
				changed: false,
			});

			_.bindAll(this, "focusInHandler");
			_.bindAll(this, "focusOutHandler");

			if (this.$el.hasClass("secondStepped") === true) {
				this.$el.focusin(this.focusInHandler);

				if (this.$el.hasClass("secondSteppedOut") === true) {
					this.$el.focusout(this.focusOutHandler);
				}
			}

			$("input, select", this.$el).change(function (event) {
				_.dispatchEvent(self.$el, "dataChanged");
			});

			$("input", this.$el).keyup(function (event) {
				if (self.dataChanged() === true) {
					_.dispatchEvent(self.$el, "dataChanged");
				}
			});

			if (this.getType() === "eventDateTime") {

				$(".eventDateTimeFromFields input, .eventDateTimeToFields input", this.$el).change(function () {

					var $hourInput,
						hourInputValue,
						currentValue = $(this).val();

					if (currentValue.length === 1) {
						$(this).val("0" + currentValue);
					}

					if ($(this).hasClass("minutes")) {

						$hourInput = $("input.hours", $(this).parent().parent());
						hourInputValue = Number($hourInput.val());

						if ($(this).val() === "60") {
							if (hourInputValue === 23) {
								hourInputValue = 0;
							} else {
								hourInputValue += 1;
							}

							$hourInput.val(hourInputValue);
							$hourInput.trigger("change");
							$(this).val("00");
						} else if (Number($(this).val()) < 0) {
							if (hourInputValue === 0) {
								hourInputValue = 23;
							} else {
								hourInputValue -= 1;
							}

							$hourInput.val(hourInputValue);
							$hourInput.trigger("change");
							$(this).val("45");
						}
					}
				});
			}
		},

		focusInHandler: function (event) {
			this.$el.toggleClass("focus", true);
		},

		focusOutHandler: function (event) {
			this.$el.toggleClass("focus", false);
		},

		dataChanged: function () {
			return this.getValue().toLowerCase() !== this.initialValue.toLowerCase();
		},

		getValue: function () {
			switch (this.getType()) {
			case "eventTitle":
			case "eventLocation":
			case "eventLecturers":
				return $("input", this.$el).val();
			case "eventType":
				return $("select", this.$el).val();
			case "eventDateTime":
				break;
			}

			return "";
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
				$("input", this.$el).val(value);
				break;
			case "eventType":
				$("select", this.$el).val(value);
				break;
			case "eventDateTime":
				break;
			}

			$(".dataValue", this.$el).text(value);
		},

		toggleEditEnabledState: function (editEnabled, updateUI, revertData) {
			var self = this;

			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			revertData = typeof revertData === "undefined" ? false : revertData;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			if (this.editEnabled === false) {
				this.$el.toggleClass("focus", false);
			}

			if (typeof this.initialWidth === "undefined") {
				this.initialWidth = this.$el.innerWidth();
			}

			//$(".dataInput", this.$el).width(this.initialWidth);

			if (revertData === true) {
				this.revertData();
			}
		},

		revertData: function () {
			this.setValue(this.initialValue);
		}
	});

	return EventField;
});
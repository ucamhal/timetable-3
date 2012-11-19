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
				changed: false
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

			$(".spinner", this.$el).spinner({
				
			});
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
			case "eventType":
				$("select", this.$el).val(value);
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
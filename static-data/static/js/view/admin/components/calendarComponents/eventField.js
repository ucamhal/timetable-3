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
			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				initialValue: $(".dataValue", this.$el).text(),
				value: $(".dataValue", this.$el).text(),
				type: this.$el.attr("class"),
				editable: false,
				changed: false,
				initialWidth: this.$el.width()
			});

			$(".dataInput", this.$el).width(this.initialWidth);
		},

		dataChanged: function () {
			return this.getValue().toLowerCase() === this.initialValue.toLowerCase();
		},

		getValue: function () {
			switch (this.type) {
			case "eventTitle":
			case "eventLocation":
			case "eventLecturers":
				return $("input", this.$el).val();
			case "eventType":
				return $("select", this.$el).val();
			case "eventDateTime":
				break;
			}

			return false;
		},

		setValue: function (value) {
			switch (this.type) {
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
			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			revertData = typeof revertData === "undefined" ? false : revertData;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

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
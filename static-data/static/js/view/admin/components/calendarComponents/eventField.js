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
				initialValue: this.$el.text(),
				value: this.$el.text(),
				type: this.$el.attr("class"),
				editable: false,
				changed: false
			});
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

		toggleEditEnabledState: function (editEnabled, updateUI, revertData) {
			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			revertData = typeof revertData === "undefined" ? false : revertData;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			if (updateUI === true) {
				this.setEditEnabledState(this.editEnabled);
			}

			if (revertData === true) {
				this.revertData();
			}
		},

		revertData: function () {
			this.$el.html("");
			this.$el.text(this.initialValue);
			this.$el.append('<span class="icon-pencil"></span>');
		},

		setEditEnabledState: function (editEnabled) {
			switch (this.type) {
			case "eventTitle":
			case "eventLocation":
			case "eventLecturers":
				this.$el.html('<input type="text" value="' + this.value + '" />');
				break;
			case "eventType":
				this.$el.html('<select><option>Lecture</option></select>');
				break;
			case "eventDateTime":
				break;
			}
		}
	});

	return EventField;
});
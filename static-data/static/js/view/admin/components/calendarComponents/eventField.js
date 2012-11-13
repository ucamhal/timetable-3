define([
	"jquery",
	"underscore"
], function ($, _) {
	"use strict";

	var EventField = function (opt) {
		_.extend(this, opt);
		this.initialize();
	}

	_.extend(EventField.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				initialValue: this.$el.text(),
				value: this.$el.text(),
				type: this.$el.attr("class"),
				editable: false
			});
		},

		toggleEditEnabledState: function (editEnabled, updateUI) {
			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			if (updateUI === true) {
				this.setEditEnabledState(this.editEnabled);
			}
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
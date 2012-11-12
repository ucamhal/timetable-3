define([
	"jquery",
	"underscore",
	"view/admin/components/calendarComponents/eventField"
], function ($, _, EventField) {
	"use strict";

	var Event = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Event.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				editEnabled: false,
				fields: []
			});

			$("td:not(.eventActions)").each(function () {
				var field = new EventField({
					$el: $(this)
				});

				self.fields.push(field);
			});

			$(".eventActions a", this.$el).click(function (event) {
				var action = $(this).text();
				switch (action) {
				case "edit":
					self.toggleEditEnabledState();
					break;
				case "duplicate":
					break;
				case "remove":
					break;
				}
			});

			$("td:not(.eventActions)", this.$el).click(function (event) {
				if (self.editEnabled === false) {
					self.toggleEditEnabledState(true);
				}
			});
		},

		toggleEditEnabledState: function (editEnabled, updateUI) {
			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			_.each(this.fields, function (item) {
				//item.toggleEditEnabledState(editEnabled, updateUI);
			});

			if (updateUI === true) {
				this.setEditEnabledState(this.editEnabled);
			}
		},

		setEditEnabledState: function (editEnabled) {
			this.$el.toggleClass("editEnabled", editEnabled);
		}
	});


	return Event;
});
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

			_.bindAll(this, "dataChangedHandler");

			$("td:not(.eventActions)", this.$el).each(function () {
				self.fields.push(new EventField({
					$el: $(this)
				}));
			});

			this.$el.on("dataChanged", "td:not(.eventActions)", self.dataChangedHandler);

			$(".eventActions a.edit", self.$el).parent().mouseover(function (event) {
				self.togglePencilHoverState(true);
			});

			$(".eventActions a.edit", self.$el).parent().mouseout(function (event) {
				self.togglePencilHoverState(false);
			});

			$(".eventActions a", this.$el).click(function (event) {
				var action = $(this).text();
				switch (action) {
				case "edit":
					self.toggleEditEnabledState();
					break;
				case "duplicate":
					//different user story:
					_.dispatchEvent(self.$el, "duplicate");
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

		dataChangedHandler: function () {
			_.dispatchEvent(this.$el, "dataChanged");
		},

		togglePencilHoverState: function (pencilHover) {
			var self = this;

			var addClass = (function () {
				if (self.editEnabled === true) {
					return false;
				}
				return typeof pencilHover === "undefined" ? !self.$el.hasClass("pencilHover") : pencilHover;
			}());

			this.$el.toggleClass("pencilHover", addClass);
		},

		toggleEditEnabledState: function (editEnabled, updateUI, revertData) {
			this.editEnabled = typeof editEnabled === "undefined" ? !this.editEnabled : editEnabled;
			revertData = typeof revertData === "undefined" ? !this.editEnabled : revertData;
			updateUI = typeof updateUI === "undefined" ? true : updateUI;

			_.each(this.fields, function (item) {
				item.toggleEditEnabledState(editEnabled, updateUI, revertData);
			});

			if (updateUI === true) {
				this.setEditEnabledState(this.editEnabled);
			}

			_.dispatchEvent(this.$el, "editStateChanged");
		},

		setEditEnabledState: function (editEnabled) {
			this.togglePencilHoverState(editEnabled);
			this.$el.toggleClass("editEnabled", editEnabled);
		},

		cancelEdit: function () {
			if (this.editEnabled === true) {
				this.toggleEditEnabledState();
			}
		},

		saveEdits: function () {
			if (this.editEnabled === true && this.dataChanged() === true) {
				//post the form back
			}
		},

		dataChanged: function () {
			return _.any(this.fields, function (item) {
				return item.dataChanged();
			});
		}
	});


	return Event;
});
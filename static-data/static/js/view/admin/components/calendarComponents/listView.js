define([
	"jquery",
	"underscore",
	"view/admin/components/calendarComponents/module"
], function ($, _, Module) {
	"use strict";

	var ListView = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(ListView.prototype, {
		initialize: function () {
			var self = this;

			var startTime = new Date();

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				modules: []
			});

			$(".module", this.$el).each(function () {
				self.modules.push(new Module({
					$el: $(this)
				}));
			});

			window.onbeforeunload = function (event) {
				if (self.checkForOpenChanges() === true) {
					return "You have unsaved changes";
				}
			}

			console.log("javascript finished");
			console.log(new Date() - startTime);
		},

		checkForOpenChanges: function () {
			return _.any(this.modules, function (item) {
				return item.hasOpenChanges();
			});
		}
	});

	return ListView;

});
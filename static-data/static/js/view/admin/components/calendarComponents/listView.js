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

			$(".notImplemented").attr("title", "").tooltip({
				title: "Not yet implemented."
			});
		},

		checkForOpenChanges: function () {
			return _.any(this.modules, function (item) {
				return item.hasOpenChanges();
			});
		}
	});

	return ListView;

});
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

			console.log(this.modules);
		}
	});

	return ListView;

});
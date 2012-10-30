define(['jquery', 'underscore', 'util/page'], function ($, _, page) {

	var ListView = function (opt) {
		_.extend(this, opt);
		this.initialize();
	}

	_.extend(ListView.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector, this.parent.$el),
				activeDate: {}
			});

			this.render();
		},

		render: function (date) {
			var self = this,
				url = page.getThingPath()+".callist.html";

			if (date !== this.date) {
				this.date = date;

				var data = {}
				if (date) {
					data = {
						"y" : date.year,
						"m" : date.month
					}
				}

				$.get(url, data, function (data) {
					self.$el.empty().html(data);
				});
			}
		}
	});

	return ListView;

});
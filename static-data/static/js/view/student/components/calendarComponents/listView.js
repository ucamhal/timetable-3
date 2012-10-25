define(['jquery', 'underscore'], function ($, _) {

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
				url = "/eventlist";

			if (date !== this.date) {
				this.date = date;
				
				if (date) {
					url += "/" + date.year + "/" + date.month;
				}

				$.get(url, function (data) {
					self.$el.empty().html(data);
				});
			}
		}
	});

	return ListView;

});
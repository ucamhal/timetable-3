define(['jquery', 'underscore'], function ($, _) {

	var ListView = function (opt) {
		_.extend(this, opt);
		this.initialize();
	}

	_.extend(ListView.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector, this.parent.$el)
			});
		}
	});

	return ListView;

});
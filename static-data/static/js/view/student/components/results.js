define(['jquery', 'underscore'], function ($, _) {
	"use strict";

	var Results = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Results.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector)
			});

			this.populateList(5);

			$('a.more', this.$el).click(function (event) {
				switch ($(this).text()) {
				case 'more':
					$(this).text('show less');
					$('.courseMoreInfo', $(this).parent().parent()).slideDown('fast');
					break;
				case 'show less':
					$(this).text('more');
					$('.courseMoreInfo', $(this).parent().parent()).slideUp('fast');
					break;
				}
			});
		},

		populateList: function (toAdd) {
			var i,
				$singleResult = $('> ul > li:last-child', this.$el);

			for (i = 0; i < toAdd; i += 1) {
				$('> ul', this.$el).append($singleResult.clone());
			}
		}
	});

	return Results;
});
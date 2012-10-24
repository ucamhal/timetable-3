define(['jquery', 'underscore'], function ($, _) {

	var Actions = function (opt) {
		_.extend(this, opt);
		this.initialize();
	}

	_.extend(Actions.prototype, {
		initialize: function () {

			var self = this;

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector)
			});

			$("a.signIn", this.$el).click(function () {
				self.pushSignedInState(true);
			});

			if (typeof $.bbq.getState("signedIn") === "undefined") {
				this.pushSignedInState(false);
			}

		},

		pushSignedInState: function (signedIn) {
			this.signedIn = signedIn;
			$.bbq.pushState({
				signedIn: signedIn
			});
		},

		setSignedInState: function (to) {
			if (to === "true") {
				$("a.save, a.export", this.$el).show();
				$("a.signIn", this.$el).hide();
			} else {
				$("a.save, a.export", this.$el).hide();
				$("a.signIn", this.$el).show();
			}
		}
	});

	return Actions;

});
define(["$", "backbone"], function(Backbone) {
	
	var NoElementException = Backbone.inherits(Error, {
		constructor: function NoElementException() {
			NoElementException.__super__.constructor.apply(
				this, arguments);
		}
	});

	var View = Classes.Any.extend({
		constructor: function View(el) {
			if(el instanceof $) {
				if(el.length == 0) {
					throw new NoElementException(
						"empty jQuery object.");
				}
				this.$el = el.first();
				this.el = el[0];
			}
			else if(el instanceof Element) {
				this.el = el;
				this.$el = $(el);
			}
			else {
				throw new throw new NoElementException(
					"el was not an Element or jQuery object.");
			}
		},

		events: function() {
			return {};
		};
	});

	return {
		View: View
	}
});
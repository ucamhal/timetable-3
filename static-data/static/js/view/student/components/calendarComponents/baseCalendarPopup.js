define(["jquery", "underscore"], function ($, _) {

	var BaseCalendarPopup = function (opt) {
		_.extend(this, opt);
		this.baseInitialize();
	}

	_.extend(BaseCalendarPopup.prototype, {
		baseInitialize: function () {
			var self = this;
			_.bindAll(this, "reposition");
			_.bindAll(this, "remove");

			_.defaults(this, {
				linkClickHandler: function () {
				}
			});

			this.$el.bind("closed", function () {
				self.remove();
			});

			$("a", this.$el).click(this.linkClickHandler);

			$(window).resize(this.reposition);
			this.$scrollReference.bind("scroll", this.reposition);
			this.reposition();
		},
		reposition: function () {
			//FIXME first time reposition doesn't correctly position the element
			//this.$el.outerHeight() seems to be 0
			if ($(this.jsEvent.currentTarget).offset().top < this.$scrollReference.offset().top || $(this.jsEvent.currentTarget).offset().top + $(this.jsEvent.currentTarget).outerHeight() > this.$scrollReference.offset().top + this.$scrollReference.outerHeight()) {
				this.removeAnimated();
			} else {
				this.$el.css({
					top: $(this.jsEvent.currentTarget).offset().top - (this.$el.outerHeight() / 2 - $(this.jsEvent.currentTarget).outerHeight() / 2),
					left: $(this.jsEvent.currentTarget).offset().left + $(this.jsEvent.currentTarget).outerWidth() + 10
				});
			}
		},
		remove: function () {
			this.$scrollReference.unbind("scroll", this.reposition);
			$(window).unbind("resize", this.reposition);
			this.$el.unbind("closed");
			$("a", this.$el).unbind("click");
			this.$el.remove();
		},

		removeAnimated: function () {
			this.$el.fadeOut("10", this.remove);
		}
	});

	return BaseCalendarPopup;

});
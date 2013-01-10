define(["jquery", "underscore", "backbone"], function ($, _, Backbone) {

	"use strict";

	var CookieHandler = Backbone.View.extend({
		initialize: function () {
			this.checkCookieAccepted();
		},

		events: {
			"click .js-close" : "onCookieAccept"
		},

		onClose: function (event) {
			this.remove();
			event.preventDefault();
		},

		checkCookieAccepted: function () {
			var acceptedCookies = localStorage.getItem("timetables_cookie_accept");

			if (acceptedCookies) {
				this.remove();
			} else {
				this.$el.show();
			}
		},

		saveCookieAccepted: function () {
			localStorage.setItem("timetables_cookie_accept", true);
		},

		onCookieAccept: function (event) {
			this.saveCookieAccepted();
			this.remove();
			event.preventDefault();
		}
	});

	return CookieHandler;

});

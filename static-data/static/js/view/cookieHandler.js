define(["jquery", "underscore", "backbone"], function ($, _, Backbone) {

	"use strict";

	var CookieHandler = Backbone.View.extend({
		initialize: function () {
			this.checkCookieAccepted();
		},

		events: {
			"click .js-accept-cookies" : "onCookieAccept",
			"click .js-close" : "onClose"
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
			this.remove();
		},

		onCookieAccept: function (event) {
			this.saveCookieAccepted();
			event.preventDefault();
		}
	});

	return CookieHandler;

});
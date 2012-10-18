require.config({
	paths: {
		jquery: 'libs/jquery/jquery.min',
		underscore: 'libs/underscore/underscore.min',
		bootstrap: 'libs/bootstrap/bootstrap.min',
		jquerybbq: 'libs/jquerybbq/jquery.bbq.min',
		fullcalendar: 'libs/fullcalendar/fullcalendar.min'
	},
	shim: {
		'jquery': {
			exports: '$'
		},
		'underscore': {
			exports: '_'
		},
		'bootstrap': {
			deps: ['jquery']
		},
		'jquerybbq': {
			deps: ['jquery']
		},
		'fullcalendar' : {
			deps: ['jquery']
		}
	}
});

require([
	'app',
	'jquery',
	'underscore',
	'bootstrap',
	'jquerybbq',
	'fullcalendar'
], function (Application, $, _) {
	"use strict";
	$(function () {
		var app = new Application();
	});
});
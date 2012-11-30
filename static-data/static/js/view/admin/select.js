define(['jquery'], function ($) {
	"use strict";

	/**
	 * Implements select tags on admin pages.
	 */
	
	$( "select.js-select-faculty" ).change( function(){
		var target = $(this).val();
		$(window.location).attr('href', '/'+target+'.home.admin.html');
	});
});
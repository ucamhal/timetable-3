define(['jquery'], function ($) {
	"use strict";
	
	/**
	 * On the page data is loaded to idenfiy the page. This module extracts that information and 
	 * makes it available to to other modules.
	 */
	var _crsfToken, _pageThingPath;
	return {
		getThingPath : function() {
			if ( _pageThingPath === undefined ) {
				if ( $("#userinfo").length == 1 ) {
					_pageThingPath = 'user/' + $("#userinfo").attr("userid");
				} else if (  $("#thinginfo").length == 1 ) {
					_pageThingPath = $("#thinginfo").attr("fullpath");
				}
			}
			return _pageThingPath;
		},
		getCrsf : function() {
			if ( _crsfToken === undefined ) {
				if ( $("#userinfo").length == 1 ) {
					_crsfToken = $("#userinfo").find("[name=csrfmiddlewaretoken]").val()
				} else if (  $("#thinginfo").length == 1 ) {
					_crsfToken = $("#thinginfo").find("[name=csrfmiddlewaretoken").val()
				}
			}
			return _crsfToken;
		}
	}
});
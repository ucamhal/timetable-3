define(["jquery", "underscore", "view/admin/lists", "bootstrap", "not-implemented-tooltips"],
		function($, _, Lists) {
    "use strict";
    
    var moduleViews = [],
    	seriesViews = [];

    $(".js-module").each(function() {
    	moduleViews.push(new Lists.WritableModuleView({el: this}));
    });

    $(".js-series").each(function() {
    	seriesViews.push(new Lists.WritableSeriesView({el: this}));
    });
	
    // Make the list watch for URL hash items in order to expand series
    // & highlight events.
    Lists.bindUrlHashWatcher();
    
    var locker = new Lists.Locker({
    	preventTimeoutTime: 30000,
    	pingTime: 10000,
    	locked: $("body").hasClass("locked"),
    	$lockedModal: $(".js-locked-modal"),
    	$timedOutModal: $(".js-timedout-modal"),
    	onLock: function () {
    		_.invoke(seriesViews, "lock");
    		_.invoke(moduleViews, "lock");
    	}
    });
    
    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");
    $(window).bind("beforeunload", function (e) {
    	locker.unlock();
    });
    
    
    Lists.listEvents.on("page-edited", locker.preventTimeout);
	
    return undefined;
});

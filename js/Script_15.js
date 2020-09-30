jQuery(document).ready(function($) {
	// for liveblog plugin's photo upload fix
	if ( $( '#liveblog-container' ).find( '.liveblog-form' ).length > 0 ) {
		$( '.article-container' ).css( 'z-index', 'auto' );
		$( '.background-image.news-single' ).toggleClass( 'liveblog' );
	}

	$(".lazy").lazyload({
        effect : "fadeIn",
        failure_limit : 20
    });

	$("iframe").each(function(){
		var ifr_source = $(this).attr('src') || "";
		var wmode = "wmode=transparent";
		if(ifr_source.indexOf('?') != -1) $(this).attr('src',ifr_source+'&'+wmode);
		else $(this).attr('src',ifr_source+'?'+wmode);
	});

	var iframeResize = {

		frameArray: [],
		aspect: "",
		contentSize: $('.entry-content').width() - (parseInt($('.entry-content p').css("padding-left")) * 2),
		container: $('.entry-content'),
		init: function(){

			iframeResize.container.find("iframe").each( function() {

				var ref = $(this),
					i = 0;

				iframeResize.aspect = ref.attr('width') / ref.attr('height');
				iframeResize.frameArray.push([ref.attr('width'), ref.attr('height')]);

				if(iframeResize.contentSize < iframeResize.frameArray[i][0] ) {
					ref.attr( 'width', '100%' );
					ref.attr( 'height', ref.width() / iframeResize.aspect );
				}

				i++;

			});

		},
		windowChange: function(){

			var k = 0;

			iframeResize.contentSize = $('.entry-content').width() - (parseInt($('.entry-content p').css("padding-left")) * 2);

			iframeResize.container.find("iframe").each( function() {

				var ref = $(this);

				if(iframeResize.contentSize < iframeResize.frameArray[0][0] && iframeResize.frameArray[0][0] != undefined) {
					ref.attr( 'width', '100%' );
					ref.attr( 'height', ref.width() / iframeResize.aspect );
				} else {

                    if(iframeResize.frameArray[k] != undefined) { // check iframe's width & height attr
					ref.attr('width', iframeResize.frameArray[k][0]).attr('height', iframeResize.frameArray[k][1]);
                    }
				}

				k++;

			});

		}

	}; iframeResize.init();

	$(window).resize(function() {

		iframeResize.windowChange();

	});

	$.getScript("//global.go.com/stat/dolWebAnalytics.js", function(data, textStatus, jqxhr) {

        $.getScript("//global.go.com/stat/plugin/urlTagging.js", function(data, textStatus, jqxhr) {
        	CTOinit();

        	(function () {
		        "use strict";
		        $(document).on("click", ".tm-cto a", function (event) {

		            // Filter out clicks that are not the left mouse
		            if (event.button !== 0) {
		                return;
		            }

		            var anchorName = $(event.currentTarget).attr("name") || "";
		            var retailerName = $(event.currentTarget).data("retailer") || "";

		            var linkNmIndex = anchorName.indexOf("&lid");
		            var linkPsIndex = anchorName.indexOf("&lpos");

		            var linkName = "";
		            var linkPosition = "";

		            if (linkNmIndex != -1 && linkPsIndex != -1 && (linkNmIndex < linkPsIndex)) {
		                linkName = anchorName.substring(linkNmIndex + 5, linkPsIndex);
		                linkPosition = anchorName.substring(linkPsIndex + 6);
		            }
		            else if (linkNmIndex != -1 && linkPsIndex == -1) {
		                linkName = anchorName.substring(linkNmIndex + 5);
		            }
		            else if (linkNmIndex != -1 && linkPsIndex != -1 && (linkPsIndex < linkNmIndex)) {
		                linkPosition = anchorName.substring(linkPsIndex + 6, linkNmIndex);
		                linkName = anchorName.substring(linkNmIndex + 5);
		            }
		            else if (linkPsIndex != -1 && linkNmIndex == -1) {
		                linkName = anchorName.substring(linkPsIndex + 6);
		            }

		            var linkUrl = $(event.currentTarget).attr("href"),
                        trackingObject = {};

		            // Make sure the link has a name and position
		            if ( linkName && linkPosition ) {
                        trackingObject = {
                            linkName: linkName,
                            linkPosition: linkPosition,
                            linkUrl: linkUrl
                        };
                    } else {
                        trackingObject = {
                            linkName: $(this).text() || false,
                            linkUrl: $(this).attr('href') || false
                        };
                    }

                    if ( retailerName.length > 0 ) {
                        trackingObject.retailerClick = retailerName;
                    }

                    if ( trackingObject.linkName && trackingObject.linkUrl ) {
		                // Make the tracking call
		                if (window.cto) {
			                cto.trackLink(trackingObject);
			            }
		            }
		        });
		    })();

        	return;

        });

        return;
    });

	$(".content-box.news .cb-content .cb-title").dotdotdot({
		ellipsis	: '... '
	});

    $(window).load(function() {
        swt_resize_sidebar();
    });

    $(window).resize(function() {
        swt_resize_sidebar();
    });

}); /* end of jQuery(document).ready() */

/*
 * Load up Foundation
 */
(function(jQuery) {
  jQuery(document).foundation();
})(jQuery);


function swt_place_sidebar() {
	var sb1 = jQuery("#fixed-container");
	sb1.parent().removeClass("stick-bottom scroll").css("top","auto");

	var sb1Top = sb1.offset().top;
	var sb1Bottom = sb1Top + sb1.height();

	var sb2 = jQuery(".sidebar-bottom");
	var sb2Top = sb2.offset().top;

	var ac = jQuery(".article-container");
	var acTop = ac.offset().top;

	var windowpos = jQuery(window).scrollTop();

	console.log(windowpos + ">=" + sb1Top + " && (" + windowpos + "+" + sb1.height() + ")" + "<" + sb2Top);

	if (windowpos >= sb1Top && (windowpos + sb1.height()) < sb2Top)  {
		sb1.parent().removeClass("stick-bottom").addClass("scroll").css("top","auto");
	} else if ((windowpos + sb1.height()) >= sb2Top) {
		sb1.parent().removeClass("scroll").css("top",sb2Top - acTop - sb1.height());
	} else {
		sb1.parent().removeClass("stick-bottom scroll").css("top","auto");
	}
}

/* Fix for absolute positioned sidebar */
function swt_resize_sidebar() {
	// Fix for right rail height
	if (jQuery('.sidebar-top, .sidebar-bottom, .sidebar').length) {
		totalHeight = 0;
		// jQuery('.sidebar-top, .sidebar-bottom, .sidebar').children().each(function(){
		//	totalHeight = totalHeight + jQuery(this).outerHeight(true);
		// });
		totalHeight = jQuery('.sidebar').outerHeight(true) + jQuery('.sidebar-top').outerHeight(true) + jQuery('.sidebar-bottom').outerHeight(true);
		jQuery('.article-container, article.content, .event-loop-content, .news-loop-content').css('min-height',totalHeight);  // Not happy with including article.content in this
	}
}


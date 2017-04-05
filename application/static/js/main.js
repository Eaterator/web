$(function() {
    
	// adding tags to input
    $(document).on("click",".sample-products-list>span", function() {
        var span = $("<span />").attr("data-role", "remove");
        $(this).prependTo(".bootstrap-tagsinput").addClass("tag label label-info");
        span.appendTo($(this));
                                                               
    });
    
    $(document).on("click",".bootstrap-tagsinput>span",function(){
        $(this).appendTo(".sample-products-list").removeClass().find("span").remove();
    });
	
    // smooth transition
	function scrollNav() {
		$('.carousel-caption > a').click(function() {  
			$('html, body').stop().animate({
				scrollTop: $( $(this).attr('href') ).offset().top - 150
			}, 400);
			return false;
		});
		$('#custom-search-input a').scrollTop();
	}
	
	scrollNav();
    
	// evaluate rating
    $(document).on("mouseup", ".btn-search",
    function() {
        setTimeout(function() {
//        $('.star').attr('data-content', '\f006');
            $('.recipe-rating').each(function(){
                if (0.5 < $(this).html() && $(this).html() <= 1.5) {
                     $(this).next().find('.rating-form').find('label.star-1').addClass('filled-star');
                }
                if (1.5 < $(this).html() && $(this).html() <= 2.5) {
                    $(this).next().find('.rating-form').find('label.star-1, label.star-2').addClass('filled-star');
                }
                if (2.5 < $(this).html() && $(this).html() <= 3.5) {
                    $(this).next().find('.rating-form').find('label.star-1, label.star-2, label.star-3').addClass('filled-star');
                }
                if (3.5 < $(this).html() && $(this).html() <= 4.5) {
                    $(this).next().find('.rating-form').find('label.star-1, label.star-2, label.star-3, label.star-4').addClass('filled-star');
                }
                if (4.5 < $(this).html() && $(this).html() <= 5) {
                    $(this).next().find('.rating-form').find('label.star-1, label.star-2, label.star-3,label.star-4, label.star-5').addClass('filled-star');
                }
            })
        }, 100);
    }
    );
    
    //div appear near clicked area
    //$('.show-detail').bind('click', function () {
    //    $(".activee").css( {position:"absolute", top:event.pageY});
    //})
    
    
    
     
    
    
    
});
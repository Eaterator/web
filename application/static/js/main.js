
$(function() {
	// adding tags to input
    $(document).on("click",".sample-products-list>span",function(){
        var span = $("<span />").attr("data-role", "remove");
        $(this).prependTo(".bootstrap-tagsinput").addClass("tag label label-info");
        span.appendTo($(this));
                                                               
    });
    
    $(document).on("click",".bootstrap-tagsinput>span",function(){
        $(this).appendTo(".sample-products-list").removeClass().find("span").remove();
    });
	
    //smooth transition
	function scrollNav() {
		$('.carousel-caption > a').click(function(){  
			//Toggle Class
//			$(".active").removeClass("active");      
//			$(this).closest('li').addClass("active");
//			var theClass = $(this).attr("class");
//			$('.'+theClass).parent('li').addClass('active');
			//Animate
			$('html, body').stop().animate({
				scrollTop: $( $(this).attr('href') ).offset().top - 150
			}, 400);
			return false;
		});
		$('#custom-search-input a').scrollTop();
	}
	
	scrollNav();
	
    
});
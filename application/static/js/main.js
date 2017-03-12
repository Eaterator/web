// adding elements to input
$(function() {
    $(document).on("click",".sample-products-list>span",function(){
        var span = $("<span />").attr("data-role", "remove");
        $(this).prependTo(".bootstrap-tagsinput").addClass("tag label label-info");
        span.appendTo($(this));
                                                               
    });
    
    $(document).on("click",".bootstrap-tagsinput>span",function(){
        $(this).appendTo(".sample-products-list").removeClass().find("span").remove();
    });
    
});
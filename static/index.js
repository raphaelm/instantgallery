$(document).ready(function(){
	$(".thumb:not(.dir)").bind("mouseenter", function(){
		if($(this).children("span").css("opacity") == 0){
			$(this).children("span").animate({opacity: 0.8}, 100);
		}
	});
	$(".thumb:not(.dir)").bind("mouseleave", function(){
		$(this).children("span").animate({opacity: 0}, 100);
	});
	$(".thumb.dir").bind("mouseenter", function(){
		if($(this).children("span").css("opacity") < 0.9){
			$(this).children("span").animate({opacity: 1}, 100);
		}
	});
	$(".thumb.dir").bind("mouseleave", function(){
		$(this).children("span").animate({opacity: 0.8}, 100);
	});
});

function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}

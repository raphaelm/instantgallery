$(document).ready(function(){
	$("#main, .exif").bind("click", function(){
		if($(".exif").css("opacity") == 0){
			if($("#map").length > 0) r = 1
			else r = 0.7
			$(".exif").animate({opacity: r}, 1000);
		}else{
			$(".exif").animate({opacity: 0}, 1000);
		}
	});
	$(".thumb").bind("mouseenter", function(){
		if($(this).children("span").css("opacity") == 0.5){
			$(this).children("span").animate({opacity: 0.9}, 100);
		}
	});
	$(".thumb").bind("mouseleave", function(){
		$(this).children("span").animate({opacity: 0.5}, 100);
	});
});

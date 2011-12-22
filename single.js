$(document).ready(function(){
	$("#main, .exif").bind("click", function(){
		if($(".exif").css("opacity") == 0){
			$(".exif").animate({opacity: 0.7}, 1000);
		}else{
			$(".exif").animate({opacity: 0}, 1000);
		}
	});
	$(".thumb").bind("mouseover", function(){
		if($(this).children("span").css("opacity") == 0.5){
			$(this).children("span").animate({opacity: 0.9}, 100);
		}
	});
	$(".thumb").bind("mouseout", function(){
		$(this).children("span").animate({opacity: 0.5}, 100);
	});
});

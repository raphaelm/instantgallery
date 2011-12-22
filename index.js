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
	$(".thumb.dir.anim").bind("mousemove", function(event){
		N = $(this).attr("rel")
		MAX = 10
		if(N > MAX){
			i = parseInt((parseInt(event.offsetX/(100 / MAX))*(N/MAX))+1)
		}else{
			i = parseInt((event.offsetX/(100 / parseInt(N)))+1)
		}
		$(this).children("img").attr("src", $(this).children("img").attr("rel")+"/thumbs/"+pad(i,8)+".jpg");
	});
});

function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}

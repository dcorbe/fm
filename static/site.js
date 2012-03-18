$(function(){
    $("#ratings").children().not(":radio").hide();
    $("#ratings").stars({
	callback: function(ui, type, value)
	{
	    $.post("/vote", {rate: value}, function(data)
		   {
		       $("#ajax_response").html(data);
		   });
	}
    });
});

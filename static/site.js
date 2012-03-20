$(document).ready(function() { 
    // bind 'myForm' and provide a simple callback function 
    $('#myForm').ajaxForm(function() { 
        alert("Thank you for your comment!"); 
    }); 
}); 

$(function(){
    $('.auto-submit-star').rating({
	callback: function(value, link){
	    //alert(value);
	    //this.form.submit();
	    $(this.form).ajaxSubmit();
	}
    });
});

// Flowplayer embed

$(function() {
	$('#btnSignUp').click(function() {
	
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST'
		});
	});
});

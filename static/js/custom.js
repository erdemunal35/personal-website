(function ($) {

  "use strict";

    // COLOR MODE
    $('.color-mode').click(function(){
        $('.color-mode-icon').toggleClass('active')
        $('body').toggleClass('dark-mode')
    })

    // HEADER
    $(".navbar").headroom();

    // PROJECT CAROUSEL
    $('.owl-carousel').owlCarousel({
    	items: 1,
	    loop:true,
	    margin:10,
	    nav:true
	});

    // SMOOTHSCROLL
    $(function() {
      $('.nav-link, .custom-btn-link').on('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top - 49
        }, 1000);
        event.preventDefault();
      });
    });  

    // TOOLTIP
    $('.social-links a').tooltip();

    // CONTACT FORM — Formspree AJAX
    var $form = $('#contact-form');
    var $status = $('#form-status');
    if ($form.length) {
      $form.on('submit', function(e) {
        e.preventDefault();
        var data = $form.serialize();
        $.ajax({
          url: $form.attr('action'),
          method: 'POST',
          data: data,
          dataType: 'json',
          success: function() {
            $form[0].reset();
            $status.text('Message sent! I will get back to you soon.').css('color', '#28a745').show();
          },
          error: function() {
            $status.text('Something went wrong. Please email me directly at erdem.unal96@gmail.com').css('color', '#dc3545').show();
          }
        });
      });
    }

})(jQuery);

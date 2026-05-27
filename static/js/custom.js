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

    // CONTACT FORM — AJAX with invisible proof-of-work CAPTCHA
    var $form = $('#contact-form');
    var $status = $('#form-status');

    async function sha256Bytes(str) {
      var buf = new TextEncoder().encode(str);
      var hash = await crypto.subtle.digest('SHA-256', buf);
      return new Uint8Array(hash);
    }

    async function computePoW(token, difficulty) {
      var n = 0;
      while (true) {
        var h = await sha256Bytes(token + '.' + n);
        var bits = (h[0] << 24) | (h[1] << 16) | (h[2] << 8) | h[3];
        if ((bits >>> (32 - difficulty)) === 0) return String(n);
        n++;
        if (n > 5000000) return '';
      }
    }

    if ($form.length && window.crypto && window.crypto.subtle) {
      var token = $form.data('captcha-token');
      var difficulty = parseInt($form.data('captcha-difficulty'), 10) || 14;
      var powPromise = computePoW(String(token), difficulty);

      $form.on('submit', function(e) {
        e.preventDefault();
        var $submit = $form.find('input[type=submit]');
        var origVal = $submit.val();
        $submit.prop('disabled', true).val('Sending…');

        powPromise.then(function(nonce) {
          $('#captcha_nonce').val(nonce);
          var data = $form.serialize();
          return $.ajax({
            url: $form.attr('action'),
            method: 'POST',
            data: data,
            dataType: 'json'
          });
        }).then(function() {
          $form[0].reset();
          $status.text('Message sent! I will get back to you soon.').css('color', '#28a745').show();
        }).catch(function() {
          $status.text('Something went wrong. Please email me directly at erdem.unal96@gmail.com').css('color', '#dc3545').show();
        }).then(function() {
          $submit.prop('disabled', false).val(origVal);
        });
      });
    }

})(jQuery);

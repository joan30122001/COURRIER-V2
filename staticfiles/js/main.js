(function() {

  'use strict';

  // preloader
  $(window).on('load', function() {
    $('.loader').fadeOut('slow');
  });

  // smooth scroll
  $("a").on("click", function(event) {

      if (this.hash !== "") {
          event.preventDefault();

          var hash = this.hash;

          $("html, body").animate({

              scrollTop: $(hash).offset().top - 50

          }, 850);

      }

  });

  // product filterizr
  $('.filtr-container').imagesLoaded( function() {
      var filterizr = $('.filtr-container').filterizr();
  });

  // product filter
  $('.product-filter-menu li').on('click', function() {
      $('.product-filter-menu li').removeClass('active');
      $(this).addClass('active');
  });

  // product magnific popup
  $('.product').each(function() { // the containers for all your galleries
      $(this).magnificPopup({
          delegate: '.product-popup', // the selector for portfolio item
          type: 'image',
          gallery: {
              enabled: true
          }
      });
  });


  // swiper slider
  $(document).ready(function () {
    var swiper = new Swiper(".mySwiper", {
      slidesPerView: 1,
      spaceBetween: 30,
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
      autoplay: {
        delay: 5000,
      },
      breakpoints: {
        0: {
          slidesPerView: 1,
        },
        768: {
          slidesPerView: 1,
        },
        780: {
          slidesPerView: 1,
        }
      }
    });
  });

  // navbar toggler icon
  $(document).on("click",".navbar-toggler",function(e){
      $(this).parent().siblings().find('i').removeClass('la-remove')
    $(this).find('i').toggleClass('la-remove')
  });

  // navbar on scroll
  $(window).on("scroll", function() {

      var onScroll = $(this).scrollTop();

      if( onScroll > 50) {
          $(".navbar").addClass("navbar-fixed");
      }
      else {
          $(".navbar").removeClass("navbar-fixed");
      }

  });

  // counter
  $('.number-counter').each(function () {
        $(this).prop('Counter',0).animate({
            Counter: $(this).text()
        }, {
            duration: 5000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
        });
    });

})();
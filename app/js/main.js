!function( $ ) {


  $('.gallery__img').magnificPopup({
    type: 'image',
    gallery: { enabled: true },
    // zoom: { enabled: true }
  });

  // Back to top link
  // =====================
  // when to show (pixels)
  var offset = 800,
  // when reduce opacity (pixels)
  offset_opacity = 1200,
  // duration ms
  scroll_top_duration = 700,
  // grab the back to top link
  $back_to_top = $('.cd-top');

  // hide or show the back to top link
  $(window).scroll(function(){
    ( $(this).scrollTop() > offset ) ? $back_to_top.addClass('cd-top--visible') : $back_to_top.removeClass('cd-top--visible cd-top--faded');
    if ( $(this).scrollTop() > offset_opacity ) { $back_to_top.addClass('cd-top--faded') }
  });

  // // smooth scroll to top
  // $('a[href^=#]').on('click', function(e){
  //   var href = $(this).attr('href');
  //   $(document).animate({
  //     scrollTop:$('a[name^='+$(this).attr('href').replace('#','')+']').offset().top },'slow');
  //     e.preventDefault();
  //   });
    $back_to_top.on('click', function(event){
        event.preventDefault();
        $('body,html').animate({
          scrollTop: 0 ,
          }, scroll_top_duration
        );
      });


  // Responsive Slides
  // ==================
    $(".rslides").responsiveSlides({
      auto: true,             // Boolean: Animate automatically, true or false
      speed: 800,            // Integer: Speed of the transition, in milliseconds
      timeout: 8000,          // Integer: Time between slide transitions, in milliseconds
      pager: true,           // Boolean: Show pager, true or false
      nav: true,             // Boolean: Show navigation, true or false
      random: false,          // Boolean: Randomize the order of the slides, true or false
      pause: true,           // Boolean: Pause on hover, true or false
      pauseControls: true,    // Boolean: Pause when hovering controls, true or false
      prevText: "Previous",   // String: Text for the "previous" button
      nextText: "Next",       // String: Text for the "next" button
      maxwidth: "800",           // Integer: Max-width of the slideshow, in pixels
      navContainer: "",       // Selector: Where controls should be appended to, default is after the 'ul'
      manualControls: "",     // Selector: Declare custom pager navigation
      namespace: "rslides",   // String: Change the default namespace used
      before: function(){},   // Function: Before callback
      after: function(){}     // Function: After callback
    });



  // Timeline
  // ========
  if ($('.timeline__wrapper').length) {
    console.log('timeline_exists');
    var $timeline_block = $('.timeline__wrapper');
    // hide timeline blocks that are not in the viewport
    $timeline_block.each(function(){
      if($(this).offset().top > $(window).scrollTop() + $(window).height() * 0.85) {
        $(this).find('.timeline__img, .timeline__content').addClass('invisible');
      }
    });
    // on scrolling show/animate timeline blocks when enter the viewport
    $(window).on('scroll', function(){
      $timeline_block.each(function(){
        if($(this).offset().top <= $(window).scrollTop()+$(window).height() * 0.85 &&
           $(this).find('.timeline__img').hasClass('invisible')) {
          $(this).find('.timeline__img, .timeline__content').removeClass('invisible').addClass('bounce-in');
        }
      });
    });
  };

}( window.jQuery )



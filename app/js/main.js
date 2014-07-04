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

  // Timeline
  // ========
  var $timeline_block = $('.timeline__wrapper');
  // hide timeline blocks that are not in the viewport
  $timeline_block.each(function(){
    if($(this).offset().top > $(window).scrollTop() + $(window).height() * 0.75) {
      $(this).find('.timeline__img, .timeline__content').addClass('invisible');
    }
  });
  // on scrolling show/animate timeline blocks when enter the viewport
  $(window).on('scroll', function(){
    $timeline_block.each(function(){
      if($(this).offset().top <= $(window).scrollTop()+$(window).height()*0.75 &&
         $(this).find('.timeline__img').hasClass('invisible')) {
          $(this).find('.timeline__img, .timeline__content').removeClass('invisible').addClass('bounce-in');
      }
    });
  });



}( window.jQuery )



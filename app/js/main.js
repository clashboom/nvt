$('.post__article').scrollNav({
  sections: 'h2',
  subSections: false,
  sectionElem: 'section',
  showHeadline: false,
  headlineText: 'Scroll To',
  showTopLink: false,
  topLinkText: 'Top',
  fixedMargin: 60,
  scrollOffset: 20,
  animated: true,
  speed: 500,
  insertTarget: this.selector,
  insertLocation: 'insertBefore',
  arrowKeys: true,
  onInit: null,
  onRender: null,
  onDestroy: null
});

var $item = $('.scroll-nav__item');
$.each($item, function(){
  $text = $(this).find('a').html().toLowerCase();
  $(this).addClass($text);
});


$('.gallery__img').magnificPopup({type: 'image',
                                  gallery: { enabled: true }});

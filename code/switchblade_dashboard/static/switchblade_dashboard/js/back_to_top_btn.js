
$('#back-to-top').on('click', function(e) {
    e.preventDefault();
    $('.content-wrapper').animate({scrollTop:0, scrollLeft:0}, '300');
});

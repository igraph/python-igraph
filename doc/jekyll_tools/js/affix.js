
var $window = $(window);
var $body   = $(document.body);

$body.scrollspy({ target: '.bs-sidebar' });

$window.on('load', function () {
    $body.scrollspy('refresh');
});


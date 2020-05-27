$('.answers').on('click', function() {
    var target = '.'.concat(this.id,'_', 'answers');
    $(target).toggleClass('hidden');
});


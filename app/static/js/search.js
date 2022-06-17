$('.search_button').on('click', function(){
    var text = $('.search_input').val();
    window.location.href = '/shop_list_new/'+ text;
})
(function(){
    if(!window.bookmarklet){
        var bookmarklet_js = document.createElement('script');
        bookmarklet_js.src = 'https://127.0.0.1:8000/static/js/bookmarklet.js?r='+Math.floor(Math.random()*9999999999999999);
        document.body.appendChild(bookmarklet_js);
        window.bookmarklet = true;
    }
    else{
        bookmarkletLaunch();
    }
})();
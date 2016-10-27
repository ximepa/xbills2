$( document ).ready(function() {
    $('.ui.dropdown').dropdown();
    $('.menu .item').tab();
    $('.sticky').sticky();
    $('.popup').popup();
    $('#search_panel').accordion();
    $('#sideBar').accordion({
        onOpen: function () {
            console.log($('#sideBar'))
        },
        onOpening:function (event, ui) {
            console.log(event)
            console.log(ui)
        }
    //    exclusive: false
    });
    $('#session').popup({
        popup : $('#browse'),
        on    : 'click',
        inline     : false,
        hoverable  : false,
        position   : 'bottom left',
        delay: {
            show: 300,
            hide: 800
        }
    });
});

function hideSidebar() {
    var context = $('#main_context');
    $('#sideBar').toggle();
    if ($("#sideBar").is(":visible") == true) {
        context.css({'width': '87.5%'});
    } else {
        context.css({'width': '100%'});
    }
}

function servicesToggle() {
    $('#services').toggle();
    setCookie('services', $("#services").css('display'))
}

function setCookie(cname, value) {
    $.cookie(cname, value, { path:'/' } );

}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}


function formatBytes(bytes,decimals) {
   if(bytes == 0) return '0 Byte';
   var k = 1024; // or 1024 for binary
   var dm = decimals + 1 || 3;
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
   var i = Math.floor(Math.log(bytes) / Math.log(k));
   return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
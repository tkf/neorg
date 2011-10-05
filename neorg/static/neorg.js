function openFirstImageByColorBox() {
    $.colorbox($.extend({}, neorgCBSetting, {
        href: $('img.neorg-gene-image').first().attr('src')
    }));
}

function neorgCBOpen(arrow) {
    var otd, oa;
    var ctd = $.colorbox.element().parent();
    if (arrow == 'left') {
        otd = ctd.prev();
    } else if (arrow == 'right') {
        otd = ctd.next();
    } else {
        var ctr = ctd.parent();
        var idx = ctr.children().index(ctd[0]);
        var otr;
        if (idx == undefined) {
            return;
        }
        if (arrow == 'up') {
            otr = ctr.prev();
        } else if (arrow == 'down') {
            otr = ctr.next();
        }
        otd = otr.children().eq(idx);
        // alert(idx + arrow + otd.text());
    }
    oa = otd.children('a.neorg-gene-image-link').first();
    if (oa.length) {
        oa.click();
    }
}

function neorgCBOpenLeft() {
    neorgCBOpen('left');
}

function neorgCBOpenRight() {
    neorgCBOpen('right');
}

function neorgCBOpenUp() {
    neorgCBOpen('up');
}

function neorgCBOpenDown() {
    neorgCBOpen('down');
}

function bindKeydown(key, func) {
    $(document).bind('keydown.neorg.' + key, key, func);
}

function unBindKeydown(key, func) {
    $(document).unbind('keydown.neorg.' + key);
}


$(document).ready(function() {
    $('.neorg-gene-image-link').colorbox(neorgCBSetting);
});


var neorgCBSetting = {
    title: function() {
        $(this).attr('title', $(this).prev('p').text());
    },
    transition: 'none',
    speed: 0,
    maxWidth: '100%',
    maxHeight: '100%',
    fixed: true,
    onOpen: function() {
        // alert('onOpen');
        bindKeydown('left', neorgCBOpenLeft);
        bindKeydown('right', neorgCBOpenRight);
        bindKeydown('up', neorgCBOpenUp);
        bindKeydown('down', neorgCBOpenDown);
    },
    onClosed: function() {
        // alert('onClosed');
        unBindKeydown('left');
        unBindKeydown('right');
        unBindKeydown('up');
        unBindKeydown('down');
    }
};

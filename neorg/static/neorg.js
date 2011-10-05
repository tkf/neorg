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

function bindKeydown(key, func) {
    $(document).bind('keydown.neorg.' + key, key, func);
}

function bindKeydownToNeorgCBOpen(key) {
    bindKeydown(key, function(e) {
        e.preventDefault();
        neorgCBOpen(key);
    });
}

function unBindKeydown(key) {
    $(document).unbind('keydown.neorg.' + key);
}


$(document).ready(function() {
    $('.neorg-gene-image-link').colorbox(neorgCBSetting);
});


var arrowKeyArray = ['left', 'right', 'up', 'down']

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
        var i;
        for (i in arrowKeyArray) {
            bindKeydownToNeorgCBOpen(arrowKeyArray[i]);
        }
    },
    onClosed: function() {
        // alert('onClosed');
        var i;
        for (i in arrowKeyArray) {
            unBindKeydown(arrowKeyArray[i]);
        }
    }
};

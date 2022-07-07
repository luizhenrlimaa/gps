'use strict';

function removeAllBreakLines(text) {

    if (!text) {
        return;
    }

    return text.replace(/(\r\n|\n|\r)/gm, "");
}

function cleanString(text) {

    if (!text) {
        return;
    }

    return text.replace(/[\W_]+/g,' ').trim();
}

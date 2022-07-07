
function showContentOnIframe(pageId, pageUrl) {
    startSpinner();
    hideCurrentContent(pageId);

    if (isPageAlreadyRendered(pageId)) {
        showPage(pageId);
    } else {
        let newContentIframe = '<iframe id="' + pageId + '" ' +
                                    ' src="' + pageUrl + '" '  +
                                    ' class="inner-page"> ' +
                                '</iframe> ';

        $('#iframe-section').append(newContentIframe);
    }

    selectSidebarMenu(pageId);
    updateBrowserUrl(pageUrl);
    setTimeout(() => { stopSpinner(); }, 2000);
}

function hideCurrentContent(pageId) {
    $('.content-wrapper').css('overflow-y', 'hidden');

    $('.inner-page').each( (index, value) => {
        if ($(value).attr('id') != pageId) {
            $(value).hide();
        } else {
             $(value).show();
        }
    });

    $('.content-header').remove();
    $('.content').remove();
}

function isPageAlreadyRendered(pageId) {
    return $('#iframe-section').find('#' + pageId).length == 1;
}

function selectSidebarMenu(pageId) {
    $('.main-sidebar').find('li.active').removeClass('active');
    $('.main-sidebar').find('#' + pageId).addClass('active');
}

function updateBrowserUrl(pageUrl, extraUrl = null) {
    let newUrl = pageUrl;

    if (extraUrl) {
        newUrl += "/" + extraUrl;
    }

    // Verify if Browser supports pushState() method
    if (window.history.pushState) {
        window.history.replaceState('', '', newUrl);
    } else {
        // Used by old versions browser
        document.location.href = "/" + newUrl;
    }
}

function showPage(pageId) {
    $('#' + pageId).show();
}

function startSpinner() {
    $('#iframe-loading').show();
}

function stopSpinner() {
    $('#iframe-loading').hide();
}

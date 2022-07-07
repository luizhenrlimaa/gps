function getCsrfTokenHeader() {
    return {
        headers: {'X-CSRFToken': csrfToken,}
    };
}

function getCurrentUrl() {
    return `${window.location.href.match(/^[^\#\?]+/)[0]}`;
}

function errorCallBack(error) {
    notify(error.message, 'danger');
}
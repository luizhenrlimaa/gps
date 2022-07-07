
function getElementHeight(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    return element ? element.offsetHeight : 0;
}

function hideElement(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element) {
        return;
    }

    if (['none', 'unset'].includes(element.style.display)) {
        element.style.display = '';
    }

    element.hidden = true;
}

function showElement(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element) {
        return;
    }

    if (!element.style.display || 'none' === element.style.display) {
        element.style.display = 'unset';
    }

    element.hidden = false;
}

function hideElements(query) {

    if (!query) {
        return;
    }

    let elements = document.querySelectorAll(query);

    if (!elements || elements.length == 0) {
        return;
    }

    elements.forEach((element) => {

        if (element.classList.value.includes('modal in')) {
            console.log(element);
            element.classList.remove('in');
            element.style.display = 'none';
            return;
        }

        if (['none', 'unset'].includes(element.style.display)) {
            element.style.display = '';
        }

        element.hidden = true;
    });
}

function showElements(query) {

    if (!query) {
        return;
    }

    let elements = document.querySelectorAll(query);

    if (!elements || elements.length == 0) {
        return;
    }

    elements.forEach((element) => {
        if (!element.style.display || 'none' === element.style.display) {
            element.style.display = 'unset';
        }

        element.hidden = false;
    });
}

function hideModalElement(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element || !element.classList.value.includes('in')) {
        return;
    }

    element.classList.remove('in');
    element.style.display = 'none';

    let contentElement = document.querySelector('.content');

    if (!contentElement) {
        contentElement = document.querySelector('.content-wrapper');
    }

    contentElement.style.filter = 'blur(0px)';
    document.querySelectorAll('.modal-backdrop.fade.in').forEach((modalBackdropElement) => modalBackdropElement.remove());
}

function showModalElement(query, dismissingFunction) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element) {
        return;
    }

    document.body.appendChild(element);

    document.querySelectorAll(query + ' [data-dismiss="modal"]').forEach((elm) => {
        elm.removeAttribute('data-dismiss');
        elm.addEventListener('click', () => { dismissingFunction ? dismissingFunction : hideModalElement(query);  });
    });

    hideElements('.modal.in');
    element.classList.add('in');
    element.style.display = 'block';

    let contentElement = document.querySelector('.content');

    if (!contentElement) {
        contentElement = document.querySelector('.content-wrapper');
    }

    contentElement.style.filter = 'blur(3px)';

    let modalBackdropElement = document.querySelector('.modal-backdrop.fade.in');

    if (modalBackdropElement) {
        return;
    }

    let modalBackdropHtml = '<div class="modal-backdrop fade in" onclick="closeModal()"></div>';
    modalBackdropElement = document.createRange().createContextualFragment(modalBackdropHtml);

    contentElement.appendChild(modalBackdropElement);
}

function closeModal() {
    let closableModalElement = document.querySelector('.modal.close-on-click-outside');

    if (!closableModalElement) {
        return;
    }

    closableModalElement.classList.remove('in');
    closableModalElement.style.display = 'none';
    document.querySelectorAll('.modal-backdrop').forEach((elm) => elm.remove());

    let contentElement = document.querySelector('.content');

    if (!contentElement) {
        contentElement = document.querySelector('.content-wrapper');
    }

    contentElement.style.filter = 'blur(0px)';
}

function disableElement(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element) {
        return;
    }

    element.disabled = true;
}

function enableElement(query) {

    if (!query) {
        return;
    }

    let element = document.querySelector(query);

    if (!element) {
        return;
    }

    element.disabled = false;
}

// TODO-DEV: Find a alternative to replace jQuery datePicker
function clearDatePickerInput(query) {

    if (!query) {
        return;
    }

    let element = $(query);

    if (element.length == 0) {
        return;
    }

    element.data("DateTimePicker").clear();
}

// TODO-DEV: Find a lib to replace jQuery notify
function notify(message, type) {

    if (!message) {
        return;
    }

    if ('danger' === type) {
        $.notify(message, {type: 'danger'});
    } else if ('warning' === type) {
        $.notify(message, {type: 'warning'});
    } else if ('info' === type) {
        $.notify(message, {type: 'info'});
    } else {
        $.notify(message, {type: 'success'});
    }
}

// TODO-DEV: Find a lib to replace $.dataTables
document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll('.modal-dialog.modal-content').forEach((elm) => {
            elm.addEventListener('click', (event) => {
                event.stopPropagation();
            });
        });
});

let celeryTaskId = 0,
    checkCeleryTaskStateInterval,
    processingMessageInterval,
    processingMessageIntervalCounter = 0,
    pendingIconInterval,
    pendingIconIntervalCounter = 0,
    pendingIconArray = ['fa-hourglass-o', 'fa-hourglass-1', ' fa-hourglass-2', ' fa-hourglass-3'],
    celeryIconElement,
    celeryMessageElement;

// CELERY STATES CONSTANTS
const API_URL = '/api/async-task-status/',
      PROCESSING = ['RECEIVED', 'STARTED'],
      DONE = ['SUCCESS'],
      FAILED = ['FAILURE', 'RETRY'],
      REVOKED = ['REVOKED'],
      UNKNOWN = ['PENDING'],
      PROCESSING_MESSAGE = 'Generating report.',
      PROCESSING_MESSAGE_EXTRA = 'If the report is very large, an XLS will be generated even if you have selected to generate it on the screen.',
      SUCCESS_MESSAGE = 'Report generated successfully.\nThe report will be displayed soon or will be available in your downloads folder.\nDo not refresh this page.',
      FAILED_MESSAGE = 'Something went wrong. Please, contact support.',
      REVOKED_MESSAGE = 'Report generation canceled.';
      UNKNOWN_MESSAGE = 'Report may be on the queue to be processed. Please, hold on.\nIn case you have already processed/viewed it, please, generate it again.';

function renderReport() {
    hideButton();
    celeryIconElement.classList = 'fa fa-check celery__icon success';
    celeryMessageElement.innerText = SUCCESS_MESSAGE;
    window.location.href = `${getCurrentUrl()}?task_id=${celeryTaskId}`;
}

function renderError() {
    hideButton();
    celeryIconElement.classList = 'fa fa-exclamation-triangle celery__icon error';
    celeryMessageElement.innerText = FAILED_MESSAGE;
}

function renderUnknown() {
    hideButton();
    celeryMessageElement.innerText = UNKNOWN_MESSAGE;
    celeryIconElement.classList = 'fa fa-hourglass-o fa-spin celery__icon unknown';
}

function renderRevoke() {
    hideButton();
    celeryIconElement.classList = 'fa fa-user-times celery__icon revoke';
    celeryMessageElement.innerText = REVOKED_MESSAGE;
}

function renderProcessing() {
    showElement('.celery__button');
    celeryIconElement.classList = 'fa fa-refresh fa-spin celery__icon';

    if (processingMessageInterval) {
        return;
    }

    celeryMessageElement.innerText = `${PROCESSING_MESSAGE}\n${PROCESSING_MESSAGE_EXTRA}`;

     processingMessageInterval = setInterval(() => {
        if (processingMessageIntervalCounter >= 4) {
            processingMessageIntervalCounter = 0;
        }

        let endMessage = '';

        for (let i=1; i<=processingMessageIntervalCounter; i++) {
            endMessage += '.';
        }

        celeryMessageElement.innerText = `${PROCESSING_MESSAGE}${endMessage}\n${PROCESSING_MESSAGE_EXTRA}`;
        processingMessageIntervalCounter++;
    }, 1000);
}

function hideButton() {
    document.querySelector('.celery__button').style.display = 'none';
}

function revokeReport() {
    axios.get(`${API_URL}?task_id=${celeryTaskId}&revoke=true`
    ).then((response) => {
        setTimeout(() => {
            checkCeleryTaskState();
        }, 1000);
    }).catch(errorCallBack);
}

function checkCeleryTaskState() {

    axios.get(`${API_URL}?task_id=${celeryTaskId}`
    ).then((response) => {

        if (!response.data) {
            return;
        }

        let state = response.data.state;

        if (!state || FAILED.includes(state)) {
            clearInterval(processingMessageInterval);
            clearInterval(checkCeleryTaskStateInterval);
            renderError();
            return;
        }

        if (REVOKED.includes(state)) {
            clearInterval(processingMessageInterval);
            clearInterval(checkCeleryTaskStateInterval);
            renderRevoke();
            return;
        }

        if (UNKNOWN.includes(state)) {
            clearInterval(processingMessageInterval);
            renderUnknown();
            return;
        }

        if (DONE.includes(state)) {
            clearInterval(processingMessageInterval);
            clearInterval(checkCeleryTaskStateInterval);
            renderReport();
            return;
        }

        renderProcessing();
    }).catch(errorCallBack);
}

function disableF5(event) {
    if ([116, 82].includes(event.which || event.keyCode)) {
        event.preventDefault();
    }
}

document.addEventListener('keydown', disableF5);
document.addEventListener('DOMContentLoaded', () => {

    setTimeout(() => {
        if (!celeryTaskId) {
            return;
        }

        let celeryTaskIdElement = document.querySelector('#celery-task');

        if (celeryTaskIdElement) {
            celeryTaskIdElement.innerText = celeryTaskId;
            document.body.appendChild(celeryTaskIdElement);
        }

        document.querySelector('.content-wrapper').style.overflow = 'hidden';

        celeryIconElement = document.querySelector('.celery__icon');
        celeryMessageElement = document.querySelector('.celery__message');

        checkCeleryTaskState();

         checkCeleryTaskStateInterval = setInterval(() => {
            checkCeleryTaskState();
        }, 30000);
    }, 500);
});
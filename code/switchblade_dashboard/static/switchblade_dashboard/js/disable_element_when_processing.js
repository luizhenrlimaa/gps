
class Listener {

    constructor(element) {
        this.setElement(element);
        this.setId(element);
        this.setClickedTimes(0);
        this.setOriginalOnclickEvent(element);
        this.setRequestUrl(element);

        this.setOriginalIcon(element);
        this.setOriginalText(element);
        this.setOriginalTooltip(element);
    }

    getElement() {
        return this.element;
    }

    setElement(element) {
        this.element = element;
    }

    getId() {
        return this.id;
    }

    setId(element) {
        let elementId = element.attr('id');

        if (!elementId) {
            let randomId = Math.random().toString(36).substring(2);
            element.attr('id', randomId);
            elementId = randomId;
        }

        this.id = elementId;
    }

    getClickedTimes() {
        return this.clickedTimes;
    }

    setClickedTimes(quantity) {
        this.clickedTimes = quantity;
    }

    getOriginalOnclickEvent() {
        return this.originalOnClickEvent;
    }

    setOriginalOnclickEvent(element) {
        this.originalOnClickEvent = element.attr('onclick');
    }

    getRequestUrl() {
        return this.requestUrl;
    }

    setRequestUrl(element) {
         let listenerPropValue = element.attr('listener-url');

         listenerPropValue.endsWith('/') ? listenerPropValue : listenerPropValue + '/' ;
         listenerPropValue.startsWith('/') ? listenerPropValue.substr(1) : listenerPropValue;

         this.requestUrl = serverUrl + listenerPropValue;
    }

    getOriginalTooltip() {
        return this.originalTooltip;
    }

    setOriginalTooltip(element) {
        this.originalTooltip = element.find('.tooltip-text');
    }

    increaseClickedTimes() {
        this.clickedTimes++;
    }

   decreaseClickedTimes() {
        this.clickedTimes--;
    }

    cleanOnclickEvent() {
        this.getElement().attr('onclick', '');
    }

    restoreOnclickEvent() {
        this.getElement().attr('onclick', this.getOriginalOnclickEvent());
    }

    disableElement() {
        this.getElement().addClass('processing');
        this.cleanOnclickEvent();

        let label = this.getElement().attr('listener-label');
        this.getElement().text(label ? label : 'Processing...');

        this.element.append('<i class="fa fa-refresh fa-spin pull-left" style="margin-top: 3px;"></i> ');

        document.dispatchEvent(new CustomEvent("button-listener-start", { detail: this.getRequestUrl()}));
    }

    skipLastListener() {
        this.decreaseClickedTimes();
    }

    enableElement() {
        this.getElement().removeClass('processing');
        this.restoreOnclickEvent();

        this.getElement().text(this.getOriginalText());
        this.element.append('<i class="' + this.getOriginalIcon() + ' pull-left" style="margin-top: 3px;"></i> ');

        let tooltip = this.getElement().attr('listener-tooltip');

        if (tooltip) {
            setTimeout(() => {
                this.getElement().addClass('has-tooltip');
                this.getElement().append('<span class="tooltip-text">' + tooltip + '</span>');
            }, 300);
        }

        document.dispatchEvent(new CustomEvent("button-listener-end", { detail: this.getRequestUrl() }));
    }

    getOriginalIcon() {
        return this.originalIcon;
    }

    setOriginalIcon(element) {
        this.originalIcon = element.find('i').attr('class');
    }

    getOriginalText() {
        return this.originalText;
    }

    setOriginalText(element) {
         this.originalText = element.text();
    }
}

let listenerList = [];
let serverUrl = document.URL.split('/')[0] + '//' + document.URL.split('/')[2] + '/';

function findListenerByUrl(url) {
    let listeners = listenerList.filter((listener) => listener.getRequestUrl() === serverUrl + url);

    if (listeners.length == 0) {
        return;
    }

    return listeners[0];

}

function findAllCustomElmListeners() {
    return $('[listener-url]');
}

function findListener(element) {
    return listenerList.filter((listener) => listener.getId() == element.attr('id'));
}

function onclickCustomPropListener(element) {
    element = $(element);
    let listener = findListener(element);

    if (listener) {
        listener[0].disableElement();
        listener[0].increaseClickedTimes();
    }
}

function initListener(element) {
    element.attr('onclick', element.attr('onclick') + '; onclickCustomPropListener(this);');

    listenerList.push(new Listener(element));
}

$(document).ready(function() { findAllCustomElmListeners().each((index, value) => initListener($(value))); });

setInterval(function() {

    listenerList.forEach((listener) => {
        let responseTimes = window.performance.getEntriesByType('resource')
                                             .filter((e) => e.initiatorType == 'xmlhttprequest'
                                                            && e.name.split('?')[0] == listener.getRequestUrl()).length;

        if (responseTimes == listener.getClickedTimes()) {
            listener.enableElement();
        }
    });

}, 1000);
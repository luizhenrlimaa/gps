function elementJump(selector, times) {

    let elm = document.querySelector(selector);

    if (!elm) {
        return;
    }

    elm.classList.add('jumper');

    if (!times) {
        times = 1;
    }

    Array.from(Array(times).keys()).forEach((counter) => setTimeout(() => { activeElementEffect(elm); }, (counter*500) ));
}

function activeElementEffect(elm, duration) {

    if (!elm || !elm.classList) {
        return;
    }

    if (!duration) {
        duration = 200;
    }

    elm.classList.add('active');
    setTimeout(() => { elm.classList.remove('active'); }, duration);
}
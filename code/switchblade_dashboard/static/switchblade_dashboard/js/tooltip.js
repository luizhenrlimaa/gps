
function addTooltip(value, tooltipText) {
    let elm = $(value);
    elm.addClass('has-tooltip');
    elm.append('<span  class="tooltip-text">' + tooltipText + '</span>');
}

function startupTooltips() {
    let elementsToAddTooltip = $('[tooltip]');
    elementsToAddTooltip.each((index, value) => addTooltip(value, $(value).attr('tooltip')));
}

document.addEventListener("DOMContentLoaded", () => {
    $('[data-toggle="tooltip"]').tooltip();
    startupTooltips();
});
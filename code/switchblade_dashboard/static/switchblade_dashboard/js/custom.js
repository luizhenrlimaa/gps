'use strict';

let csrfToken = null;
let filterLoaded = false;
let filterLoading = false;

setTimeout(() => { filterLoaded = true; }, 2000);

function clearField(parent, fields) {

    if (!filterLoaded || filterLoading) {
        return;
    }

    let parentName = parent.name.split('-').pop();

    let fieldsToClear = fields.split(',');

    for (let index in fieldsToClear) {
        let fieldToClear = parent.name.replace(parentName, fieldsToClear[index]);
        $('#id_' + fieldToClear).val(null).trigger("change");
        $('#id_' + fieldToClear + ' option').remove();
    }
}

function cleanNonSelectSideBarItem() {
    if ($('.main-sidebar').find('li.active').length > 1) {
        $('.main-sidebar').find('li.active').first().removeClass('active');
    }
    $.holdReady( false );
}
$.holdReady( true );
cleanNonSelectSideBarItem();

function adjustSidebarLayoutOnSmallWindow() {
    let body = $('body');

     if (window.innerWidth < 767) {
        body.removeClass('sidebar-collapse');
     }
}

function setContentNoScroll() {
    if (document.querySelectorAll('.tabbed-box, #table-template').length == 2) {
        document.querySelector('.content-wrapper').style.overflow = 'hidden';
    }
}

function setDataTableHeight() {

    let dataTableElements = document.querySelectorAll(".dataTables_scrollBody");
    let tabbedBoxElement = document.querySelector('.tabbed-box');

    if (dataTableElements.length == 0 || !tabbedBoxElement) {
        return;
    }

    let tabbedBoxHeight = 0;

    let tabbedBoxMinimizedBtn = document.querySelector('.nav-filter-button .fa.fa-chevron-left');
    let alertElement = document.querySelector('.alert');

    if (tabbedBoxElement) {
        let height = tabbedBoxElement.offsetHeight;
        tabbedBoxHeight = tabbedBoxMinimizedBtn ? (height - 5) : height;
    }

    if (alertElement) {
        tabbedBoxHeight = (tabbedBoxHeight - alertElement.offsetHeight) - 20;
        let closeAlertBtnElement = document.querySelector('.alert button.close');

        if (closeAlertBtnElement) {
            closeAlertBtnElement.addEventListener('click', () => { setTimeout(() => { setTableHeight(); }, 300); });
        }
    }

    let tableMaxHeight = (window.innerHeight - tabbedBoxHeight - 190) + (window.outerWidth < 1367 ? 34 : 0) + "px";


    dataTableElements.forEach((dataTableElement) => {
        dataTableElement.style.maxHeight = tableMaxHeight;
        dataTableElement.style.overflow = 'scroll';
    });
}

function setTableHeight() {
    let tableElement = document.querySelector('.table-container.table-responsive');
    let alertElement = document.querySelector('.alert');

    if (!tableElement) {
        return;
    }

    let tabbedBoxElement = document.querySelector('.tabbed-box');
    let paginationElement = document.querySelector('.pagination');
    let tableHeight = window.innerHeight - ((tabbedBoxElement ? tabbedBoxElement.offsetHeight : 0) + (paginationElement ? 154 : 115));

    if (alertElement) {
        tableHeight = (tableHeight - alertElement.offsetHeight) - 20;
        let closeAlertBtnElement = document.querySelector('.alert button.close');

        if (closeAlertBtnElement) {
            closeAlertBtnElement.addEventListener('click', () => { setTimeout(() => { setTableHeight(); }, 300); });
        }
    }

    tableElement.style.maxHeight = tableHeight + 'px';
}

function setTablesHeight() {
    setTableHeight();
    setDataTableHeight();
}

$(window).resize(() => {
    setDataTableHeight();
});

// Init Select2
$('.select2').select2({
    allowClear: true
});

// ------------------------------
// On Document Ready
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {

    // Init
    $(document).ajaxStart(() => {
        try {
            Pace.restart();
        } catch(error) {
            // pace is not defined, so, ignore it
        }
    });

    // Init notify
    $.notifyDefaults({
        type: 'info',
        delay: 2000,
        offset: {
            x: 20,
            y: 60
        }
    });

    // Applied globally on all textareas with the "autoExpand" class
    $(document).one('focus.autoExpand', 'textarea.autoExpand', function() {
        let savedValue = this.value;
        this.value = '';
        this.baseScrollHeight = this.scrollHeight;
        this.value = savedValue;
    }).on('input.autoExpand', 'textarea.autoExpand', function() {
        let minRows = this.getAttribute('data-min-rows')|0, rows;
        this.rows = minRows;
        rows = Math.ceil((this.scrollHeight - this.baseScrollHeight) / 16);
        this.rows = minRows + rows;
    });

    // Init date element
    $('.date-range').daterangepicker({
        opens: 'center',
        autoUpdateInput: false,
        locale: {
            cancelLabel: 'Clear',
            format: 'YYYY-MM-DD'
        }
    });

    // Init date element
    $('.date-range').on('apply.daterangepicker', function(ev, picker) {
        if (picker.startDate.format('YYYY-MM-DD') === picker.endDate.format('YYYY-MM-DD')) {
            $(this).val(picker.startDate.format('YYYY-MM-DD'));
        } else {
            $(this).val(picker.startDate.format('YYYY-MM-DD') + ' until ' + picker.endDate.format('YYYY-MM-DD'));
        }
    });

    // Init date element
    $('.date-range').on('cancel.daterangepicker', function(ev, picker) {
      $(this).val('');
    });

    // Init date element
    $('.date-time-range').daterangepicker({
        opens: 'left',
        timePicker: true,
        autoUpdateInput: false,
        timePicker24Hour: true,
          locale: {
              cancelLabel: 'Clear',
          }
    });

        // Init date element
    $('.date-time-range').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    // Init date element
    $('.date-time-range').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm') + ' until ' + picker.endDate.format('YYYY-MM-DD HH:mm'));
    });

    // Handlers for tables height
    document.querySelectorAll('.tabbed-box #filter-badges li').forEach((element) => {
        element.addEventListener('click', () => {
            setTimeout(() => { setTablesHeight(); }, 50);
        });
    });
    $('.nav-filter-button').on('click', () => { setTimeout(() => { setTablesHeight(); }, 50); });
    setTimeout(() => { setTablesHeight(); }, 1000);
    setContentNoScroll();

    // Add event click on calendar icons to show date range picker
    $(".input-group i.fa.fa-calendar").each(function( index, value ) {
        $(value).parent().bind( "click", {
              element_id: $(value).parent().parent().find('input').attr('id')
            }, function(event) {

                if (!event.data.element_id) {
                    return;
                }

                let element = $('#' + event.data.element_id);

                if (element.length == 0) {
                    return;
                }

                element.click();
        });
    });

    adjustSidebarLayoutOnSmallWindow();
});
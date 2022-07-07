function change_icon(element_id, new_icon_class) {
    if (!element_id) {
        return;
    }

    let icon_el = document.getElementById(element_id);

    if(icon_el) {
        icon_el.className = new_icon_class;
    }

    if (new_icon_class == 'fa fa-chevron-down') {
        $('#table-container').attr('style', 'margin-top: 0;');
    } else {
        $('#table-container').attr('style', 'margin-top: -5px;');
    }
}

function remove_selected_tab_classes() {
    $('.box-tabs').find('ul').find('li').removeClass('active');
    $('.box-tabs').find('ul').find('li').find('a').removeClass('selected');
}

function hide_tabbed_box_content() {
    let box_tabs_element = $('.box-tabs-content');
    box_tabs_element.removeClass('collapsed-box');
    box_tabs_element.hide();
    change_icon('show-hide-search-box-button', 'fa fa-chevron-left');
    remove_selected_tab_classes();
}

function show_tabbed_box_content() {
    let box_tabs_element = $('.box-tabs-content');
    box_tabs_element.addClass('collapsed-box');
    box_tabs_element.show();
    change_icon('show-hide-search-box-button', 'fa fa-chevron-down');
}

function hide_or_show_tabbed_box_content() {
    classes = document.getElementsByClassName('box-tabs-content')[0].className;
    if (classes.includes('collapsed-box')) {
        hide_tabbed_box_content();
    } else {
        let box_tabs = $('.box-tabs').find('ul').find('li.default-tab').find('a');
        box_tabs.click();
    }
}

function initializeTabbedBox() {
    $('.tabbed-box').find('ul.nav-tabs').find('li').bind('click', show_tabbed_box_content);
    $('.header-tab').prop("onclick", null).off("click");
    $('.tabbed-box').find('.nav-filter-button').bind('click', hide_or_show_tabbed_box_content);
}

$(document).ready(function () {

    $(function initSearchBox() { show_tabbed_box_content() });

    initializeTabbedBox();

});
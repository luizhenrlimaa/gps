// *** Page ***//

function setCustomContextMenu(el, relevantActions=[], callback=null, target='contextMenu') {

    $(`#${el}`).off('contextmenu');

    if (callback) {
        $(`#${el}`).contextMenu({
            menuSelector: `#${target}`,
            menuSelected: callback,
            relevantActions: relevantActions
        });
    } else {
        $(`#${el}`).contextMenu({
            menuSelector: `#${target}`,
            menuSelected: function (invokedOn, selectedMenu) { /* Callback function example */ },
            relevantActions: relevantActions
        });
    }
}

// *** Components *** //

function serializeForm(form, formPrefix=null, skipHiddenFields=true) {

    let formData = {};
    formPrefix = (formPrefix) ? formPrefix + "-" : formPrefix;

	Array.prototype.slice.call(form.elements).forEach(function (field) {
		if (!field.name || field.disabled || ['file', 'reset', 'submit', 'button'].indexOf(field.type) > -1) return;

		if(skipHiddenFields && field.type === 'hidden'){
		    return;
        }

		if (field.type === 'select-multiple') {
			Array.prototype.slice.call(field.options).forEach(function (option) {
				if (!option.selected) return;

				let name = (formPrefix) ? field.name.split(formPrefix)[1] : field.name;

				if (name in formData){
                    formData[name].push(option.value)
                } else {
				    formData[name] = [option.value]
                }

			});
			return;
		}

		if (['checkbox', 'radio'].indexOf(field.type) > -1) {
			let name = (formPrefix) ? field.name.split(formPrefix)[1] : field.name;
			formData[name] = field.checked;
			return;
		}

		if (!field.value){
		    return;
        }

		let name = (formPrefix) ? field.name.split(formPrefix)[1] : field.name;

		formData[name] = field.value;
	});

	return formData;
};

// *** Events *** //

setTimeout(() => {
    $('#pages').on('slid.bs.carousel', function () { dashboard.resizeComponents(); });
}, 500);

(function ($, window) {

    // Resize
    $(window).resize(() => { dashboard.resizeComponents(); });

    // Context Menu
    $.fn.contextMenu = function (settings) {

    	return this.each(function () {

            // Open context menu
            $(this).on("contextmenu", function (e) {

            	// Return native menu if pressing control
                if (e.ctrlKey) return;

                // Hide all actions
                $(`${settings.menuSelector} > li`).hide();

                // Display the relevant actions
                settings.relevantActions.forEach((action) =>{
                    $(`#${action}`).show();
                });

                // Open menu
                let $menu = $(settings.menuSelector)
                    .data("invokedOn", $(e.target))
                    .show()
                    .css({
                        position: "absolute",
                        left: getMenuPosition(e.clientX, 'width', 'scrollLeft'),
                        top: getMenuPosition(e.clientY, 'height', 'scrollTop')
                    })
                    .off('click')
                    .on('click', 'a', function (e) {
                        $menu.hide();

                        let $invokedOn = $menu.data("invokedOn");
                        let $selectedMenu = $(e.target);

                        settings.menuSelected.call(this, $invokedOn, $selectedMenu);
                    });

                return false;
            });

            // Make sure menu closes on any click
            $('body').click(function () {
                $(settings.menuSelector).hide();

                // Hide all actions
                $(`${settings.menuSelector} > li`).hide();
            });
        });

        function getMenuPosition(mouse, direction, scrollDir) {
            let win = $(window)[direction](),
                scroll = $(window)[scrollDir](),
                menu = $(settings.menuSelector)[direction](),
                position = mouse + scroll;

            // Opening menu would pass the side of the page
            if (mouse + menu > win && menu < mouse)
                position -= menu;

            return position;
        }
    };

})(jQuery, window);

function renderDataTables() {
        $('table.data_tables').DataTable().destroy();
        $('table.data_tables').DataTable({
        "scrollX": true,
        dom: '<"box-header"<"table_header"B><"table_header"f><"table_header"l><"table_header"i>>rt<"table_header"p>p',
        paging: false,
        select: false,
        order: [],
        buttons: [
            {
                extend: 'copy',
                text: 'Copy to clipboard',
                className: 'btn btn-success btn-filters',
                title: null
            },
            {
                extend: 'csv',
                text: 'Export to CSV',
                className: 'btn btn-success btn-filters',
                title: null
            },
            {
                extend: 'excel',
                text: 'Export to Excel',
                className: 'btn btn-success btn-filters',
                title: null
            },
            {
                extend: 'pdf',
                text: 'Export to PDF',
                className: 'btn btn-success btn-filters',
                orientation: 'landscape',
                title: null
            },
            {
                extend: 'print',
                text: 'Print',
                className: 'btn btn-success btn-filters',
                title: null
            }
        ]
   });

}
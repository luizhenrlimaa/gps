
let formFields = [];

class FormField {

    constructor(id, type, value, selectedData) {
        this.setId(id);
        this.setType(type);
        this.setValue(value);
        this.setSelectedData(selectedData);
    }

    getId() {
        return this.id;
    }

    setId(id) {
        this.id = id;
    }

     getName() {
        return this.id.replace('id_', '').replace('_', ' ').charAt(0).toUpperCase();
    }

    getType() {
        return this.type;
    }

    setType(type) {
        this.type = type;
    }

    getValue() {
        return this.value;
    }

    setValue(value) {
        this.value = value;
    }

    getVerboseValue() {
        return this.verboseValue;
    }

    getSelectedData() {
        return this.selectedData;
    }

    setSelectedData(selectedData) {

        if (!selectedData) {
            this.selectedData = Array.from($('#' + this.getId()).find(':selected')
                                                      .map((i, e) => {

                                                      let verboseName = null;

                                                      document.querySelector('#' + this.getId()).parentNode.querySelectorAll('li')
                                                      .forEach( (a) => { if (a.title === e.text) { verboseName = a.textContent.replace('×', ''); } });

                                                      if (!verboseName) {
                                                        verboseName = $('#select2-' + this.getId() + '-container').text();
                                                      }

                                                      return [{id: e.value, name: e.text, verboseName: verboseName}];
                                                      }));
        } else {
            this.selectedData = selectedData;
        }
    }

}

const FieldTypeEnum = {
    AUTO_COMPLETE: 'autocomplete',
    CHECKBOX: 'checkbox',
    DATE_RANGE: 'date-range',
    MODEL_SELECT2: 'modelselect2',
    SELECT: 'select',
    SELECT2: 'select2',
    SELECT2_MULTIPLE: 'modelselect2multiple',
    V_FILTER_SINGLE_DATE: 'single-date',
    V_FILTER_SELECT2: 'select2-multiple-select',
    V_FILTER_SELECT2_SINGLE: 'select2-select',
    V_FILTER_MULTIPLE_SELECT: 'multiple-select',
}

const FieldTypeGroupEnum = {
    
    SELECT: [
        FieldTypeEnum.V_FILTER_SELECT2,
        FieldTypeEnum.V_FILTER_SELECT2_SINGLE,
        FieldTypeEnum.V_FILTER_MULTIPLE_SELECT,
        FieldTypeEnum.AUTO_COMPLETE,
        FieldTypeEnum.SELECT2_MULTIPLE,
     ],
     
     DATE: [
        FieldTypeEnum.DATE_RANGE,
        FieldTypeEnum.V_FILTER_SINGLE_DATE,
     ],
     
}

function updateFormData(formData) {

    if (!formData) {
        return;
    }

    formData.fields.forEach((field) => { field.setSelectedData(null); });
    sessionStorage.setItem(window.location.href, JSON.stringify(formData));
}

function load_form_data() {
    let form_data = JSON.parse(sessionStorage.getItem(window.location.href));

    if (!form_data) {
        return;
    }

    form_data.fields.forEach((field) => { load_field_data(new FormField(field.id, field.type, field.value, field.selectedData)); });
}

function load_field_data(field) {

    if (!field) {
        return;
    }

    if (FieldTypeGroupEnum.SELECT.includes(field.type)) {
        fill_select_field_data(field);
    }
    else if (FieldTypeEnum.MODEL_SELECT2 === field.type) {
        fill_modelselect2_field_data(field);
    }
    else if (FieldTypeEnum.SELECT2 === field.type || FieldTypeEnum.SELECT  === field.type) {
        fill_select2_field_data(field);
    }
    else if (FieldTypeEnum.CHECKBOX === field.type || !field.type) {
        fill_checkbox_field_data(field);
    }
    else if (FieldTypeGroupEnum.DATE.includes(field.type)) {
        fill_date_range_field_date(field);
    }
    else {
        fill_text_field_date(field);
    }
}

function fill_select_field_data(field) {

    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).empty();

        let field_form = $(field_id).siblings();

        field_form.find('ul').empty();

        for (i = 0; i < field.getSelectedData().length; i++) {
            let current_field_id = field.getSelectedData()[i].id;
            let current_field_name = field.getSelectedData()[i].name;
            let current_field_verbose_name = field.getSelectedData()[i].verboseName ? field.getSelectedData()[i].verboseName : field.getSelectedData()[i].name;

            $(field_id).append(
                '<option value=' + current_field_id + '>' +
                    current_field_verbose_name +
                '</option>'
            );

            field_form.find('ul').append(
                '<li class="select2-selection__choice" title=' + current_field_name + '>' +
                    '<span class="select2-selection__choice__remove" role= "presentation" >×</span >' +
                     current_field_name +
                '</li >'
            );
        }
        $(field_id).val(field.getSelectedData().map((data) => data.id)).trigger('change');
    } catch (error) {
        console.group("It wasn't possible to fill autocomplete field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function fill_modelselect2_field_data(field) {
    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).empty();

        let current_field_id = field.getSelectedData()[0].id;
        let current_field_name = field.getSelectedData()[0].name;
        let current_field_verbose_name = field.getSelectedData()[0].verboseName  ? field.getSelectedData()[0].verboseName : field.getSelectedData()[0].name;

        $(field_id).append(
            '<span class="select2-selection__rendered" id="select2-id_service_packages-container" title="' + current_field_name + '">' +
            '<span class="select2-selection__clear">×</span>' + current_field_name + '</span>' +
            '<option value="' + current_field_id + '">' + current_field_verbose_name + '</option>'
        );

        $(field_id).val(current_field_id).trigger('change');
    } catch (error) {
        console.group("It wasn't possible to fill autocomplete field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function fill_select2_field_data(field) {

    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).val(field.getSelectedData().map((data) => data.id)).trigger('change');
    } catch (error) {
        console.group("It wasn't possible to fill date range field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function fill_checkbox_field_data(field) {

    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).prop('checked', field.value);
    } catch (error) {
        console.group("It wasn't possible to fill checkbox field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function fill_date_range_field_date(field) {

    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).val(field.value);
    } catch (error) {
        console.group("It wasn't possible to fill date range field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function fill_text_field_date(field) {

    if (!field) {
        return;
    }

    field_id = '#' + field.id;

    try {
        $(field_id).val(field.value);
    } catch (error) {
        console.group("It wasn't possible to fill date range field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function clean_form_data() {
    let form_data = JSON.parse(sessionStorage.getItem(window.location.href));

    if (!form_data) {
        return;
    }

    form_data.fields.forEach((field) => { clean_field_data(field); });
}

function clean_field_data(field) {

    if (!field) {
        return;
    }

    if (FieldTypeGroupEnum.SELECT.includes(field.type) || FieldTypeEnum.MODEL_SELECT2 === field.type) {
        clean_select_field_data(field.id);
    }
    else if (FieldTypeEnum.SELECT2 === field.type || FieldTypeEnum.SELECT  === field.type) {
        clean_select2_field_data(field.id);
    }
    else if (FieldTypeEnum.CHECKBOX === field.type) {
        clean_checkbox_field_data(field.id);
    }
    else if (FieldTypeEnum.DATERANGE === field.type) {
        clean_date_range_field_data(field.id);
    } else {
        clean_text_field_data(field.id);
    }
}

function clean_select_field_data(field_id) {

    if (!field_id) {
        return;
    }

    field_id = '#' + field_id;

    try {
        $(field_id).empty();
        $(field_id).val('').trigger('change');
    } catch (error) {
        console.group("It wasn't possible to clean select2 field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function clean_select2_field_data(field_id) {

    if (!field_id) {
        return;
    }

    field_id = '#' + field_id;

    try {
        $(field_id).val('').trigger('change');
    } catch (error) {
        console.group("It wasn't possible to clean select2 field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function clean_checkbox_field_data(field_id) {

    if (!field_id) {
        return;
    }

    field_id = '#' + field_id;

    try {
        $(field_id).prop('checked', false);
        $(field_id).parent('div').removeClass('checked');
    } catch (error) {
        console.group("It wasn't possible to clean checkbox field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function clean_date_range_field_data(field_id) {

    if (!field_id) {
        return;
    }

    field_id = '#' + field_id;

    try {
        $(field_id).val('');
    } catch (error) {
        console.group("It wasn't possible to clean date range field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function clean_text_field_data(field_id) {

    if (!field_id) {
        return;
    }

    field_id = '#' + field_id;

    try {
        $(field_id).val('');
    } catch (error) {
        console.group("It wasn't possible to clean date range field data.");
        console.warn(error);
        console.groupEnd();
    }
}

function syncFormData() {

    let formData = sessionStorage.getItem(window.location.href);

    if (formData) {
        load_form_data();
        return;
    } else {
        updateForm();
    }
}

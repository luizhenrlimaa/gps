const forwardMixin = {
    methods: {
        getFilterValue(filterName) {
            return $(`#id_input_${filterName}`).val();
        },
    },
};

const singleDate = {
    mixins: [forwardMixin],
    props: {
        filter: {required: true},
    },
    data() {
        return {
            inputElement: '',
            value: '',
        };
    },
    template: `
        <div class="form-group">
            <label :for="'id_input_' + filter.name" class="col-sm-12">
                {{ filter.verboseName }}
                <span class="text-red" v-show="filter.required">*</span>
            </label>
            <div class="col-sm-12">
                <div class="input-group">
                    <div class="input-group-addon">
                        <i class="fa fa-calendar"></i>
                    </div>
                    <input :id="'id_input_' + filter.name" type="text" style="height: 45px;" autocomplete="off" class="form-control">
                </div>
            </div>
        </div>
    `,

     methods: {

         setValue() {
            this.value = this.inputElement.value;
            this.triggerChange();
         },

         triggerChange() {
            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': this.value,
                    }
                }
            ));
         },
     },

     mounted() {
        this.inputElement = document.querySelector(`#id_input_${this.filter.name}`);
        let vueElement = this;
        $(`#id_input_${this.filter.name}`).daterangepicker({
            singleDatePicker: true,
            showWeekNumbers: true,
            opens: 'center',
            autoUpdateInput: false,
            locale: {
                cancelLabel: 'Clear',
                format: 'YYYY-MM-DD'
            },
        }).on('change', function(ev, picker) {
            vueElement.setValue();
        }).on('apply.daterangepicker', function(ev, picker) {
            if (picker.startDate.format('YYYY-MM-DD') === picker.endDate.format('YYYY-MM-DD')) {
                $(this).val(picker.startDate.format('YYYY-MM-DD'));
            } else {
                $(this).val(picker.startDate.format('YYYY-MM-DD') + ' until ' + picker.endDate.format('YYYY-MM-DD'));
            }
            vueElement.setValue();
        }).on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            vueElement.setValue();
        });
     },
};

const dataRange = {
    mixins: [forwardMixin],
    props: {
        filter: {required: true},
    },
    data() {
        return {
            inputElement: '',
            value: '',
        };
    },
    template: `
        <div class="form-group">
            <label :for="'id_input_' + filter.name" class="col-sm-12">
                {{ filter.verboseName }}
                <span class="text-red" v-show="filter.required">*</span>
            </label>
            <div class="col-sm-12">
                <div class="input-group">
                    <div class="input-group-addon">
                        <i class="fa fa-calendar"></i>
                    </div>
                    <input :id="'id_input_' + filter.name" type="text" autocomplete="off" style="height: 45px;" class="form-control">
                </div>
            </div>
        </div>
    `,

     methods: {

         setValue() {
            this.value = this.inputElement.value;
            this.triggerChange();
         },

         triggerChange() {
            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': this.value,
                    }
                }
            ));
         },
     },

     mounted() {
        this.inputElement = document.querySelector(`#id_input_${this.filter.name}`);
        let vueElement = this;
        $(`#id_input_${this.filter.name}`).daterangepicker({
            opens: 'center',
            autoUpdateInput: false,
            locale: {
                cancelLabel: 'Clear',
                format: 'YYYY-MM-DD'
            },
        }).on('change', function(ev, picker) {
            vueElement.setValue();
        }).on('apply.daterangepicker', function(ev, picker) {
            if (picker.startDate.format('YYYY-MM-DD') === picker.endDate.format('YYYY-MM-DD')) {
                $(this).val(picker.startDate.format('YYYY-MM-DD'));
            } else {
                $(this).val(picker.startDate.format('YYYY-MM-DD') + ' until ' + picker.endDate.format('YYYY-MM-DD'));
            }
            vueElement.setValue();
        }).on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            vueElement.setValue();
        });
     },
};

// TODO-DEV: Develop it
const singleSelect = {
    mixins: [forwardMixin],
    props: {
        field: {required: true},
    },
    data() {
        return {
            inputElement: '',
            options: [],
            selection: [],
        };
    },
    template: `
        <div class="form-group">
            <label :for="field.field_name" class="col-sm-3 control-label">{{ field.description }}
                <span class="text-red" v-show="field.field_required">*</span>
            </label>
            <div class="col-sm-9">
                <select class="form-control" @change="onChange($event)">
                <option value="">Select one...</option>
                <option v-for="opt in field.field_options.split(',')" :value="opt">{{ opt }}</option>
                </select>
            </div>
        </div>
    `,
    methods: {
        onChange(event) {
             this.field.value = event.target.value
        },

        selectItem() {

            let inputValue = this.inputElement.value;

            document.querySelectorAll(`#id_select_${this.filter.name} data`).forEach((opt) => {

                 if (inputValue == opt.textContent.trim()) {
                    this.selection.push({'id': opt.value, 'text': inputValue});
                    this.inputElement.value = '';
                    this.triggerChange();
                 }
            });
        },

        unselectItem(item) {
            this.selection = this.selection.filter((i) => { return i !== item; });
            this.triggerChange();
        },

        triggerChange() {
            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': this.selection,
                    }
                }
            ));
        },
    },
};

const multipleSelect = {
    mixins: [forwardMixin],
    props: {
        filter: {required: true},
    },
    data() {
        return {
            inputElement: '',
            options: [],
            selection: [],
        };
    },
    template: `
        <div class="form-group">
            <label :for="filter.name" class="col-sm-12">
                {{ filter.verboseName }}
                <span class="text-red" v-show="filter.required">*</span>
            </label>
            <div class="col-sm-12">
                <div class="selected-items-container col-sm-12">
                    <div class="selected-items-scroll-box">
                        <div :class="['selected-item', itemClass(item)]" @click="unselectItem(item)" v-for="item in selection"
                            title="Click to remove">
                            {{ item.text }}
                        </div>
                    </div>
                    <input :id="'id_input_' + filter.name" type="text" class="select-input" @keydown="onChange($event)"
                           :list="'id_select_' + filter.name" autocomplete="off" @change="selectItem()">
                    <datalist :id="'id_select_' + filter.name" >
                        <select v-for="opt in options">
                            <option v-if="isNotSelected(opt)">
                                <data :value="opt.id">
                                    {{ opt.text }}
                                </data>
                            </option>
                        </select>
                    </datalist>
                </div>
            </div>
        </div>
    `,

    methods: {

        isNotSelected(item) {

            if (!item) {
                return false;
            }

            return this.selection.length == 0 || this.selection.filter((s) => { return s.id == item.id; }).length == 0;
        },

        itemClass(item) {

            if (!item || !item.text) {
                return;
            }

            let textLength = item.text.length;

            if (textLength < 2) {
                return 'col-sm-1';
            }

            if (textLength > 1 && textLength < 6) {
                return 'col-sm-2';
            }

            if (textLength > 5 && textLength < 13) {
                return 'col-sm-4';
            }

            if (textLength > 12 && textLength < 23) {
                return 'col-sm-6';
            }

            if (textLength > 22 && textLength < 31) {
                return 'col-sm-8';
            }

            if (textLength > 30 && textLength < 39) {
                return 'col-sm-10';
            }

            return 'col-sm-11';
        },

        onChange(event) {
             setTimeout(() => {
                 let queryParam = '?q=' + (this.inputElement.value ? this.inputElement.value : '');
                 this.loadOptions(`${this.filter.autocompleteUrl}${queryParam}`);
             }, 300);
        },

        loadOptions(url) {
            axios.get(url
            ).then((response) => {

                if (!response.data) {
                    return;
                }

                this.options = [];
                this.options.push(...response.data.results);
            }).catch((error) => {
                console.error(`Could not load options of ${this.filter.verboseName} from ${url}`);
            });
        },

        selectItem() {

            let inputValue = this.inputElement.value;

            document.querySelectorAll(`#id_select_${this.filter.name} data`).forEach((opt) => {

                 if (inputValue == opt.textContent.trim()) {
                    this.selection.push({'id': opt.value, 'text': inputValue});
                    this.inputElement.value = '';
                    this.triggerChange();
                 }
            });
        },

        unselectItem(item) {
            this.selection = this.selection.filter((i) => { return i !== item; });
            this.triggerChange();
        },

        triggerChange() {
            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': this.selection,
                    }
                }
            ));
        }
    },

    mounted() {
        this.inputElement = document.querySelector(`#id_input_${this.filter.name}`);
        this.loadOptions(this.filter.autocompleteUrl);
    },
};

const select2MultipleSelect = {
    mixins: [forwardMixin],
    props: {
        filter: {required: true},
    },
    data() {
        return {
            inputElement: '',
            options: [],
            selection: [],
        };
    },
    template: `
        <div class="form-group">
            <label :for="filter.name" class="col-sm-12">
                {{ filter.verboseName }}
                <span class="text-red" v-show="filter.required">*</span>
            </label>
            <div class="col-sm-12">
                <select multiple="multiple" :id="'id_input_' + filter.name" class="select-input"></select>
            </div>
        </div>
    `,

    methods: {

        triggerChange(event) {

            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': $(event.currentTarget).val(),
                    }
                }
            ));
        },
    },

    mounted() {
        this.inputElement = $(`#id_input_${this.filter.name}`);
        let vueElement = this;
        this.inputElement.select2({ cache: true, allowClear: true,  placeholder : ' ', ajax: {
            url: vueElement.filter.autocompleteUrl,
            data: function (params) {

                let query = {};

                if (vueElement.filter.forward) {
                    let forwardMap = new Map();

                    vueElement.filter.forward.forEach((forwardName) => {
                        let forwardValue = vueElement.getFilterValue(forwardName);
                        if (!forwardValue) {
                            return;
                        }
                        forwardMap.set(forwardName, forwardValue);
                    });

                    if (forwardMap.size > 0) {
                        query.forward = {};
                        forwardMap.forEach((forwardValue, forwardName) => query.forward[forwardName] = forwardValue);
                        query.forward = JSON.stringify(query.forward);
                    }
                }

                if (params._type) {
                    query._type = params._type;
                }

                if (params.term) {
                    query.term = params.term;
                    query.q = params.term;
                }

                return query;
            }
        }});
        this.inputElement.on('change', (event) => vueElement.triggerChange(event));
    },
};

const select2Select = {
    mixins: [forwardMixin],
    props: {
        filter: {required: true},
    },
    data() {
        return {
            inputElement: '',
            options: [],
            selection: [],
        };
    },
    template: `
        <div class="form-group">
            <label :for="filter.name" class="col-sm-12">
                {{ filter.verboseName }}
                <span class="text-red" v-show="filter.required">*</span>
            </label>
            <div class="col-sm-12">
                <select single="single" :id="'id_input_' + filter.name" class="select-input"></select>
            </div>
        </div>
    `,

    methods: {

        triggerChange(event) {

            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': this.filter.name,
                        'value': $(event.currentTarget).val(),
                    }
                }
            ));
        },
    },

    mounted() {
        this.inputElement = $(`#id_input_${this.filter.name}`);
        let vueElement = this;
        this.inputElement.select2({ ajax: { url: vueElement.filter.autocompleteUrl }, cache: true, allowClear: true, placeholder : ' ', });
        this.inputElement.on('change', (event) => vueElement.triggerChange(event));
    },
};

Vue.component('v-filter', {
    template: `
        <div>
            <div class="box-body">
                <template v-for="filter in filters">
                    <div class="col-md-12">
                        <component :is="filter.type" :filter="filter"></component>
                    </div>
                </template>
            </div>
        </div>
      `,

    components: {
        'single-select': singleSelect,
        'multiple-select': multipleSelect,
        'select2-multiple-select': select2MultipleSelect,
        'select2-select': select2Select,
        'data-range': dataRange,
        'single-date': singleDate,
    },

    props: {
        filters: {required: true},
    },

    mounted() {
        document.addEventListener('clear-all-filters', () => {
            this.filters.forEach((filter) => {
                let filterElement = document.querySelector(`#id_input_${filter.name}`);

                if (!filterElement) {
                    return;
                }

                filterElement.value = '';
                filterElement.dispatchEvent(new CustomEvent('change'));
            });
        });
    }
});
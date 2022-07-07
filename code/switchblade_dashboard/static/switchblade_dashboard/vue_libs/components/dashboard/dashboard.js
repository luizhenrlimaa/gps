'use strict';

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of spin.                                                                      */
/**********************************************************************************************************************/
const spinMixin = {
    
    methods: {
        
        removeSpin(element) {
            element.parentElement.querySelectorAll('.overlay').forEach((spin) => spin.remove());
        },

        appendSpinTo(element) {

            this.removeSpin(element);

            let spinHtml = `<div class="overlay" title="Syncing data...">
                                <i class="fa fa-refresh fa-spin"></i>
                            </div>`;

            let spinElement = document.createRange().createContextualFragment(spinHtml);
            element.parentElement.appendChild(spinElement);
        },
    }
};

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of sync time.                                                                 */
/**********************************************************************************************************************/
const syncTimeMixin = {

    data() {
        return {
            syncDataIntervalMap: new Map(),
            refreshSyncDataMap: new Map(),
        }
    },

    methods: {

        mapSyncData(elmId, counter, syncing) {
            this.refreshSyncDataMap.set(elmId, {'counter': counter, 'syncing': syncing});
        },

        getSyncData(elmId) {
            let syncData = this.refreshSyncDataMap.get(elmId);

            if (syncData) {
                return syncData;
            }

            syncData = {};
            syncData.counter = 0;
            syncData.syncing = false;

            return syncData;
        },
        
        appendSyncTimeTo(elm, elmId) {
            let elmConfigBtnElement = elm.parentElement.querySelector('.sync-time');

            if (elmConfigBtnElement) {
                elmConfigBtnElement.remove();
            }

            let elmSyncTimeHtml = `<div type="button" class="sync-time" title="Last sync time">
                                       <i class="fa fa-refresh fa-spin"></i>
                                       <span>Syncing data...</span>
                                   </div>`;

            let elmSyncTimeElement = document.createRange().createContextualFragment(elmSyncTimeHtml);
            elm.parentElement.appendChild(elmSyncTimeElement);
            this.initSyncDataElement(elmId, elm);
        },
        
        initSyncDataElement(elmId, elm) {

            this.mapSyncData(elmId, 0, true);

            let interval = setInterval(() => {
                let syncData = this.getSyncData(elmId);
                this.mapSyncData(elmId, ++syncData.counter, syncData.syncing);

                let iconElement = elm.parentElement.querySelector('.sync-time i');
                let spanTextElement = elm.parentElement.querySelector('.sync-time span');

                if (syncData.syncing) {
                    this.showLoadingData(elm, spanTextElement, iconElement);
                } else {
                    this.showTimerData(elmId, spanTextElement, iconElement);
                }
            }, 1000);
        },

        showLoadingData(elm, spanTextElement, iconElement) {
            iconElement.classList.remove('fa-clock-o');
            iconElement.classList.add('fa-refresh');
            iconElement.classList.add('fa-spin');
            spanTextElement.innerText = 'Syncing data...';
        },

        showTimerData(elmId, spanTextElement, iconElement) {
            let syncData = this.getSyncData(elmId);

            if (syncData.counter == 0) {
                return;
            }

            let momentObject = moment().startOf('day').seconds(syncData.counter);
            let mins = momentObject.format('mm');
            let secs = momentObject.format('ss');
            let minsText = mins > 0 ? mins > 1 ? `${mins} minutes` : `${mins} minute` : '';
            let secsText = secs > 0 ? secs > 1 ? `${secs} seconds` : `${secs} second` : '00 second';

            iconElement.classList.remove('fa-refresh');
            iconElement.classList.remove('fa-spin');
            iconElement.classList.add('fa-clock-o');
            spanTextElement.innerText = `Data synced ${minsText} ${secsText} ago`;
        },
    }
};

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of filter.                                                                    */
/**********************************************************************************************************************/
const filterMixin = {

    data() {
        return {
            filters: new Map(),
        }
    },

    computed: {
        pageFiltersTemplate() {
            return dashboardTemplate.filters.filter((f) => !f.showOnPage || f.showOnPage.includes(this.currentPage));
        },
    },

    methods: {

        getFiltersAsQueryParams() {
            let params = {};
            let queryParams = [];

            this.filters.forEach((value, name) => {

                // TODO-DEV: find out a better way to build this kind of exception for 'out_of_demand'/'milestone'
                if (!['milestone', 'out_of_demand'].includes(name) && this.pageFiltersTemplate.filter((f) => f.name == name).length == 0) {
                    return;
                }

                let isObject = value[0] instanceof Object || Array.isArray(value);
                let paramName = isObject ? `${name}_ids` : name;
                let paramValue = isObject ? value.map((v) => { if (v.id) { return v.id } return v; }) : value;
                params[paramName] = paramValue;
            });

            Object.keys(params).forEach((paramName, index) => {
                 let paramValue = params[paramName];

                 if (!paramValue || paramValue.length == 0) {
                    return;
                 }

                 queryParams.push(`${paramName}=${paramValue}`);
            });

            if (!queryParams || queryParams.length == 0) {
                return '';
            }

            return '?' + queryParams.join('&');
        },

        updateFilterState() {
            let fields = [];

            this.pageFiltersTemplate.forEach((filter) => {
                let filterInputId = `id_input_${filter.name}`;
                let filterElement = document.getElementById(filterInputId);

                if (!filterElement) {
                    return;
                }

                this.filters.forEach((value, name) => {
                    if (filter.name == name) {
                        fields.push(new FormField(filterInputId, filter.type, value, []));
                    }
                });
            });

            updateFormData({ fields: fields });
        },

        updateKeepFormData() {
            let fields = this.pageFiltersTemplate.map((filter) => {
                let value = $(`#id_input_${filter.name}`).val();
                return new FormField(`id_input_${filter.name}`, `${filter.type}`, value, []);
            });

            updateFormData({ fields: fields });
        },

        initFiltersStartData() {

            if (!this.charts || !this.pageFiltersTemplate || this.pageFiltersTemplate.length == 0) {
                return;
            }

            let fields = [];

            dashboardTemplate.filters.forEach((filter) => {
                if (!this.filterWasTouched(filter)) {
                    if (filter.startData && (!filter.useStartDataOnPage || filter.useStartDataOnPage.includes(this.currentPage))) {
                        this.setFilterData(filter, filter.startData);
                        fields.push(new FormField(`id_input_${filter.name}`, `${filter.type}`, filter.startData, []));
                    } else {
                        this.setFilterData(filter, '');
                        fields.push(new FormField(`id_input_${filter.name}`, `${filter.type}`, '', []));
                    }
                } else {
                    let value = $(`#id_input_${filter.name}`).val();
                    filter.startData = value;
                    this.setFilterData(filter, value);
                    fields.push(new FormField(`id_input_${filter.name}`, `${filter.type}`, filter.startData, []));
                }
            });

            updateFormData({ fields: fields });
        },

        setFilterData(filter, value) {

            document.dispatchEvent(new CustomEvent('filter-change', {
                'detail':
                    {
                        'name': filter.name,
                        'value': value,
                    }
                }
            ));
        },

        filterWasTouched(filter) {

            let storedData = JSON.parse(sessionStorage.getItem(window.location.href));

            if (!storedData) {
                return;
            }

            let storedFilter = storedData.fields.filter((storedFilter) => storedFilter.id == `id_input_${filter.name}`);

            if (!storedFilter || storedFilter.length == 0) {
                return;
            }

            storedFilter = storedFilter[0];

            return ((storedFilter.value && storedFilter.value.length > 0) && (!filter.startData || (filter.startData && storedFilter.value !== filter.startData)))
                || ((storedFilter.selectedData && storedFilter.selectedData.length > 0) && (!filter.startData || (filter.startData && storedFilter.selectedData !== filter.startData)));
        },
    },

    mounted() {
        document.addEventListener('filter-change', (filter) => this.filters.set(filter.detail.name, filter.detail.value));
    },
};

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of refresh data.                                                              */
/**********************************************************************************************************************/
const refreshDataMixin = {

    data() {
        return {
            refreshDataEnable: true,
            refreshIntervalMap: new Map(),
            refreshDefaultTime: (60000 * 3),
        }
    },

    methods: {

        clearIntervals() {
            this.refreshIntervalMap.forEach((interval, chartId) => clearInterval(interval));
        },

        changeRefreshTime(newRefreshTime) {
            this.refreshDefaultTime = newRefreshTime;
            this.clearIntervals();
            this.forceRefreshCurrentPageData();
            this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams());
        },

        stopStartRefreshData() {
            this.refreshDataEnable = !this.refreshDataEnable;

            if (this.refreshDataEnable) {
                this.initFiltersStartData();
                setTimeout(() => {
                    this.forceRefreshCurrentPageData();
                    this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams());
                }, 500);
            }
        },
    },

    mounted() {
        document.addEventListener('stop-start-refresh-data', () => this.stopStartRefreshData());
        document.addEventListener('change-refresh-time', (event) => this.changeRefreshTime(event.detail.value));
        document.addEventListener('force-page-refresh-data', () => {
            this.updateFilterState();
            this.forceRefreshCurrentPageData();
            this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams());
        });
    },
};

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of pagination.                                                                */
/**********************************************************************************************************************/
const paginationMixin = {

     data() {
        return {
            currentPage: 1,
            viewedPages: [],
            responseDataMap: new Map(),
            pageSearchedParamsMap: new Map(),
        }
    },

    methods: {

        changeCurrentPage(pageNumber) {
            this.hideAllPages();
            this.currentPage = pageNumber;
            this.renderCurrentPage();
        },

        pageChange(value) {
            document.dispatchEvent(new CustomEvent('page-change', {
                    'detail': {
                        'value': value,
                    }
                }
            ));
        },

        nextPage() {
            this.pageChange(++this.currentPage);
        },

        previousPage() {
            this.pageChange(--this.currentPage);
        },

        renderCurrentPage() {

            this.initFiltersStartData();

            setTimeout(() => {
                if (this.viewedPages.includes(this.currentPage)) {
                    this.refreshPage();
                    return;
                }

                this.initPage();
                this.viewedPages.push(this.currentPage);
                setTimeout(() => { this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams()); }, 500);
            }, 500);
        },

        initPage() {
            showElement(`#dashboard-page-${this.currentPage}`);
            setTimeout(() => { this.initiateCurrentPageComponents(); }, 500);
        },

        refreshPage() {
            this.viewedPages.forEach((page) => {
                if (page == this.currentPage) {
                    showElement(`#dashboard-page-${page}`);
                }
            });

            if (!this.isPageUpToDate()) {
                this.refreshCurrentPageData();
                setTimeout(() => { this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams()); }, 2000);
                return;
            }

            this.initiateCurrentPageComponents();
            setTimeout(() => { this.pageSearchedParamsMap.set(this.currentPage, this.getFiltersAsQueryParams()); }, 2000);
        },

        isPageUpToDate() {
            return this.pageSearchedParamsMap.get(this.currentPage) == this.getFiltersAsQueryParams();
        },

        initPagination() {
            this.renderCurrentPage();

            if (!this.charts) {
                return;
            }

            this.hideAllPages();
        },

        hideAllPages() {

            if (!this.charts) {
                return;
            }

            this.charts.forEach((page, pageNumber) => hideElement('#dashboard-page-' + (pageNumber + 1)));
        },
    },

    mounted() {
        this.initPagination();
        document.addEventListener('page-change', (event) => this.changeCurrentPage(event.detail.value));
    }
};

/**********************************************************************************************************************/
/* This Mixin contains a fragment logic of detail data.                                                                */
/**********************************************************************************************************************/
const detailDataMixin = {
    data() {
        return {
            extraInfoMap: new Map(),
            tableStyleMap: new Map(),
        }
    },

    methods: {

        showDetailsFor(elementId, event) {

            let rawExtraInfoData = this.extraInfoMap.get(elementId);

            if (!rawExtraInfoData || !rawExtraInfoData.modal || !rawExtraInfoData.modal.params) {
                return;
            }

            let componentDataKey = '';

            if (typeof this.getComponentDataKey === 'function') {
                componentDataKey = this.getComponentDataKey(event);
            } else {
                let customComponentsDataModel = this.getComponentsFromCurrentPage().find((elm) => elm.id == elementId);

                if (!customComponentsDataModel || !customComponentsDataModel.getComponentDataKeyHandler) {
                    return;
                }

                componentDataKey = customComponentsDataModel.getComponentDataKeyHandler(event);
            }

            if (!rawExtraInfoData.modal.params[componentDataKey]) {
                return;
            }

            this.setUpModalTemplate(rawExtraInfoData.modal.params[componentDataKey], elementId, rawExtraInfoData, componentDataKey);
        },

        getTableTemplate(rawExtraInfoData, key) {
            let templateDataModel = [];
            let rawTableTemplateData = rawExtraInfoData.table_template;

            let line = rawExtraInfoData.modal.params[key][0];
            let width = 100/Object.keys(line).length;

            Object.keys(line).forEach((propertyName, index) => {
                let propertyType = rawTableTemplateData[index];
                let classList = this.tableStyleMap.get(propertyType);

                templateDataModel.push({
                    'width': `${width}%`,
                    'verboseName': cleanString(propertyName),
                    'type': propertyType,
                    'classList': classList,
                });
            });

            return {
                'dataModel': templateDataModel,
            };
        },

        setUpModalTemplate(payLoad, elementId, rawExtraInfoData, componentDataKey) {

            let url = rawExtraInfoData.modal.urlApiTemplate;
            let element = document.querySelector(`#${elementId}`);
            this.appendSpinTo(element);

            if (!url) {
                setTimeout(() => { this.removeSpin(element); }, 1000);

                let tableDataModel = {
                    'data': payLoad,
                    'template': this.getTableTemplate(rawExtraInfoData, componentDataKey),
                };

                updateDetailModalContent(tableDataModel, MODAL_CONTENT_TYPE.CACHE_TABLE);
                showModalElement('#detail-data-modal');

                return;
            }

            let requestData = {
                'payload': payLoad,
            };

            axios.post(url, requestData, getCsrfTokenHeader()
            ).then((response) => {
                updateDetailModalContent(response.data, MODAL_CONTENT_TYPE.HTML_API);
                showModalElement('#detail-data-modal');
            }).catch(errorCallBack)
            .then(() => this.removeSpin(element));
        },
    },

    mounted() {
        this.tableStyleMap.set('text', ['btn', 'btn-block', 'task-name']);
        this.tableStyleMap.set('image', ['btn', 'btn-block', 'table-image']);
        this.tableStyleMap.set('date', ['btn', 'btn-block', 'btn-outline-secondary-no-hover', 'btn-sm']);
        this.tableStyleMap.set('dateTime', ['btn', 'btn-block', 'btn-outline-secondary-no-hover', 'btn-sm']);
        this.tableStyleMap.set('wsLink', ['btn', 'btn-block', 'btn-default', 'workscope-id']);
    },
};

/**********************************************************************************************************************/
/* This Mixin contains all methods that has more than one fragment logic and is shared within charts and              */
/* custom components (but totally equal code).                                                                        */
/**********************************************************************************************************************/
const commonDashboardMixin = {

    mixins: [spinMixin, syncTimeMixin, filterMixin, refreshDataMixin, paginationMixin, detailDataMixin],

    methods: {

        setAllCssStyle(elmId) {
             if (!elmId) {
                return;
            }

            let elm = document.querySelector(`#${elmId}`);

            if (!elm) {
                return;
            }

            elm.style.height = '100%';
            let elmContainer = document.querySelectorAll(`#${elmId}-container, #${elmId}-container .box`);

            if (elmContainer && elmContainer.length > 0) {
                elmContainer.forEach((e) => e.style.padding = '0');
            }
        },
    },
};

/**********************************************************************************************************************/
/* This Mixin contains all charts logic implementation of the all fragments Mixing above.                             */
/**********************************************************************************************************************/
const chartsDashboardMixin = {

    mixins: [commonDashboardMixin],

    props: ['filters-template'],

    data() {
        return {
            tableData: '',
            tableTemplate: '',
            tableResetData: false,
            modalContentFromAPI: true,
            currentDetailDataModalTemplate: '',
        }
    },

    methods: {

        getComponentDataKey(event) {

            if ('pie' === event.seriesType) {
                return event.name;
            }

            return `${event.name}__${event.seriesName}`;
        },

        initiateCurrentPageComponents() {
            let components = this.getComponentsFromCurrentPage();

            if (!components || components.length == 0) {
                return;
            }

            components.forEach((chart) => {

                if (!chart.id || this.responseDataMap.get(chart.id)) {
                    return;
                }

                this.setAllCssStyle(chart.id);
                this.render(chart);
                this.refreshComponentData(chart.id, chart.apiUrl);

                let interval = setInterval(() => {
                    this.refreshComponentData(chart.id, chart.apiUrl);
                }, this.refreshDefaultTime);

                this.refreshIntervalMap.set(chart.id, interval);
            });
        },

        refreshCurrentPageData() {
            this.getComponentsFromCurrentPage().forEach((component) => {

                if (this.responseDataMap.get(component.id)  && this.isPageUpToDate()) {
                    return;
                }

                this.refreshComponentData(component.id, component.apiUrl);

                let interval = setInterval(() => {
                    this.refreshComponentData(component.id, component.apiUrl);
                }, this.refreshDefaultTime);

                clearInterval(this.refreshIntervalMap.get(component.id));
                this.refreshIntervalMap.set(component.id, interval);
            });
        },

        forceRefreshCurrentPageData() {
            this.getComponentsFromCurrentPage().forEach((component) => {

                this.refreshComponentData(component.id, component.apiUrl);

                let interval = setInterval(() => {
                    this.refreshComponentData(component.id, component.apiUrl);
                }, this.refreshDefaultTime);

                clearInterval(this.refreshIntervalMap.get(component.id));
                this.refreshIntervalMap.set(component.id, interval);
            });
        },

        refreshComponentData(chartId, apiUrl) {
            let isComponentInCurrentPage = this.getComponentsFromCurrentPage().find((chart) => chart.id == chartId);

            if ((!this.refreshDataEnable && this.responseDataMap.get(chartId)) || !isComponentInCurrentPage
                || isComponentInCurrentPage.length == 0) {
                return;
            }

            let chart = document.querySelector(`#${chartId}`);
            let syncingData = this.getSyncData(chartId);
            this.mapSyncData(chartId, syncingData.counter, true);

            if (!this.responseDataMap.get(chartId)) {
                this.appendSpinTo(chart);

                if (!this.getSyncData(chartId).counter) {
                    this.appendSyncTimeTo(chart, chartId);
                }
            }

            axios.get(`${apiUrl}${this.getFiltersAsQueryParams()}`
            ).then((response) => {
                this.mapSyncData(chartId, 0, false);

                if (!response || !response.data) {
                    return;
                }

                this.responseDataMap.set(chartId, response);

                let rawData = response.data.results;
                let rawExtraInfoData = response.data.extra_info;
                let chart = this.getChart(chartId);
                let dataHandler = this.dataHandlerMap.get(chartId);
                let parsedData = dataHandler(rawData);

                chart.setOption(this.initialOptionMap.get(chartId), true);
                chart.setOption(parsedData);

                let chartDataModel = this.getChartDataModel(chartId);

                if (chartDataModel && chartDataModel.customOption) {
                    chart.setOption(chartDataModel.customOption);
                }

                try {
                    this.extraInfoMap.set(chartId, rawExtraInfoData);
                    this.handleExtraData(chartId, chart);
                } catch (error) {
                    console.log(chartId, error);
                }
            }).catch((error) => {
                console.log(chartId, error);
                this.mapSyncData(chartId, syncingData.counter, false);
            }).then(() => {
                this.removeSpin(chart);
            });
        },

        getComponentsFromCurrentPage() {
            return this.charts[this.currentPage - 1];
        },
    },

    mounted() {
         document.addEventListener('change-detail-modal-content', (event) => {
            if (MODAL_CONTENT_TYPE.HTML_API === event.detail.type) {
                this.tableData = '';
                this.tableTemplate = '';
                this.modalContentFromAPI = true;
                this.currentDetailDataModalTemplate = event.detail.value;
            } else if (MODAL_CONTENT_TYPE.CACHE_TABLE === event.detail.type) {
                this.currentDetailDataModalTemplate = '';
                this.modalContentFromAPI = false;
                this.tableResetData = true;
                setTimeout(() => {this.tableResetData = false;}, 1);
                this.tableData = event.detail.value.data;
                this.tableTemplate = event.detail.value.template;
            }
         });
    },
};

/**********************************************************************************************************************/
/* This Mixin contains all custom components logic implementation of the all fragments Mixing above.                  */
/**********************************************************************************************************************/
const customDashboardComponentsMixin = {

    mixins: [commonDashboardMixin],

    data: {
        refreshData: true,
        outOfDemand: false,
        filtersTemplate: [],
        refreshDataValue: 3,
        customComponents: [],
        forceVueComponentToRestart: false,
    },

    methods: {

        initiateCurrentPageComponents() {
            let components = this.getComponentsFromCurrentPage();

            if (!components || components.length == 0) {
                return;
            }

            components.forEach((component) => {

                if (!component.id || this.responseDataMap.get(component.id)) {
                    return;
                }

                this.setAllCssStyle(component.id);
                this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);

                let interval = setInterval(() => {
                    this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);
                }, this.refreshDefaultTime);

                this.refreshIntervalMap.set(component.id, interval);
            });
        },

        refreshCurrentPageData() {
            let components = this.getComponentsFromCurrentPage();

            if (!components || components.length == 0) {
                return;
            }

            components.forEach((component) => {

                if (this.responseDataMap.get(component.id) && this.isPageUpToDate()) {
                    return;
                }

                this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);

                let interval = setInterval(() => {
                    this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);
                }, this.refreshDefaultTime);

                clearInterval(this.refreshIntervalMap.get(component.id));
                this.refreshIntervalMap.set(component.id, interval);
            });
        },

        forceRefreshCurrentPageData() {
             let components = this.getComponentsFromCurrentPage();

            if (!components || components.length == 0) {
                return;
            }

            components.forEach((component) => {
                this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);

                let interval = setInterval(() => {
                    this.refreshComponentData(component.id, component.apiUrl, component.dataHandler);
                }, this.refreshDefaultTime);

                clearInterval(this.refreshIntervalMap.get(component.id));
                this.refreshIntervalMap.set(component.id, interval);
            });
        },

        refreshComponentData(id, apiUrl, dataHandler) {

            let components = this.getComponentsFromCurrentPage();
            let isComponentInCurrentPage = components ? components.find((elm) => elm.id == id) : [];

            if (!id || !apiUrl || !dataHandler || (!this.refreshDataEnable && this.responseDataMap.get(id))
                || !isComponentInCurrentPage || isComponentInCurrentPage.length == 0) {
                return;
            }

            let syncingData = this.getSyncData(id);
            this.mapSyncData(id, syncingData.counter, true);

            let isFirstRequest = !this.responseDataMap.get(id);

            if (isFirstRequest) {
                let componentElement = document.querySelector(`#${id}`);
                this.appendSpinTo(componentElement);

                if (!this.getSyncData(id).counter) {
                    this.appendSyncTimeTo(componentElement, id);
                }
            }

            axios.get(`${apiUrl}${this.getFiltersAsQueryParams()}`
            ).then((response) => {

                this.mapSyncData(id, 0, false);

                if (!response || !response.data) {
                    return;
                }

                this.responseDataMap.set(id, response);
                dataHandler(response);

                let rawExtraInfoData = response.data.extra_info;

                if (rawExtraInfoData) {
                    this.extraInfoMap.set(id, rawExtraInfoData);
                }

                if (isFirstRequest) {
                    let component = this.getComponentsFromCurrentPage().forEach((component) => {
                        if (id == component.id) {
                            let addEventListener = component.eventListenerHandler;

                            if (!addEventListener || typeof addEventListener !== 'function') {
                                return;
                            }

                            addEventListener();
                        }
                    });
                }
            }).catch((error) => {
                console.log(id, error);
                this.mapSyncData(id, syncingData.counter, false);
            }).then(() => {
                this.removeSpin(document.querySelector(`#${id}`));
            });
        },

        getComponentsFromCurrentPage() {
            return this.customComponents[this.currentPage - 1];
        },

        changeOutOfDemandFilter() {
            setTimeout(() => { changeOutOfDemandFilter(this.outOfDemand); }, 500);
        },

        updateMilestone(milestone) {
            setTimeout(() => { updateMilestone(milestone); }, 500);
        },

        showFiltersModal() {
            this.forceVueComponentToRestart = true;
            setTimeout(() => {this.forceVueComponentToRestart = false;}, 1);
            setTimeout(() => {load_form_data();}, 300);
            showModalElement('#filters-modal');
        },
    },
};

/**********************************************************************************************************************/
/* This component contains all the tools for build and manipulate eCharts charts.                                     */
/**********************************************************************************************************************/
Vue.component('v-dashboard', {
    props: ['charts', 'filters-template'],
    delimiters: ['[[', ']]'],
    template: `
        <div>
            <div v-if="currentPage > 1" id="previous-page" @click="previousPage()" title="Previous page">
                <button title="Previous page">
                    <i class="fa fa-chevron-left"></i>
                </button>
            </div>
            <div v-if="currentPage < charts.length" id="next-page" @click="nextPage()" title="Next page">
                <button title="Next page">
                    <i class="fa fa-chevron-right"></i>
                </button>
            </div>
            <div class="modal close-on-click-outside" id="detail-data-modal" onclick="closeModal()">
                <div class="modal-dialog modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                        <h4 class="modal-title"><i class="fa fa-bar-chart-o"></i>
                            Details
                        </h4>
                    </div>
                    <div class="modal-body bg-modal-wrapper">
                        <div v-if="modalContentFromAPI" v-html="currentDetailDataModalTemplate"></div>
                        <div v-else-if="!modalContentFromAPI && !tableResetData" class="box box-default">
                            <v-table :comp-template="tableTemplate" :comp-data="tableData"></v-table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-success" title="Click to close this modal" data-dismiss="modal">
                            <i class="fa fa-close"></i> Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `,

    mixins: [chartsDashboardMixin],

    data() {
        return {
            chartsMap: new Map(),
            dataHandlerMap: new Map(),
            initialOptionMap: new Map(),
            chartDataModelMap: new Map(),
            extraDataHandlerMap: new Map(),
        }
    },

    methods: {
        render(dataModel) {

            if (!dataModel) {
                return;
            }

            this.chartDataModelMap.set(dataModel.id, dataModel);

            let dataType = dataModel.type;
            let customRender = dataModel.render;

            if (!customRender) {
                this.defaultRender(dataType, dataModel);
            }

            try {
                if (typeof customRender === 'function') {
                    customRender(this, dataModel);
                }
            } catch (error) {
                console.log(error);
            }
        },

        // TODO-DEV: Provide better and meaningfully names for charts types
        defaultRender(dataType, dataModel) {
            if ('ring' === dataType) {
                this.renderRingChart(dataModel);
            } else if ('multiple-ring' === dataType) {
                this.renderMultipleRingChart(dataModel);
            } else if ('bar' === dataType) {
                this.renderBarChart(dataModel);
            } else if ('stack-bar' === dataType) {
                this.renderStackBarChart(dataModel);
            } else if ('stack-bar-legend-reverse' === dataType) {
                this.renderStackBarChart(dataModel);
            } else if ('stack-bar-horizontal' === dataType) {
                this.renderStackBarHorizontalChart(dataModel);
            } else if ('horizontal-stack-bar' === dataType) {
                this.renderHorizontalStackBarChart(dataModel);
            } else if ('horizontal-bar' === dataType) {
                this.renderHorizontalBarChart(dataModel);
            } else if ('line-and-bar' === dataType) {
                this.renderLineAndBarChart(dataModel);
            } else if ('bar-fourth-stacked' === dataType) {
                this.renderBarChart(dataModel);
            } else if ('multicolor-single-bar' === dataType) {
                this.renderMulticolorSingleBarChart(dataModel);
            }
        },

        renderRingChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': dataModel.title,
                    'top': '3.5%',
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [ 5, 10, 5, 14],
                },
                'tooltip': {
                    'trigger': 'item',
                    'formatter': '{a} <br/>{b}: {c} ({d}%)',
                },
                'legend': {
                    'type': 'scroll',
                    'orient': 'vertical',
                    'left': 15,
                    'top': '65%',
                    'bottom': 15,
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'data': ['No info'],
                },
                'series': [
                    {
                        'name': dataModel.title,
                        'type': 'pie',
                        'radius': ['40%', '55%'],
                        'center': ['50%', '40%'],
                        'avoidLabelOverlap': false,
                        'minAngle': 15,
                        'startAngle': 180,
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'auto',
                            'margin': '25%',
                            'formatter': function (params) {
                                return  params.value;
                            },
                        },
                        'labelLine': {
                            'show': true,
                            'type': 'dashed',
                        },
                        'emphasis': {
                            'label': {
                                'show': true,
                                'fontSize': '20',
                                'color': '#C2C3CD',
                                'fontWeight': 'bold',
                            },
                        },
                        'data': [
                            {'name': 'No info', 'value': 0},
                        ],
                    },
                    {
                        'name': 'Total',
                        'type': 'pie',
                        'radius': [0, '25%'],
                        'center': ['50%', '40%'],
                        'color': ['#071038'],
                        'label': {
                            'fontSize': 26,
                            'position': 'center',
                            'formatter': function (params) {
                                return params.value;
                            },
                        },
                        'labelLine': {
                            'show': false,
                        },
                        'data': [
                            {'value': 0, 'name': 'Total'},
                        ],
                    },
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderMultipleRingChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': dataModel.title,
                    'top': '5%',
                    'left': 'center',
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    }
                },
                'label': {
                    'formatter': '{b}\n{c} ({d}%)',
                    'color': 'white',
                    'fontSize': 10
                },
                'series': [{
                    'type': 'pie',
                    'radius': ['10%', '30%'],
                    'color': ['#ACB0BF'],
                    'data': [{'value': 0, 'name': 'No Info'}],
                }]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                'color': '#C2C3CD',
                'fontSize': 18,
                'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [5, 10, 5, 14],
                },
                'legend': {
                    'type': 'scroll',
                    'orient': 'vertical',
                    'right': 10,
                    'top': '10%',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                },
                'grid': {
                    'left': '2%',
                    'right': '10%',
                    'bottom': '2%',
                    'top': '15%',
                    'containLabel': true,
                },
                'tooltip': {},
                'dataset': {
                'dimensions': ['x',],
                'source': [
                {'x': 'No info', 'No info': 0},
                ]
                },
                'xAxis': {
                    'type': 'category',
                    'axisLabel': {
                        'color': '#C2C3CD',
                        'fontSize': 13,
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'yAxis': {
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        }
                    },
                },
                'series': [
                    {
                        'type': 'bar',
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'top',
                            'formatter' : function (params) {
                                return params.data[params.seriesName];
                            },
                        },
                    },
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderStackBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [5, 10, 5, 14],
                },
                'legend': {
                    'type': 'scroll',
                    'orient': 'vertical',
                    'right': 10,
                    'top': '10%',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                },
                'grid': {
                    'left': '2%',
                    'right': '10%',
                    'bottom': '2%',
                    'top': '15%',
                    'containLabel': true,
                },
                'tooltip': {
                    'trigger': 'item',
                    'showContent': true,
                },
                'dataset': {
                    'source': [],
                },
                'xAxis': {
                    'type': 'category',
                    'axisLabel': {
                        'color': '#C2C3CD',
                        'fontSize': 13,
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'yAxis': {
                    'gridIndex': 0,
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                },
                'series': [
                    {
                        'type': 'bar',
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'top',
                            'formatter' : function (params) {
                                return params.data[params.seriesName];
                            },
                        },
                    },
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderHorizontalBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [ 5, 10, 5, 14],
                },
                'legend': {
                    'type': 'scroll',
                    'data': ['No info'],
                    'bottom': 10,
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                },
                'tooltip': {
                    'trigger': 'axis',
                    'axisPointer': {
                        'type': 'shadow',
                    },
                },
                'grid': {
                    'top': '15%',
                    'left': '5%',
                    'right': '10%',
                    'bottom': '10%',
                    'containLabel': true,
                },
                'xAxis': {
                    'type': 'value',
                    'position': 'top',
                    'axisLine': {
                        'lineStyle': {
                            'color': 'DFDFDF',
                        },
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'yAxis': {
                    'type': 'category',
                    'axisLine': {
                        'lineStyle': {
                            'color': 'DFDFDF',
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                    'data': ['No info'],
                },
                'series': [
                    {
                        'type': 'bar',
                        'stack': 'same',
                        'label': {
                            'show': true,
                            'position': 'right',
                        },
                        'data': [0],
                    },
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderMulticolorSingleBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [ 5, 10, 5, 14],
                },
                'grid': {
                    'top': '15%',
                    'left': '5%',
                    'right': '10%',
                    'bottom': '10%',
                    'containLabel': true,
                },
                'xAxis': {
                    'type': 'value',
                    'position': 'top',
                    'axisLine': {
                        'lineStyle': {
                            'color': 'DFDFDF',
                        },
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'yAxis': {
                    'type': 'category',
                    'axisLine': {
                        'lineStyle': {
                            'color': 'DFDFDF',
                        }
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'series': [
                    {
                        'type': 'bar',
                        'stack': 'bar',
                        'label': {
                            'show': true,
                            'position': 'inside',
                        },
                        'data': [0],
                    },
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderStackBarHorizontalChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [5, 10, 5, 14],
                },
                'legend': {
                    'type': 'scroll',
                    'orient': 'horizontal',
                    'bottom': 10,
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                },
                'grid': {
                    'top': '15%',
                    'left': '5%',
                    'right': '10%',
                    'bottom': '10%',
                    'containLabel': true,
                },
                'tooltip': {
                    'trigger': 'item',
                    'showContent': true,
                },
                'dataset': {
                    'source': [
                    ],
                },
                'yAxis': {
                    'type': 'category',
                    'axisLabel': {
                        'color': '#C2C3CD',
                        'fontSize': 13,
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                },
                'xAxis': {
                    'gridIndex': 0,
                    'splitLine': {
                        'lineStyle': {
                            'type': 'dashed',
                            'color': 'gray',
                        },
                    },
                    'axisLine': {
                        'lineStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                },
                'series': [
                    {
                        'type': 'bar',
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'top',
                            'formatter' : function (params) {
                                return  params.data[params.seriesName];
                            },
                        },
                    },
                ],
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderHorizontalStackBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                "textStyle": {
                    "color": "#C2C3CD",
                    "fontSize": 18,
                    "fontFamily": "Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif"
                },
                "title": {
                    "top": "3.5%",
                    "text": dataModel.title,
                    "textStyle": {
                        "fontSize": 24,
                        "color": "#C2C3CD",
                        "fontFamily": "Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif"
                    },
                    "subtext": "",
                    "left": "left",
                    "padding": [5, 10, 5, 14]
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "shadow"
                    }
                },
                "legend": {
                    "type": "scroll",
                    "data": [
                        "No info"
                    ],
                    "bottom": 10,
                    "textStyle": {
                        "fontSize": 13,
                        "color": "#C2C3CD",
                        "fontFamily": "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif"
                    }
                },
                "grid": {
                    "top": "12%",
                    "left": "2%",
                    "right": "8%",
                    "bottom": "10%",
                    "containLabel": true
                },
                "xAxis": {
                    "axisLine": {
                        "lineStyle": {
                            "color": "DFDFDF"
                        }
                    },
                    "splitLine": {
                        "lineStyle": {
                            "type": "dashed",
                            "color": "gray"
                        }
                    },
                    "type": "value"
                },
                "yAxis": {
                    "axisLine": {
                        "lineStyle": {
                            "color": "DFDFDF"
                        }
                    },
                    "splitLine": {
                        "lineStyle": {
                            "type": "dashed",
                            "color": "gray"
                        }
                    },
                    "type": "category",
                    "data": [
                        "No info"
                    ]
                },
                "series": [
                    {
                        "name": "No info",
                        "type": "bar",
                        "stack": "same",
                        "label": {
                            "show": true,
                            "position": "right"
                        },
                        "data": [
                            0
                        ]
                    }
                ]
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderLineAndBarChart(dataModel) {
            this.renderChart(dataModel.id, dataModel.type, {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': dataModel.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'left',
                    'padding': [ 5, 10, 5, 14],
                },
                'tooltip': {
                    'trigger': 'axis',
                    'axisPointer': {
                        'type': 'cross',
                        'crossStyle': {
                            'color': '#C2C3CD',
                        },
                    },
                },
                'legend': {
                    'type': 'scroll',
                    'right': 15,
                    'top': '2%',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'data': ['No info'],
                },
                'grid': {
                    'left': '2%',
                    'right': '2%',
                    'bottom': '2%',
                    'top': '15%',
                    'containLabel': true,
                },
                'xAxis': [
                    {
                        'type': 'category',
                        'data': ['No info'],
                        'axisLine': {
                            'lineStyle': {
                                'color': 'DFDFDF',
                            },
                        },
                        'axisPointer': {
                            'type': 'shadow',
                        },
                        'splitLine': {
                            'lineStyle': {
                                'type': 'dashed',
                                'color': 'gray',
                            },
                        },
                    }
                ],
                'yAxis': [
                    {
                        'axisLine': {
                            'lineStyle': {
                                'color': 'DFDFDF',
                            }
                        },
                        'splitLine': {
                            'lineStyle': {
                                'type': 'dashed',
                                'color': 'gray',
                            },
                        },
                        'type': 'value',
                    },
                    {
                        'axisLine': {
                            'lineStyle': {
                                'color': 'DFDFDF',
                            }
                        },
                        'splitLine': {
                            'lineStyle': {
                                'type': 'dashed',
                                'color': 'gray',
                            },
                        },
                        'type': 'value',
                    },
                ],
                'series': [
                    {
                        'name': 'No info',
                        'type': 'bar',
                        'yAxisIndex': 1,
                        'data': [],
                    },
                ],
            }, dataModel.customOption, dataModel.extraDataHandler);
        },

        renderChart(chartId, chartType, option, customOption, extraDataHandler) {

            // TODO-DEV: Try to use refs instead of id
            let dom = document.getElementById(chartId);
            let chart = null;

            if (!dom) {
                console.warn(`Could not initiate charts ${chartId}.`);
                return;
            }

            try {
                chart = echarts.init(dom);
            }
            catch (error) {
                console.log(chartId, error);
            }

            chart.setOption(option, true);

            this.initialOptionMap.set(chartId, option);

            if (customOption) {
                chart.setOption(customOption);
            }

            this.chartsMap.set(chartId, chart);
            this.dataHandlerMap.set(chartId, this.getDataHandler(chartType));
            this.extraDataHandlerMap.set(chartId, extraDataHandler ? extraDataHandler : this.getExtraDataHandler(chartType));

            let dashboardVue = this;
            chart.on('click', (event) => {
                dashboardVue.showDetailsFor(chartId, event);
            });
        },

        getChartDataModel(chartId) {
            return this.chartDataModelMap.get(chartId);
        },

        handleExtraData(chartId, chart) {
            let rawExtraInfoData = this.extraInfoMap.get(chartId);
            let extraDataHandler = this.extraDataHandlerMap.get(chartId);

            if (!rawExtraInfoData || !extraDataHandler || typeof extraDataHandler !== "function") {
                return;
            }

            let parsedExtraInfoData = extraDataHandler(rawExtraInfoData);

            if (!parsedExtraInfoData) {
                return;
            }

            try {
                chart.setOption(parsedExtraInfoData);
            } catch (error) {
                console.log(chartId, error);
            }
        },

        getChart(chartId) {
            return this.chartsMap.get(chartId);
        },

        getDataHandler(dataType) {

            if (!dataType) {
                return;
            }

            if ('ring' === dataType) {
                return this.dataHandlerRingChart;
            } else if ('multiple-ring' === dataType) {
                return this.dataHandlerMultipleRingChart;
            } else if ('bar' === dataType) {
                return this.dataHandlerBarChart;
            } else if ('stack-bar' === dataType) {
                return this.dataHandlerStackBarChart;
            } else if ('stack-bar-legend-reverse' === dataType) {
                return this.dataHandlerStackBarLegendReverseChart;
            } else if ('stack-bar-horizontal' === dataType) {
                return this.dataHandlerStackBarHorizontalChart;
            } else if ('horizontal-stack-bar' === dataType) {
                return this.dataHandlerHorizontalStackBarChart;
            } else if ('horizontal-bar' === dataType) {
                return this.dataHandlerHorizontalBarChart;
            } else if ('line-and-bar' === dataType) {
                return this.dataHandlerLineAndBarChart;
            } else if ('bar-fourth-stacked' === dataType) {
                return this.dataHandlerBarChartFourthStacked;
            } else if ('multicolor-single-bar' === dataType) {
                return this.dataHandlerMulticolorSingleBar;
            }
        },

        getExtraDataHandler(dataType) {

            if (!dataType) {
            return;
            }

            if ('ring' === dataType) {
                return this.extraDataHandlerRingChart;
            } else if ('bar' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('bar-simple' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('stack-bar' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('stack-bar-legend-reverse' === dataType) {
                return this.extraDataHandlerBarLegendReverseChart;
            } else if ('stack-bar-horizontal' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('horizontal-stack-bar' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('horizontal-bar' === dataType) {
                return this.extraDataHandlerBarChart;``
            } else if ('line-and-bar' === dataType) {
                return this.dataHandlerLineAndBarChart;
            } else if ('bar-fourth-stacked' === dataType) {
                return this.extraDataHandlerBarChart;
            } else if ('multicolor-single-bar' === dataType) {
                return this.extraDataHandlerBarChart;
            }
        },

        dataHandlerRingChart(data) {

            if (!data || data.length == 0) {
                return {
                    'legend': {
                        'data': ['No info'],
                    },
                    'series': [
                        {
                        'data': [{'name': 'No info', 'value': 0}],
                        },
                    ]
                };
            }

            let legendData = [];

            let firstObjectKey = Object.keys(data[0])[0];
            let secondObjectKey = '';

            if (!data['value']) {
                secondObjectKey = Object.keys(data[0])[1];
            }

            data.forEach((d) => {
                legendData.push(removeAllBreakLines(d[firstObjectKey]));
            });

            let seriesData = data.map((d) => {
                let name = d['name'] ? d['name'] : d[firstObjectKey];
                let value = d['value'] ? d['value'] : d[secondObjectKey];

                return {'name': removeAllBreakLines(name), 'value': value};
            });

            return {
                'legend': {
                    'data': legendData
                },
                'series': [
                    {
                        'data': seriesData
                    }
                ]
                };
        },

        extraDataHandlerRingChart(data) {

            if (!data || !data.total) {
                return {
                    'series': [
                        {},
                        {
                            'data': [
                                {'value': 0, 'name': 'Total'},
                            ],
                        },
                    ],
                };
            }

            let opt = {};

            if (data.title) {
                opt.title =  { 'text': data.title };
            }

            opt.series = [
                {},
                {
                    'data': [
                        {
                            'value': data.total,
                            'name': 'Total'
                        },
                    ],
                },
            ];

            return opt;
        },

        dataHandlerMultipleRingChart(data) {

            if (!data || data.length == 0) {
                return {
                    'legend': {
                        'data': ['No info'],
                    },
                    'series': [{
                        'type': 'pie',
                        'radius': ['10%', '30%'],
                        'color': ['#ACB0BF'],
                        'data': [{'value': 0, 'name': 'No Info'}],
                    }]
                };
            }

            let legendData = [];

            let firstObjectKey = Object.keys(data[0])[0];

            data.forEach((d) => {
                d['type'] = 'pie';
                legendData.push(removeAllBreakLines(d[firstObjectKey]));
            });

            return {
                'legend': {
                    'data': legendData
                },
                'series': data
            };
        },

        dataHandlerBarChart(data) {

            if (!data || data.length == 0) {
                return {
                    'dataset': {
                        'dimensions': ['x', 'No info'],
                        'source': [
                            {'x': 'No info', 'No info': 0},
                        ],
                    },
                    'series': [
                        {
                            'type': 'bar',
                            'label' : {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter' : function (params) {
                                    return  params.data[params.seriesName];
                                },
                            },
                        },
                    ],
                };
            }

            let dimensionsData = Object.keys(data[0]).map((key, index) => { if (index == 0) { return 'x'; } return key; });

            let sourceData = data.map((d) => {

                let parsedObj = {};

                Object.entries(d).forEach((entry, index) => {

                    if (index == 0) {
                        parsedObj['x'] = entry[1];
                        return;
                    }

                    if (entry[1] == 0) {
                        return;
                    }

                    parsedObj[entry[0]] = entry[1];
                });

                return  parsedObj;
            });

            let seriesData = [];

            for (let i = 1; i < dimensionsData.length; i++) {
                seriesData.push({
                    'type': 'bar',
                    'label' : {
                        'show': true,
                        'fontSize': 18,
                        'position': 'top',
                        'formatter' : function (params) {
                            return  params.data[params.seriesName];
                        },
                    },
                });
            }

            return {
                'dataset': {
                    'dimensions': dimensionsData,
                    'source': sourceData,
                },
                'series': seriesData,
            };
        },

        extraDataHandlerBarChart(data) {

            if (!data || !data.title) {
                return;
            }

            return {
                'title': {
                    'text': data.title,
                },
            };
        },

        extraDataHandlerBarLegendReverseChart(data) {

            if (!data || (!data.title && !data.max_axis_x && !data.max_axis_y)) {
                return;
            }

            let extraOpt = {};

            if (data.title) {
                extraOpt.title = {
                    'text': data.title,
                }
            }

            if (data.max_axis_x) {
                extraOpt.xAxis = {
                    'max': function (value) {
                        return value.max + data.max_axis_x;
                    }
                }
            }

            if (data.max_axis_y) {
                extraOpt.yAxis = {
                    'max': function (value) {
                        return value.max + data.max_axis_y;
                    }
                }
            }

            return extraOpt;
        },

        genFormatter(order, labelData) {
            return (param) => {
                let name = param.name;
                return labelData[order][name];
            }
        },

        dataHandlerStackBarChart(data) {

            if (!data || data.length === 0) {
                return {
                    'dataset': {
                        'dimensions': ['x', 'No info'],
                        'source': [
                            {'x': 'No info', 'No info': 0},
                        ],
                    },
                    'series': [
                        {
                            'type': 'bar',
                            'label': {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter': function (params) {
                                    return params.data[params.seriesName];
                                },
                            },
                        },
                    ],
                };
            }

            let dimensionsData = ['x'];
            dimensionsData.push(...Object.keys(data[0]['value']).map((key) => { return key; }));

            let sourceData = [dimensionsData];
            sourceData.push(...data.map((d) => {
                return [d.compound_name, ...Object.entries(d.value).map((v) => v[1])];
            }));

            let seriesData = [];

            var labelData = {};

            data.forEach((d, index) => {
                for (const [key, value] of Object.entries(d.value)) {
                    if (!(d.order in labelData)) {
                        labelData[d.order] = {};
                    }
                    if(labelData[d.order][key] !== undefined) {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] += value;
                        }
                    } else {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] = value;
                        }
                    }
                }
            });

            var labelIndex = [];

            //TODO-DEV: Check for more than 3 stacked values
            data.map((d) => { return d.order}).filter((e, i, a) => {if (a.indexOf(e) !== i) { labelIndex.push(i-1); return true}});

            data.forEach((d, index) => {
                seriesData.push({
                    'type': 'bar',
                    'stack': d.stack,
                    'seriesLayoutBy': 'row',
                    'barMinHeight': d.top_sum ? 0:20,
                    'clip': false,
                    'label': {
                        'show': true,
                        'fontSize': 12,
                        'color': d.label_color == '#050D2F' ? (d.top_sum ? '#C2C3CD':'#050D2F'):d.label_color,
                        'position': d.top_sum ? 'top':'inside',
                        'formatter': d.top_sum ? this.genFormatter(d.order, labelData) : function (params) {
                            return  params.data[params.seriesName];
                        },
                    },
                });
            });

            return {
            'color': data.filter(d => !d.top_sum).map((d) => d.color),
            'dataset': {
                'source': sourceData,
            },
            'series': seriesData,
            };
        },

        dataHandlerStackBarLegendReverseChart(data) {

            if (!data || data.length === 0) {
                return {
                    'legend': {
                        'data': [],
                    },
                    'dataset': {
                        'dimensions': ['x', 'No info'],
                        'source': [
                            {'x': 'No info', 'No info': 0},
                        ],
                    },
                    'series': [
                        {
                            'type': 'bar',
                            'label': {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter': function (params) {
                                    return params.data[params.seriesName];
                                },
                            },
                        },
                    ],
                };
            }

            let dimensionsData = ['x'];
            dimensionsData.push(...Object.keys(data[0]['value']).map((key) => { return key; }));

            let sourceData = [dimensionsData];
            sourceData.push(...data.map((d) => {
                return [d.compound_name, ...Object.entries(d.value).map((v) => v[1])];
            }));

            let seriesData = [];
            let seriesLegend = [];

            var labelData = {};

            data.forEach((d, index) => {
                for (const [key, value] of Object.entries(d.value)) {
                    if (!(d.order in labelData)) {
                        labelData[d.order] = {};
                    }
                    if(labelData[d.order][key] !== undefined) {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] += value;
                        }
                    } else {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] = value;
                        }
                    }
                }
            });

            var labelIndex = [];

            //TODO-DEV: Check for more than 3 stacked values
            data.map((d) => { return d.order}).filter((e, i, a) => {if (a.indexOf(e) !== i) { labelIndex.push(i-1); return true}});

            data.forEach((d, index) => {
                seriesLegend.push(d.compound_name);
                seriesData.push({
                    'type': 'bar',
                    'stack': d.stack,
                    'seriesLayoutBy': 'row',
                    'barMinHeight': d.top_sum ? 0:20,
                    'clip': false,
                    'label': {
                        'show': true,
                        'fontSize': 12,
                        'color': d.top_sum ? '#C2C3CD':'#050D2F',
                        'position': d.top_sum ? 'top':'inside',
                        'formatter': d.top_sum ? this.genFormatter(d.order, labelData) : function (params) {
                            return  params.data[params.seriesName];
                        },
                    },
                });
            });

            return {
            'color': data.filter(d => !d.top_sum).map((d) => d.color),
            'legend': {
                'data': seriesLegend.reverse(),
            },
            'dataset': {
                'source': sourceData,
            },
            'series': seriesData,
            };
        },

        dataHandlerStackBarHorizontalChart(data) {

            if (!data || data.length === 0) {
                return {
                    'dataset': {
                        'dimensions': ['y', 'No info'],
                        'source': [
                            {'y': 'No info', 'No info': 0},
                        ],
                    },
                    'series': [
                        {
                            'type': 'bar',
                            'label': {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter': function (params) {
                                    return params.data[params.seriesName];
                                },
                            },
                        },
                    ],
                };
            }

            let dimensionsData = ['y'];
            dimensionsData.push(...Object.keys(data[0]['value']).map((key) => { return key; }));

            let sourceData = [dimensionsData];
            sourceData.push(...data.map((d) => {
                return [d.compound_name, ...Object.entries(d.value).map((v) => v[1])];
            }));

            let seriesData = [];
            let labelData = {};

            data.forEach((d, index) => {
                for (const [key, value] of Object.entries(d.value)) {
                    if (!(d.order in labelData)) {
                        labelData[d.order] = {};
                    }
                    if(labelData[d.order][key] !== undefined) {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] += value;
                        }
                    } else {
                        if (Number.isInteger(value)) {
                            labelData[d.order][key] = value;
                        }
                    }
                }
            });

            var labelIndex = [];

            //TODO-DEV: Check for more than 3 stacked values
            data.map((d) => { return d.order}).filter((e, i, a) => {if (a.indexOf(e) !== i) { labelIndex.push(i-1); return true}})

            data.forEach((d, index) => {
                seriesData.push({
                    'type': 'bar',
                    'stack': d.stack,
                    'seriesLayoutBy': 'row',
                    'barMinHeight': d.top_sum ? 0: 20,
                    'clip': false,
                    'label': {
                        'distance': 1,
                        'show': true,
                        'fontSize': d.top_sum ? 14:11,
                        'fontWeight': d.top_sum ? 'normal':'bold',
                        'color': d.top_sum ? '#C2C3CD':'#050D2F',
                        'padding': [1.4, 0, 0, 0],
                        'position': d.top_sum ? 'right':'inside',
                        'formatter': d.top_sum ? this.genFormatter(d.order, labelData) : function (params) {
                            return  params.data[params.seriesName];
                        },
                    },
                });
            });

            return {
                'color': data.filter(d => !d.top_sum).map((d) => d.color),
                'dataset': {
                    'source': sourceData,
                },
                'series': seriesData,
            };
        },

        dataHandlerBarChartFourthStacked(data) {

            if (!data || data.length === 0) {
                return {
                    'dataset': {
                        'dimensions': ['x', 'No info'],
                        'source': [
                            {'x': 'No info', 'No info': 0},
                        ],
                        },
                        'series': [
                            {
                            'type': 'bar',
                            'label' : {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter' : function (params) {
                                    return  params.data[params.seriesName];
                                },
                            },
                        },
                    ],
                };
            }

            let dimensionsData = Object.keys(data[0]).map((key, index) => { if (index == 0) { return 'x'; } return key; });

            let sourceData = data.map((d) => {

                let parsedObj = {};

                Object.entries(d).forEach((entry, index) => {

                    if (index == 0) {
                        parsedObj['x'] = entry[1];
                        return;
                    }

                    if (entry[1] == 0) {
                        return;
                    }

                    parsedObj[entry[0]] = entry[1];
                });

                return  parsedObj;
            });

            let seriesData = [];

            for (let i = 1; i < dimensionsData.length; i++) {
                if (i < 4) {
                    seriesData.push({
                        'type': 'bar',
                        'label': {
                            'show': true,
                            'fontSize': 18,
                            'position': 'top',
                            'formatter' : function (params) {
                                return  params.data[params.seriesName];
                            },
                        },
                    });
                } else {
                    seriesData.push({
                        'type': 'bar',
                        'stack': 'same',
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'inside',
                            'formatter' : function (params) {
                                return  params.data[params.seriesName];
                            },
                        },
                    });
                }
            }

            return {
                'dataset': {
                    'dimensions': dimensionsData,
                    'source': sourceData,
                },
                'series': seriesData,
            };
        },

        dataHandlerHorizontalStackBarChart(data) {

            if (!data || data.length == 0) {
                return {
                    'legend': {
                        'data': ['No info'],
                    },
                    'yAxis': {
                        'data': ['No info'],
                    },
                    'series': [
                        {
                            'name': 'No info',
                            'type': 'bar',
                            'stack': 'same',
                            'label': {
                                'show': true,
                                'position': 'right',
                            },
                            'data': [0],
                        },
                    ],
                };
            }

            let legendData = []

            Object.keys(data[0]).forEach((key, index) => {
                if (index != 0) {
                    legendData.push(key);
                }
            });

            let firstObjectKey = Object.keys(data[0])[0];

            let yAxisData = data.map((d) => d[firstObjectKey]);

            let seriesData = legendData.map((legend, index) => {
                return {
                    'name': legend,
                    'type': 'bar',
                    'stack': 'same',
                    'label': {
                        'show': true,
                        'position': 'inside',
                    },
                    'data': data.map((d) => { return d[legend]; })
                };
            });

            return {
                'legend': {
                    'data': legendData,
                },
                'yAxis': {
                    'data': yAxisData,
                },
                'series': seriesData,
            };
        },

        dataHandlerMulticolorSingleBar(data) {

            if (!data || data.length == 0) {
                return {
                    'series': [
                        {
                            'name': 'No info',
                            'type': 'bar',
                            'stack': 'bar',
                            'label': {
                                'show': true,
                                'position': 'inside',
                            },
                            'data': [0],
                        },
                    ],
                };
            }

            let seriesData = []

            data.forEach((data) => {
                seriesData.push({
                    'name': data.name,
                    'color': data.color,
                    'type': 'bar',
                    'stack': 'bar',
                    'barMinHeight': 5,
                    'label': {
                        'show': true,
                        'position': 'right',
                    },
                    'data': data.data
                });
            });

            return {
                'yAxis': {
                    'data': data.map((d) => d.name),
                },
                'series': seriesData,
            };
        },

        dataHandlerHorizontalBarChart(data) {

            if (!data || data.length == 0) {
                return {
                    'legend': {
                        'data': ['No info'],
                    },
                    'yAxis': {
                        'data': ['No info'],
                    },
                    'series': [
                        {
                            'name': 'No info',
                            'type': 'bar',
                            'stack': 'same',
                            'label': {
                                'show': true,
                                'position': 'right',
                            },
                            'data': [0],
                        },
                    ],
                };
            }

            let legendData = []

            Object.keys(data[0]).forEach((key, index) => {
                if (index != 0) {
                    legendData.push(key);
                }
            });

            let firstObjectKey = Object.keys(data[0])[0];

            let yAxisData = data.map((d) => d[firstObjectKey]);

            let seriesData = legendData.map((legend, index) => {
                return {
                    'name': legend,
                    'type': 'bar',
                    'label': {
                        'show': true,
                        'position': 'right',
                    },
                    'data': data.map((d) => { return d[legend]; })
                };
            });

            return {
                'legend': {
                    'data': legendData,
                },
                'yAxis': {
                    'data': yAxisData,
                },
                'series': seriesData,
            };
        },

        dataHandlerLineAndBarChart(data) {

            if (!data || data.length == 0) {
                return {
                    'legend': {
                        'data': ['No info'],
                    },
                    'xAxis': [
                        {
                        'data': ['No info'],
                        }
                    ],
                    'series': [
                        {
                            'name': 'No info',
                            'type': 'bar',
                            'label' : {
                                'show': true,
                                'fontSize': 18,
                                'position': 'top',
                                'formatter' : function (params) {
                                    return  params.data[params.seriesName];
                                },
                            },
                            'yAxisIndex': 1,
                            'data': [],
                        },
                    ],
                };
            }

            let firstObjectKey = '';

            if (!data['name']) {
                firstObjectKey = Object.keys(data[0])[0];
            }

            let legendData = Object.keys(data[0]).map((key, index) => { if (index != 0) { return key; } });

            let xAxisData = data.map((d) => d['name'] ? d['name'] : d[firstObjectKey]);

            let seriesData = legendData.map((legend, index) => {
                return {
                    'name': legend,
                    'type': index == 1 ? 'bar' : 'line',
                    'label' : {
                        'show': true,
                        'fontSize': 18,
                        'position': 'top',
                        'formatter' : function (params) {
                            return  params.data[params.seriesName];
                        },
                    },
                    'yAxisIndex': 1,
                    'data': data.map((d) => { return d[legend]; }),
                };
            });

            return {
                'legend': {
                    'data': legendData,
                },
                'xAxis': [
                    {
                    'data': xAxisData,
                    }
                ],
                'series': seriesData,
            };
        },
    },

    mounted() {
        let timeout;

        document.addEventListener('mousemove', () => {
            let navigationElements = document.querySelectorAll('#previous-page, #next-page');
            clearTimeout(timeout);
            navigationElements.forEach((elm) => elm.classList.add('visible'));
            timeout = setTimeout(() => { navigationElements.forEach((elm) => elm.classList.remove('visible')) }, 500);
        });

        sessionStorage.removeItem(window.location.href);
        window.addEventListener('resize', () => this.chartsMap.forEach((chart, chartId) => chart.resize()));
     },
});
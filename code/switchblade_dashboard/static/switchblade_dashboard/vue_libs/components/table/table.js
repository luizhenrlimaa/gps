let vTable = Vue.component('v-table', {
    props: ['comp-template', 'comp-data', 'api-url', 'api-query-params', 'default-api-method', 'custom-page-size', 'custom-params', 'custom-style'],
    delimiters: ['[[', ']]'],

    template: `
        <table :id="id" class="table table-bordered table-hover dataTables_scrollBody" v-bind:style="customStyle && customStyle.table ? customStyle.table : {}">
            <thead>
                <tr>
                    <th v-if="compTemplate.actions" v-html="'Actions'"
                        :width="compTemplate.actions.length * 40 > 80 ? (compTemplate.actions.length * 33) + 'px' : '80px'">
                    </th>
                    <th v-for="tt in compTemplate.dataModel" :width="tt.width" v-html="tt.verboseName"
                        v-if="tt && !tt.readyOnly"></th>
                </tr>
            </thead>
            <tbody v-bind:style="customStyle && customStyle.tbody ? customStyle.tbody : {}">
                <tr v-for="data in lazyData" v-bind:style="customStyle && customStyle.tr ? customStyle.tr : {}">
                    <td v-if="compTemplate.actions"
                        :width="compTemplate.actions.length * 33 > 80 ? (compTemplate.actions.length * 33) + 'px' : '80px'">
                        <div class="btn-group-xs text-center text-nowrap">
                            <button v-for="action in compTemplate.actions"
                                    :title="action.verboseName" @click="action.handler(data)" :class="action.classList">
                                    <i v-if="action.icon" :class='action.icon'></i>
                            </button>
                        </div>
                    </td>
                    <td v-for="(value, name, index) in data" :width="compTemplate.dataModel[index].width"
                        v-html="handle(value, index, data)"
                        v-if="compTemplate.dataModel[index] && !compTemplate.dataModel[index].readyOnly"
                        v-bind:style="value && value.cellStyle ? value.cellStyle : {}"
                        :class="value && value.cellClass ? value.cellClass : []">
                    </td>
                </tr>
                <tr v-if="loadingData" v-bind:style="customStyle && customStyle.tr ? customStyle.tr : {}">
                    <td class="table-loading">
                        <i class="fa fa-refresh fa-spin"></i>
                    </td>
                </tr>
            </tbody>
        </table>
    `,

    data() {
        return {
            id: (this.customParams && this.customParams.table && this.customParams.table.id)? this.customParams.table.id : 'v-table',
            loadingData: false,
            coolDown: 1000,
            coolingDownTimer: 0,
            tableBodyElement: '',
            lazyData: [],
            data: [],
            allDataLoaded: false,
            page: 0,
            pageSize: this.customPageSize || 25,
            infiniteScroll: true,
        };
    },

    computed: {
        coolingDown() {
            return (Date.now - this.coolingDownTimer) < this.coolDown;
        }
    },

    methods: {
        handle(data, index, obj) {

            let dataModel = this.compTemplate.dataModel[index];

            if (!dataModel) {
                return;
            }

            dataType = dataModel.type;
            handler = dataModel.handler;

            if (!handler || 'default' === handler) {
                return this.defaultHandler(data, dataType, dataModel);
            }

            try {
                return handler(data, dataModel, obj);
            } catch (error) {
                console.log(error);
            }
        },

        defaultHandler(data, dataType, dataModel) {
            if ('text' === dataType) {
                return this.handleText(data, dataModel);
            } else if ('image' === dataType) {
                return this.handleImage(data, dataModel);
            } else if ('date' === dataType) {
                return this.handleDate(data, dataModel);
            } else if ('dateTime' === dataType) {
                return this.handleDateTime(data, dataModel);
            } else if ('dateTime' === dataType) {
                return this.handleDateTime(data, dataModel);
            } else if ('wsLink' === dataType) {
                return this.handleWsLink(data, dataModel, '');
            } else if ('wsStatus' === dataType) {
                return this.handleWsStatus(data, dataModel);
            } else if ('imageProfile' === dataType) {
                return this.handleImageProfile(data, dataModel);
            } else if ('templateObject' === dataType) {
                return this.handleTemplateObject(data);
            }
        },

        handleWsLink(data, dataModel, sites) {

            let siteName = '';

            if (!sites) {
                siteName = '#CIDC' + data;
            }

            sites = sites.split(' ');

            if (sites.length > 1) {
                siteName = 'Multiple sites';
            } else if (sites[0]) {
                siteName = sites[0];
            }

            return `
                <button class="btn btn-block btn-default workscope-id" title="${siteName}"
                        onclick="window.open('/workscopes/detail/${data}', '_blank');">
                    <a>${siteName}</a>
                </button>
            `;
        },

        handleWsStatus(data, dataModel) {

            if (data.detail && data.detail.assignee) {
                return `<a class="btn btn-block btn-social workscope-status ${data.status_class}">
                            <img src="${data.detail.assignee.avatar}"
                                 title="${data.detail.assignee.name}">
                                <i class="fa ${data.detail.status_icon}"></i>
                                &nbsp${data.detail.status_title}
                        </a>`;
            }

            return `<a class="btn btn-block workscope-status ${data.status_class}">
                        ${data.detail.task_name}
                    </a>`;
        },

        handleImageProfile(data, dataModel) {

            if (!data.avatar) {
                return '';
            }

            if (!data.avatar.includes('/files/') && !data.avatar.includes('/static/')) {
                data.avatar = `/files/${data.avatar}`;
            }

            return `
                <span class="assignee ${dataModel.classList ? dataModel.classList.join(' ') : ''}">
                    <img src="${data.avatar}" title="${data.name}">
                </span>
            `;
        },

        handleText(text, dataModel) {

            if (dataModel.preHandler) {
                try {
                    text = dataModel.preHandler(text);
                } catch (error) {
                    console.log(error);
                }
            }

            if (!text) {
                return '';
            }

            text = `${text}`.trim();

            if (!('classList' in dataModel)) {
                dataModel['classList'] = [];
            }

            return `
                <span class="${dataModel.classList.join(' ')}" title="${text}">
                    ${text}
                </span>
            `;
        },

        handleImage(imageHref, dataModel) {

            if (dataModel.preHandler) {
                try {
                    imageHref = dataModel.preHandler(imageHref);
                } catch (error) {
                    console.log(error);
                }
            }

            if (!imageHref) {
                return '';
            }

            if (!imageHref.includes('/files/') && !imageHref.includes('/static/')) {
                imageHref = `/files/${imageHref}`;
            }

            return `
                <span class="${dataModel.classList.join(' ')}">
                    <img src="${imageHref}" width="50px">
                </span>
            `;
        },

        handleDate(date, dataModel) {

            if (dataModel.preHandler) {
                try {
                    date = dataModel.preHandler(date);
                } catch (error) {
                    console.log(error);
                }
            }

            if (!date) {
                return '';
            }

            let dateString = moment(date).format("YYYY-MM-DD");

            if (!('classList' in dataModel)) {
                dataModel['classList'] = [];
            }

            return `
                <span class="${dataModel.classList.join(' ')}">
                    ${dateString}
                </span>
            `;
        },

        handleDateTime(dateTime, dataModel) {

            if (dataModel.preHandler) {
                try {
                    dataModel = dataModel.preHandler(dataModel);
                } catch (error) {
                    console.log(error);
                }
            }

            if (!dateTime) {
                return '';
            }

            let dateTimeString = moment(dateTime).format("YYYY-MM-DD HH:MM");

            if (!('classList' in dataModel)) {
                dataModel['classList'] = [];
            }

            return `
                <span class="${dataModel.classList.join(' ')}">
                    ${dateTimeString}
                </span>
            `;
        },

        handleTemplateObject(data) {

            if (!data.content) {
                return '';
            }

            return data.content;
        },

        initCollDown() {
            this.coolingDownTimer = Date.now();
        },

        scrollAtBottom() {

            if (!this.tableBodyElement) {
                this.tableBodyElement = document.querySelector(`#${this.id} tbody`);

                if (!this.tableBodyElement) {

                    return;
                }
            }

            let currentPosition = this.tableBodyElement.scrollHeight - this.tableBodyElement.scrollTop;

            if (this.apiUrl) {
                let customOffsetHeight = this.tableBodyElement.offsetHeight + 300;
                let range = Array.from(Array(customOffsetHeight).keys()).slice((customOffsetHeight - 300), customOffsetHeight);

                return range.includes(currentPosition);
            }

            return currentPosition == this.tableBodyElement.offsetHeight;
        },

        lazyLoadData() {

            if (!this.data && !this.apiUrl) {
                return;
            }

            if (this.coolingDown || this.loadingData) {
                return;
            }

            if (!this.scrollAtBottom() && this.lazyData && this.lazyData.length > 0) {
                return;
            }

            this.initCollDown();

            if (this.apiUrl) {

                if (this.allDataLoaded) {
                    return;
                }

                this.loadingData = true;
                setTimeout(() => {

                    if(this.defaultApiMethod) {
                        axios.get(this.apiUrl + this.getQueryString()
                        ).then((response) => {

                            if (!response || !response.data) {
                                return;
                            }

                            if (!this.data) {
                                this.data = [];
                            }

                            this.data.push(...response.data.results.map((r) => r.data));
                            this.updateRenderedData();
                        }).catch((error) => {
                            if (404 == error.response.status) {
                                this.allDataLoaded = true;
                                return;
                            }
                            console.log(error);
                        }).finally(() => {
                            this.loadingData = false;
                        });
                    } else {

                        if (!this.page) {
                            this.page = 1;
                        }

                        this.apiQueryParams.extra_params = {'table_page': this.page, 'entries': this.pageSize};

                        axios.post(this.apiUrl, this.apiQueryParams, getCsrfTokenHeader()
                        ).then((response) => {

                            if (!response || !response.data || response.data.length < 1) {
                                return;
                            }

                            if (!this.data) {
                                this.data = [];
                            }

                            if (response.data.results.length < 1){
                                this.allDataLoaded = true;
                                return;
                            }

                            this.data.push(...response.data.results.map((r) => r.data));
                            this.updateRenderedData();
                        }).catch((error) => {
                            if (404 == error.response.status) {
                                this.allDataLoaded = true;
                                return;
                            }
                            console.log(error);
                        }).finally(() => {
                            this.loadingData = false;
                        });
                    }
                }, 500);
                return;
            }

            this.updateRenderedData();
        },

        updateRenderedData() {

            if (!this.page) {
                this.lazyData = this.data.slice(0, this.pageSize);
                this.page++;
                return;
            }

            let start = this.page ? this.apiUrl ? (this.page - 1) * this.pageSize : this.page * this.pageSize : 0;
            let end = start + this.pageSize;

            if (this.infiniteScroll) {
                this.lazyData.push(...this.data.slice(start, end));
            } else {
                // TODO-DEV: Implement pagination UI
                this.lazyData = this.data.slice(start, end);
            }

            this.page++;
        },

        getQueryString() {

            if (!this.apiQueryParams) {
                return '';
            }

            let queryParams = [];

            if (!this.page) {
                this.page = 1;
            }

            this.apiQueryParams.page = this.page;

            Object.keys(this.apiQueryParams).forEach((paramName, index) => {
                 let paramValue = this.apiQueryParams[paramName];

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

        initServerSideProcessing() {
            // TODO-DEV: get config data from server and set on this
        },
    },

    mounted() {
        if(this.customParams && this.customParams.table && this.customParams.table.class){
            document.querySelector(`#${this.id}`).classList.add(this.customParams.table.class);
        }

        if (this.compData) {
            this.data = this.compData;
        }

        if (this.apiUrl) {
            this.initServerSideProcessing();
        }

        document.querySelector(`#${this.id} tbody`).addEventListener('scroll', this.lazyLoadData);
        this.lazyLoadData();

        // TODO-DEV: Implement an init validation of data (running into exceptions/warnings)
    },
});
const vRingChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true },
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': this.title,
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
                    'formatter': function (params) {
                        return `${params.seriesName} <br/> ${params.value[0]}: ${params.value[1]} (${params.percent}%)`
                    }
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
                },
                'graphic': {
                    'type': 'text',
                    'left': 'center',
                    'top': 'middle',
                    'style': {
                        'textAlign': 'center',
                        'font': "5vh 'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                        'fill': '#C2C3CD'
                    },
                },
                'series': [
                    {
                        'name': this.title,
                        'type': 'pie',
                        'radius': ['40%', '55%'],
                        'avoidLabelOverlap': false,
                        'label' : {
                            'show': true,
                            'fontSize': 18,
                            'position': 'auto',
                            'margin': '25%',
                            'formatter': function (params) {
                                return  params.value[1];
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
                    },
                ]
            },
            loading: false,
            syncing: false
        }
    },
    methods: {
        getOption: function() {
            return this.option;
        }
    }
};

const vMultipleRingChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': this.title,
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
                'legend' : {}
            },
            loading: false,
            syncing: false
        }
    },

    methods: {
        getOption: function() {
            return this.option;
        }
    }
};

const vBarChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box bar" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>
               `,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': this.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'center',
                    'padding': [5, 10, 5, 14],
                },
                'legend': {},
                'grid': {
                    'left': '2%',
                    'right': '10%',
                    'bottom': '2%',
                    'top': '15%',
                    'containLabel': true,
                },
                'tooltip': {},
                'xAxis': {},
                'yAxis': {},
                'series': []
            },
            loading: false,
            syncing: false,
            showModal: false,
            position: {},
            clearOnRefresh: true,
            percentageMode: false,
            percentageModeOriginSeries: [],
            customActionsData: {}
        }
    },
    methods: {
        getOption: function() {
            return this.option;
        },

        handlePercentageModeExtraOptions: function () {
            let extraOptions = {};

            const tooltip_formatter = (originSeries) => {
                return (params) => {
                    if (!params) {
                        return '';
                    }

                    let tooltipString = `<span>${params[0].axisValueLabel}</span></br>`;

                    params.map((param) => {
                        let series = originSeries[param.dataIndex][param.seriesName];
                        tooltipString += `${param.marker} <span>${param.seriesName}: ${series} (${param.value} %)</span></br>`;
                    });

                    return tooltipString;
                }
            }

            extraOptions['tooltip.formatter'] = tooltip_formatter(this.percentageModeOriginSeries);
            extraOptions['tooltip.trigger'] = 'axis';
            extraOptions['tooltip.axisPointer'] = {'type': 'none'};

            return extraOptions;
        }

    }
};

const vLineAndBarChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                },
                'title': {
                    'top': '3.5%',
                    'text': this.title,
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif',
                    },
                    'subtext': '',
                    'left': 'left',
                    'padding': [5, 10, 5, 14],
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
                    }
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
                        'yAxisIndex': 1
                    },
                ],
            },
            loading: false,
            syncing: false,
            customActionsData: {}
        }
    },
    methods: {
        getOption: function() {
            return this.option;
        }
    }
};

const vLineChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': this.title,
                    'top': '5%',
                    'left': 'center',
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    }
                },
                'tooltip': {
                    'trigger': 'axis'
                },
                'xAxis': {'type': 'category'},
                'yAxis': {'type': 'value'},
                'legend' : {
                    'type': 'scroll',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'bottom': 10
                }
            },
            loading: false,
            syncing: false,
            customActionsData: {}
        }
    },

    methods: {
        getOption: function() {
            return this.option;
        }
    }
};

const vAreaChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': this.title,
                    'top': '5%',
                    'left': 'center',
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    }
                },
                'tooltip': {
                    'trigger': 'axis'
                },
                'xAxis': {
                    'type': 'category',
                    'boundaryGap': false
                },
                'yAxis': {'type': 'value'},
                'legend' : {
                    'type': 'scroll',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'bottom': 10
                }
            },
            loading: false,
            syncing: false,
            percentageMode: false,
            percentageModeOriginSeries: [],
            customActionsData: {}
        }
    },

    methods: {
        getOption: function() {
            return this.option;
        },

        handlePercentageModeExtraOptions: function () {
            let extraOptions = {};

            const tooltip_formatter = (originSeries) => {
                return (params) => {
                    if (!params) {
                        return '';
                    }

                    let tooltipString = `<span>${params[0].axisValueLabel}</span></br>`;

                    params.map((param) => {
                        let series = originSeries[param.dataIndex][param.seriesName];
                        let paramValue = param.value.slice(1)[param.seriesIndex];

                        tooltipString += `${param.marker} <span>${param.seriesName}: ${series} (${paramValue} %)</span></br>`;
                    });

                    return tooltipString;
                }
            }

            extraOptions['tooltip.formatter'] = tooltip_formatter(this.percentageModeOriginSeries);
            extraOptions['tooltip.trigger'] = 'axis';

            return extraOptions;
        }
    }
};

const vScatterChart = {
    props: {
        id: { required: true },
        title: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true }
    },
    template: `<div class="box" :style=" {height: 'calc('+height+' - 10px)'}">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div :class="'sync-time ' + (exportOption ? '' : 'sync-time-no-padding')" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                       <span>Syncing data...</span>
                   </div>
                   <div class="export-option" title="Export" @click="$parent.exportData()" v-show="exportOption" data-html2canvas-ignore>
                       <i class="fa fa-download"></i>
                   </div>
                   <div :id="id" :style=" {height: height}"></div>
               </div>`,
    data: function() {
        return {
            option: {
                'textStyle': {
                    'color': '#C2C3CD',
                    'fontSize': 18,
                    'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                },
                'title': {
                    'text': this.title,
                    'top': '5%',
                    'left': 'center',
                    'textStyle': {
                        'fontSize': 24,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    }
                },
                'tooltip': {
                    'axisPointer': {
                        'type': 'cross'
                    }
                },
                'xAxis': {},
                'yAxis': {},
                'legend' : {
                    'type': 'scroll',
                    'textStyle': {
                        'fontSize': 13,
                        'color': '#C2C3CD',
                        'fontFamily': "'Source Sans Pro','Helvetica Neue',Helvetica,Arial,sans-serif",
                    },
                    'bottom': 10
                }
            },
            loading: false,
            syncing: false
        }
    },

    methods: {
        getOption: function() {
            return this.option;
        }
    }
};

const vCharts = {
    props: {
        position: { required: true, type: Object },
        type: { required: true },
        id: { required: true },
        title: { required: true },
        legend: { required: true },
        exportOption: { required: true },
        customActions: { required: true },
        height: { required: true },
        extraOptions: { required: true },
        chartsThemeName: { required: true }
    },
    template: `<component :is="currentChart" :id="id" :title="title" :exportOption="exportOption" customActions="customActions" :height="height"></component>`,
    computed: {
        currentChart: function() {
            return this.type;
        }
    },
    data: function() {
        return {
            chart: null,
            showModal: false,
        }
    },
    methods: {
        render: function() {
            let dom = document.getElementById(this.id);
            let option = this.$children[0].getOption();

            if (!dom) {
                console.warn(`Could not initiate charts ${this.id}.`);
                return;
            }

            try {
               const themeName = this.chartsThemeName ? this.chartsThemeName : null;
               // If a theme is required you have to use the
               // imported theme name in the theme name variable
               // and use the init method below.
               // this.chart = echarts.init(dom, themeName);
               this.chart = echarts.init(dom, themeName);
               this.chart.on('click', (event) => this.$parent.showSeriesModal(event, this.id, this.title, this.position));
            }
            catch (error) {
                console.log(`${this.id}`, error);
            }

            if (this.legend && Object.keys(this.legend).length > 0) {
                Object.assign(option['legend'], this.legend);
            }

            if (this.extraOptions) {
                option = this.setExtraOptions(option, this.extraOptions);
            }

            this.chart.setOption(option, true);

            if (this.customActions && this.customActions.length > 0) {
                setCustomContextMenu(this.id, this.customActions, this.handleCustomContextMenuActions);
            }

            this.refresh({}, true)
        },

        refresh: async function (filters, render=false) {
            if (render) {
                this.$children[0].loading = true;
            } else {
                this.$children[0].syncing = true;
            }

            let results = await this.getData(filters);

            if (!results) {

                if (render) {
                    this.$children[0].loading = false;
                } else {
                    this.$children[0].syncing = false;
                }

                return;
            }

            try {

                // Echarts Bar Chart bug fix. Check to replace in next versions...
                if (this.$children[0].clearOnRefresh) {
                    this.chart.setOption(this.$children[0].getOption(), true);
                }

                this.chart.setOption(results.data);

                if (results.extra_options && Object.keys(results.extra_options).length > 0) {
                    let option = this.setExtraOptions(this.normalizeOptions(), results.extra_options);
                    this.chart.setOption(option, true);

                    if ('dataZoom' in results.extra_options) {
                        this.chart.on('dataZoom', this.handleZoom);
                    }

                }

                if (results.data.percentage_mode && results.data.origin_series) {
                    if(this.$children[0].percentageMode != undefined) {
                        this.$children[0].percentageMode = results.data.percentage_mode;
                        this.$children[0].percentageModeOriginSeries = results.data.origin_series;

                        let extraOptions = this.$children[0].handlePercentageModeExtraOptions();
                        let option = this.setExtraOptions(this.normalizeOptions(), extraOptions);
                        this.chart.setOption(option, true);
                    }
                }

                if (results.custom_actions_data && Object.keys(results.custom_actions_data).length > 0) {
                    if (this.$children[0].customActionsData) {
                        this.$children[0].customActionsData = results.custom_actions_data;
                    }
                }

            } catch (error) {
                console.log(`${this.chartId}`, error);
            }

            if (render) {
                this.$children[0].loading = false;
            } else {
                this.$children[0].syncing = false;
            }
        },

        getData: async function (filters) {
            return await axios.post('data/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': filters}, getCsrfTokenHeader()
            ).then((response) => {
                return response.data;
            }).catch((error) => {
                console.log(`${this.id}`, error);
            })
        },

        normalizeOptions: function() {
            let options = this.chart.getOption();

            Object.entries(options).forEach(([key, value]) => {

                if (!Array.isArray(value)) {
                    return;
                }

                if (value.length == 0 || value.length > 1) {
                    return;
                }

                options[key] = value[0];
            });

            return options
        },

        setExtraOptions: function (option, extraOptions) {
            Object.keys(extraOptions).forEach((key) => {
                let currentProp = option;
                const optionsArr = key.split(".");

                optionsArr.forEach((value, index) => {
                    if (currentProp[value] && index !== optionsArr.length - 1) {
                        currentProp = currentProp[value];
                    } else {
                        currentProp[value] = extraOptions[key];
                    }
                });
            });

            return option;
        },

        exportData: function () {
            this.$children[0].loading = true;

            axios.post('export/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': this.$parent.filters}, { responseType: 'blob', ...getCsrfTokenHeader()}
            ).then((response) => {
                let fileURL = window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']}));
                let fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', response.headers['content-disposition']);
                document.body.appendChild(fileLink);
                fileLink.click();
                document.body.removeChild(fileLink);
            }).catch((error) => {
                console.log(`${this.id}`, error);
            });

            this.$children[0].loading = false;
        },

        handleZoom: function(params) {
            let syncZoomSwitch = document.querySelector(`#sync-zoom-page-${this.position.page}`);

            if (!syncZoomSwitch) {
                return;
            }

            let syncZoom = syncZoomSwitch.checked;

            if (!syncZoom) {
                return;
            }

            let { start, end } = params;

            if ('skipSearch' in params) {
                return;
            }

            let zoomComponents = this.$parent.$children.filter((c) => {
                return c.position &&
                    c.position.page == this.position.page &&
                    c.chart &&
                    c.id != this.id &&
                    'dataZoom' in c.chart.getOption() &&
                    c.chart.getOption()['dataZoom'].length > 0
            });

            zoomComponents.forEach((component) => {
                component.chart.dispatchAction({
                    type: 'dataZoom',
                    start: start,
                    end: end,
                    skipSearch: true
                });
            });
        },

        // *** Custom Actions *** //

        insertEvent: function (selectedEvent, selectedColor='#000', eventText='') {
            let option = this.chart.getOption();

            if ((!'series' in option) || option['series'].length == 0){
                return;
            }

            if (!('markLine' in option['series'][0])) {
                option['series'][0]['markLine'] = {'data': []}
            }

            let axis = this.$children[0].customActionsData['insertEvents']['axis'];

            let markLineOptions = {
                label: {
                    normal: {
                        formatter: eventText,
                        color: selectedColor
                    },
                },
                itemStyle: {
                    normal: {
                      color: selectedColor,
                    }
                }
            };

            markLineOptions[axis] = selectedEvent;

            option['series'][0]['markLine']['data'].push(markLineOptions);

            // Echarts Bar Chart bug fix. Check to replace in next versions...
            if (this.$children[0].clearOnRefresh) {
                this.chart.setOption(option, true);
            } else {
                this.chart.setOption(option);
            }

            setCustomContextMenu(this.id, this.customActions.concat(['clearEvents']), this.handleCustomContextMenuActions);
        },

        clearEvent: function (selectedEvent) {
            let option = this.chart.getOption();

            if ((!'series' in option) || option['series'].length == 0){
                return;
            }

            if (!('markLine' in option['series'][0])) {
                return;
            }

            option['series'][0]['markLine']['data'].splice(selectedEvent, 1);

            // Echarts Bar Chart bug fix. Check to replace in next versions...
            if (this.$children[0].clearOnRefresh) {
                this.chart.setOption(option, true);
            } else {
                this.chart.setOption(option);
            }

            if (option['series'][0]['markLine']['data'].length == 0) {
                setCustomContextMenu(this.id, this.customActions, this.handleCustomContextMenuActions);
            }
        },

        clearAllEvents: function() {
            let option = this.chart.getOption();

            if ((!'series' in option) || option['series'].length == 0){
                return;
            }

            if (!('markLine' in option['series'][0])) {
                return;
            }

            option['series'][0]['markLine']['data'] = [];

            // Echarts Bar Chart bug fix. Check to replace in next versions...
            if (this.$children[0].clearOnRefresh) {
                this.chart.setOption(option, true);
            } else {
                this.chart.setOption(option);
            }

            setCustomContextMenu(this.id, this.customActions, this.handleCustomContextMenuActions);
        },

        handleCustomContextMenuActions: function (el, action) {
            if (!action) {
                return;
            }

            if (action.text() == 'Insert Events') {
                this.$parent.clearCustomActionModal('insert-events');
                this.handleInsertEventsAction();
                this.$parent.showCustomActionModal('insert-events');
            } else if (action.text() == 'Clear Events') {
                this.$parent.clearCustomActionModal('clear-events');
                this.handleClearEventsAction();
                this.$parent.showCustomActionModal('clear-events');
            }
        },

        handleInsertEventsAction: function() {
            let insertEventsComponentId = document.querySelector('#insert-events-component-id');
            let insertEventsList = document.querySelector('#insert-events-events-list');

            insertEventsComponentId.value = this.id;
            insertEventsList.innerHTML = '';

            if (this.$children[0].customActionsData && 'insertEvents' in this.$children[0].customActionsData) {

                if (!'data' in this.$children[0].customActionsData['insertEvents']) {
                    return;
                }

                this.$children[0].customActionsData['insertEvents']['data'].forEach((data) =>{
                    let option = document.createElement('option');
                    option.value = data;
                    option.innerHTML = data;
                    insertEventsList.appendChild(option);
                });
            }
        },

        handleClearEventsAction: function () {
            let chartOption = this.chart.getOption();
            let clearEventsComponentId = document.querySelector('#clear-events-component-id');
            let clearEventsList = document.querySelector('#clear-events-events-list');

            clearEventsComponentId.value = this.id;
            clearEventsList.innerHTML = '';

            if ((!'series' in chartOption) || chartOption['series'].length == 0){
                return;
            }

            if (!('markLine' in chartOption['series'][0])) {
                return;
            }

            let events = chartOption['series'][0]['markLine']['data'];
            let axis = this.$children[0].customActionsData['insertEvents']['axis'];


            events.forEach((eventData, i) => {
                let option = document.createElement('option');
                let color = eventData['itemStyle']['color'];
                let text = eventData['label']['formatter'];
                let axisEvent = eventData[axis];

                color = color.charAt(0).toUpperCase() + color.substr(1);

                option.value = i;
                option.innerHTML = (text != "") ? `${axisEvent} - ${text} (${color})`: `${axisEvent} (${color})`;
                clearEventsList.appendChild(option);
            });
        }
    }
};

const vDataTable = {
    props: {
        position: { required: true, type: Object },
        id: { required: true },
        title: { required: true },
        entries: { required: true },
        exportOption: { required: true },
        height: { required: true },
    },
    delimiters: ['[[', ']]'],
    template: `<div class="box box-table" :style="{height: 'calc('+height+' - 10px)'}">
                    <div class="overlay" v-show="isLoading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin"></i>
                   </div>
                   <div class="box-header">
                        <h3 class="box-title">[[title]]</h3>
                        <div class="box-tools pull-right">
                            <div class="syncing-message-table" title="Syncing data..." v-show="isSyncing" data-html2canvas-ignore>
                               <i class="fa fa-refresh fa-spin"></i>
                               <span>Syncing data...</span>
                            </div>

                            <!-- Here goes the arrows to change the table page -->
                            <span class="pages-label" v-if="hasPagination" data-html2canvas-ignore>Showing [[ itemsStartIndex ]] - [[ itemsEndIndex ]] of [[ itemsCount ]] items / Page [[ paginationIndex ]] of [[ tablePagesCount ]] Pages </span>
                            <a class="pages-change-control" v-if="hasPagination" href="#" @click="changePage(-1);" data-html2canvas-ignore>
                                <span class="fa fa-angle-left"></span>
                            </a>
                            <a class="pages-change-control" v-if="hasPagination" href="#" @click="changePage(1);" data-html2canvas-ignore>
                                <span class="fa fa-angle-right"></span>
                            </a>
                            <div class="export-option-table" title="Export" @click="exportData()" v-show="exportOption"  data-html2canvas-ignore>
                                <i class="fa fa-download"></i>
                            </div>
                        </div>
                   </div>
                   <div class="box-body" v-html="tableContent"></div>
               </div>`,
    data: function() {
        return {
            apiURL: 'data/',
            queryParams: {'id': this.id, 'page': this.position.page, 'filters': {}},
            customParams: {
                'table': {
                    id: `v-table-${this.id}`,
                    class: 'dashboardTable'
                }
            },
            customStyle: {
                'tbody': {maxHeight: (this.title) ? `calc(${this.columnHeight}vh - 94px)`: `calc(${this.columnHeight}vh - 60px)`},
                'tr': {display: 'flex'}
            },
            showTable: true,
            tableContent: '',
            tablePagesCount: 0,
            itemsPerPage: 0,
            itemsStartIndex: 0,
            itemsEndIndex: 0,
            itemsCount: 0,
            paginationIndex: 1,
            isLoading: true,
            isSyncing: false,
            filters: {},
            hasPagination: false
        }
    },
    methods: {

        changePage: async function (direction) {
            if(this.paginationIndex + direction >= 1 && this.paginationIndex + direction <= this.tablePagesCount) {
                this.paginationIndex += direction;
                this.isSyncing = true;
                await this.getData(this.filters);
                this.isSyncing = false;
            }
        },

        render: async function(filters) {
            this.filters = filters;
            this.isLoading = true;
            await this.getData(filters);
            this.isLoading = false;
        },

        refresh: async function (filters) {
            this.filters = filters;
            this.isSyncing = true;
            this.paginationIndex = 1;
            await this.getData(filters);
            this.isSyncing = false;
        },

        getData: async function (filters) {
            return await axios.post('data/', {'id': this.id, 'pagination_index': this.paginationIndex, 'page': this.position.page, 'position': this.position, 'entries':  this.entries, 'filters': filters}, getCsrfTokenHeader()
            ).then((response) => {
                if(response && response.data) {
                    this.tableContent = response.data.table_html ? response.data.table_html : '';

                    this.hasPagination = !!response.data.pagination

                    if(this.hasPagination) {
                        const pagination = response.data.pagination;
                        this.paginationIndex = pagination.pagination_index;
                        this.itemsCount = pagination.items_count;
                        this.itemsStartIndex = pagination.items_start_index;
                        this.itemsEndIndex = pagination.items_end_index;
                        this.itemsPageCount = pagination.items_page_count;
                        this.itemsPerPage = pagination.items_per_page;
                        this.tablePagesCount = pagination.table_pages_count;
                    }
                }

                return response.data;

            }).catch((error) => {
                console.log(`${this.id}`, error);
            })
        },

        exportData: function () {
            this.loading = true;

            axios.post('export/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': this.$parent.filters}, { responseType: 'blob', ...getCsrfTokenHeader()}
            ).then((response) => {
                let fileURL = window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']}));
                let fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', response.headers['content-disposition']);
                document.body.appendChild(fileLink);
                fileLink.click();
                document.body.removeChild(fileLink);
            }).catch((error) => {
                console.log(`${this.id}`, error);
            });

            this.loading = false;
        }
    }
};

const vSimpleCard = {
    props: {
        id: { required: true },
        initialTitle: { required: true },
        height: { required: true },
    },
    delimiters: ['[[', ']]'],
    template: `<div class="box">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin card-overlay"></i>
                   </div>
                   <div :id="id" :style="{height: height, position: 'relative'}">
                       <div class="sync-time sync-time-no-padding" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                           <i class="fa fa-refresh fa-spin"></i>
                           <span>Syncing data...</span>
                       </div>
                       <div class="info-box">
                           <span :class="'info-box-icon ' + color"><i :class="'fa ' + icon"></i></span>
                           <div class="info-box-content">
                               <span class="info-box-text">[[ title ]]</span>
                               <span class="info-box-number">[[ content ]]</span>
                           </div>
                       </div>
                   </div>
               </div>
               `,
    data: function() {
        return {
            title: '',
            content: '',
            icon: '',
            color: '',
            syncing: false,
            loading: false
        }
    },
    mounted() {
        this.title = this.initialTitle;
    }
};

const vPercentageCard = {
    props: {
        id: { required: true },
        initialTitle: { required: true },
        height: { required: true },
    },
    delimiters: ['[[', ']]'],
    template: `<div class="box">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin card-overlay"></i>
                   </div>
                    <div :id="id" :style=" {height: height}">
                       <div class="sync-time sync-time-no-padding" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                           <i class="fa fa-refresh fa-spin"></i>
                           <span>Syncing data...</span>
                       </div>
                       <div :class="'info-box ' + color">
                           <span class="info-box-icon"><i :class="'fa ' + icon"></i></span>
                           <div class="info-box-content">
                               <span class="info-box-text">[[ title ]]</span>
                               <span class="info-box-number">[[ content ]]</span>
                               <div class="progress">
                                  <div class="progress-bar" :style="'width: ' + percentage + '%'"></div>
                               </div>
                               <span class="progress-description">
                                   [[ percentageDescription ]]
                               </span>
                           </div>
                       </div>
                   </div>
                 </div>
               `,
    data: function() {
        return {
            title: '',
            content: '',
            percentage: 0,
            percentageDescription: '',
            icon: '',
            color: '',
            syncing: false,
            loading: false
        }
    },
    mounted() {
        this.title = this.initialTitle;
    }
};

const vLinkCard = {
    props: {
        id: { required: true },
        initialTitle: { required: true },
        exportOption: { required: true },
        height: { required: true },
    },
    delimiters: ['[[', ']]'],
    template: `<div class="box">
                   <div class="overlay" v-show="loading" data-html2canvas-ignore>
                       <i class="fa fa-refresh fa-spin card-overlay"></i>
                   </div>
                   <div :id="id" :style=" {height: height}">
                       <div class="sync-time sync-time-no-padding" title="Syncing data..." v-show="syncing" data-html2canvas-ignore>
                           <i class="fa fa-refresh fa-spin"></i>
                           <span>Syncing data...</span>
                       </div>
                       <div :class="'small-box ' + color">
                           <div class="inner">
                               <h3>[[ title ]]</h3>
                               <p>[[ content ]]</p>
                           </div>
                           <div class="icon">
                               <i :class="'fa ' + icon"></i>
                           </div>
                           <a href="#" class="small-box-footer" @click="$parent.exportData()">
                              Export <i class="fa fa-download"></i>
                           </a>
                       </div>
                   </div>
                 </div>
              `,
    data: function() {
        return {
            title: '',
            content: '',
            icon: '',
            color: '',
            syncing: false,
            loading: false
        }
    },
    mounted() {
        this.title = this.initialTitle;
    }
};

const vCards = {
    props: {
        position: { required: true, type: Object },
        type: {required: true},
        id: {required: true},
        title: {required: true},
        exportOption: {required: true},
        height: {required: true},
        extraOptions: { required: true }
    },
    template: `<component :is="currentCard" :id="id" :initialTitle="title" :exportOption="exportOption" :height="height"></component>`,
    computed: {
        currentCard: function () {
            return this.type;
        }
    },
    data: function () {
        return {
            card: null
        }
    },
    methods: {
        render: async function(filters) {
            this.$children[0].loading = true;

            if (this.extraOptions) {
                this.setExtraOptions(this.extraOptions)
            }

            await this.refresh(filters);

            this.$children[0].loading = false;
        },

        refresh: async function (filters) {

            this.$children[0].syncing = true;

            let results = await this.getData(filters);

            if (!results) {
                this.$children[0].syncing = false;
                return;
            }

            if ('title' in results) {
                this.$children[0].title = results.title;
            }

            if ('content' in results) {
                this.$children[0].content = results.content;
            }

            if (this.type == 'v-percentage-card') {
                this.$children[0].percentage = ('percentage' in results) ? results.percentage : 0;
            }

            if (results.extra_options && Object.keys(results.extra_options).length > 0) {
                this.setExtraOptions(results.extra_options);
            }

            this.$children[0].syncing = false;
        },

        getData: async function (filters) {
            return await axios.post('data/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': filters}, getCsrfTokenHeader()
            ).then((response) => {
                return response.data;
            }).catch((error) => {
                console.log(`${this.id}`, error);
            })
        },

         setExtraOptions: function (extraOptions) {
             if ('content' in extraOptions) {
                 this.$children[0]['content'] = extraOptions['content']
             }

             if ('percentage_description' in extraOptions) {
                 this.$children[0]['percentageDescription'] = extraOptions['percentage_description']
             }

             if ('icon' in extraOptions) {
                 this.$children[0]['icon'] = extraOptions['icon']
             }

             if ('color' in extraOptions) {
                 this.$children[0]['color'] = extraOptions['color']
             }
         },

        exportData: function () {
            this.$children[0].loading = true;

            axios.post('export/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': this.$parent.filters}, { responseType: 'blob', ...getCsrfTokenHeader()}
            ).then((response) => {
                let fileURL = window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']}));
                let fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', response.headers['content-disposition']);
                document.body.appendChild(fileLink);
                fileLink.click();
                document.body.removeChild(fileLink);
            }).catch((error) => {
                console.log(`${this.id}`, error);
            });

            this.$children[0].loading = false;
        }
    }
};

const vCustomHTML = {
    props: {
        position: { required: true, type: Object },
        type: {required: true},
        id: {required: true},
        title: {required: true},
        exportOption: {required: true},
        height: {required: true},
    },
    delimiters: ['[[', ']]'],
    template: `
                <div class="box box-table" :style="{height: 'calc('+height+' - 10px)'}">
                    <div class="overlay" v-show="isLoading" data-html2canvas-ignore>
                        <i class="fa fa-refresh fa-spin"></i>
                    </div>
                    <div class="box-header">
                        <h3 class="box-title">[[title]]</h3>
                        <div class="box-tools pull-right">
                            <div class="syncing-message-table" title="Syncing data..." v-show="isSyncing" data-html2canvas-ignore>
                                <i class="fa fa-refresh fa-spin"></i>
                                <span>Syncing data...</span>
                            </div>
                            <div class="export-option-table" title="Export" @click="exportData()" v-show="exportOption" data-html2canvas-ignore>
                                <i class="fa fa-download"></i>
                          </div>
                        </div>
                    </div>
                    <div class="box-custom-html-content" v-html="content"></div>
               </div>
    `,
    data: function () {
        return {
           isLoading: false,
           isSyncing: false,
           content: ''
        }
    },
    methods: {
        render: async function(filters) {
            this.isLoading = true;
            await this.refresh(filters);
            this.isLoading = false;
        },

        refresh: async function (filters) {
            this.isSyncing = true;
            await this.getData(filters);
            this.isSyncing = false;
        },

        getData: async function (filters) {
            return await axios.post('data/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': filters}, getCsrfTokenHeader()
            ).then((response) => {
                if(response.data && response.data.content) {
                    this.content = response.data.content;
                }
                return response.data;
            }).catch((error) => {
                console.log(`${this.id}`, error);
            })
        },

        exportData: function () {
            this.isLoading = true;

            axios.post('export/', {'id': this.id, 'page': this.position.page, 'position': this.position, 'filters': this.$parent.filters}, { responseType: 'blob', ...getCsrfTokenHeader()}
            ).then((response) => {
                let fileURL = window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']}));
                let fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', response.headers['content-disposition']);
                document.body.appendChild(fileLink);
                fileLink.click();
                document.body.removeChild(fileLink);
            }).catch((error) => {
                console.log(`${this.id}`, error);
            });

            this.isLoading = false;
        }
    }
};

const vChartModal = {
    delimiters: ['[[', ']]'],
    template: `
                <div class="modal-blur">
                    <div class="modal-box">
                        <div class="overlay" v-show="isLoading">
                           <i class="fa fa-refresh fa-spin card-overlay"></i>
                        </div>
                        <div class="modal-title">[[ this.title ]]</div>
                        <div class="modal-html-content" v-html="content"></div>
                        <div class="modal-actions">
                            <button @click="onCloseClick()" class="btn btn-success btn-filters">Close</button>
                        </div>
                    </div>
                </div>
    `,
    data: function () {
        return {
           isLoading: false,
           content: '',
           title: 'Modal Title'
        }
    },
    methods: {
        render: async function(clickEvent, id, title, position, filters) {
            this.title = title ? title : this.title;
            delete clickEvent.event;
            const clickEventObj = JSON.parse(JSON.stringify(clickEvent));
            return await this.getData(id, position, filters, clickEventObj);
        },

        getData: async function (id, position, filters, clickEventObj) {
            this.isLoading = true;

            const content = await axios.post('detail/', {'id': id, 'position': position, 'filters': filters, 'click_event_obj': clickEventObj}, getCsrfTokenHeader()
            ).then((response) => {
                if(response.data && response.data.content) {
                    this.content = response.data.content;
                }
                    return true;

                }).catch((error) => {
                    console.log(`${this.id}`, error);
                    return false;
                });

            this.handleTable();
            this.isLoading = false;

            return content;
        },

        handleTable: function() {
            let modalTable = document.querySelector('table.data_tables');

            if (!modalTable) {
                return;
            }

            renderDataTables();
            setTimeout( () => {
            $('table.data_tables').DataTable().columns.adjust();
            }, 1);
        },

        onCloseClick: function() {
            this.$parent.showModal = false;
        }
    }
};

Vue.component('v-ring-chart', vRingChart);
Vue.component('v-multiple-ring-chart', vMultipleRingChart);
Vue.component('v-bar-chart', vBarChart);
Vue.component('v-line-and-bar-chart', vLineAndBarChart);
Vue.component('v-line-chart', vLineChart);
Vue.component('v-area-chart', vAreaChart);
Vue.component('v-scatter-chart', vScatterChart);
Vue.component('v-chart', vCharts);
Vue.component('v-chart-modal', vChartModal);

Vue.component('v-data-table', vDataTable);

Vue.component('v-simple-card', vSimpleCard);
Vue.component('v-percentage-card', vPercentageCard);
Vue.component('v-link-card', vLinkCard);
Vue.component('v-card', vCards);

Vue.component('v-custom-html', vCustomHTML);

Vue.config.silent = true;

let dashboard = new Vue({
    el: '#dashboard',
    delimiters: ['[[', ']]'],
    beforeMount: function () {
       Vue.config.silent = false;
    },
    props: ['totalPages'],
    data: {
        currentPage: 0,
        highestPageIndex: 0,
        filters: {},
        sync: true,
        syncTime: 300000, // Milliseconds
        syncTimeout: null,
        showModal: false,
        changesObject: {},
        seriesModalRef: null
    },
    watch: {
        currentPage: function () { this.paginationHandler(); },
        filters: function () { this.refreshComponents(); },
        sync: function () { this.startStopSync(); }
    },
    mounted() {
        this.setNavExtraCommandsEvents();
        this.setFilters(this.currentPage, false);
        this.renderComponents();
        this.setSyncInterval();
        this.createChangesObject();
        this.seriesModalRef = this.$children.find(element => element.$el.className === 'modal-blur');

       let timeout;

        document.addEventListener('mousemove', () => {
            let navigationElements = document.querySelectorAll('#previous-page, #next-page');
            clearTimeout(timeout);
            navigationElements.forEach((elm) => elm.classList.add('visible'));
            timeout = setTimeout(() => { navigationElements.forEach((elm) => elm.classList.remove('visible')) }, 500);
        });
    },
    methods: {
        createChangesObject: function() {
            for(let pageIndex=0;pageIndex<totalPages;pageIndex++)
                this.changesObject[pageIndex] = { 'hasChanges': false }
        },

        // *** Pagination *** //
        paginate: function (action) {
            if(action != 'prev' && action != 'next'){
                return;
            }

            if (action == 'prev'){
                (this.currentPage > 0) ? this.currentPage-- : this.currentPage;
            } else {
                (this.currentPage < totalPages - 1) ? this.currentPage++ : this.currentPage;
            }
        },

        paginationHandler: function() {
            this.clearSyncInterval();

            let self = this;

            setTimeout(() => {
                if (this.currentPage > this.highestPageIndex) {
                    this.highestPageIndex = this.currentPage;
                    self.setNavExtraCommandsEvents();
                    self.renderComponents();
                } else if(this.changesObject[this.currentPage]['hasChanges']) {
                    self.refreshComponents();
                    this.changesObject[this.currentPage]['hasChanges'] = false;
                }
            }, 500);

            if (this.sync) {
                this.setSyncInterval();
            }

            this.setFilters(this.currentPage, false);
        },

        // *** Components *** //
        renderComponents: function() {
            this.$children.filter((d) => { if(d.position && d.position.page == this.currentPage && d.render) d.render()});
        },

        refreshComponents: function () {
            this.$children.filter((d) => { if(d.position && d.position.page == this.currentPage)d.refresh(this.filters[this.currentPage] || {})});
        },

        resizeComponents: function() {
            this.$children.forEach(children => {
                if (children.position && children.position.page == this.currentPage && children.chart) {
                    children.chart.resize();
                }
            })
        },

        // *** Nav Extra Commands & Filters *** //
        setNavExtraCommandsEvents: function() {
            let navExtraCommandsForm = document.querySelector(`#nav-extra-commands-${this.currentPage}-form`);

            if(!navExtraCommandsForm){
                return;
            }

            let self = this;

            navExtraCommandsForm.addEventListener("input", function () {
                self.setFilters(self.currentPage);
            });
        },

        showFiltersModal(page) {
            if (!page) {
                return;
            }
            showModalElement(`#filters-modal-page-${page}`);
        },

        async showSeriesModal(clickEvent, id, title, position) {
            if(this.seriesModalRef && clickEvent && clickEvent.seriesIndex != null) {
                this.showModal = await this.seriesModalRef.render(clickEvent, id, title, position, this.filters);
            }
        },

        setFilters(page, refreshComponents=true) {
            if (page == null || page == undefined) {
                return;
            }

            let pageForm = document.querySelector(`#filter-${page}-form`);
            let navExtraCommandsForm = document.querySelector(`#nav-extra-commands-${page}-form`);

            if(!pageForm && !navExtraCommandsForm) {
                return;
            }

            let pageFormData = (pageForm) ? serializeForm(pageForm, `filter_${page}`) : {};

            if(navExtraCommandsForm) {
                let navExtraCommandsFormData = serializeForm(navExtraCommandsForm, `nav_extra_commands_${page}`);

                if (navExtraCommandsFormData && Object.keys(navExtraCommandsFormData).length > 0) {
                    pageFormData['NAV_EXTRA_COMMANDS'] = navExtraCommandsFormData;
                }
            }

            this.filters[page] = pageFormData;

            if (refreshComponents) {
                this.filters = JSON.parse(JSON.stringify(this.filters)); // Trigger Vue.JS watch
            }
        },

        clearFilters(page) {
            let filterForm = document.getElementById(`filter-${page}-form`);

            if (!filterForm) {
                return;
            }

            filterForm.reset();

            Array.prototype.slice.call(filterForm.elements).forEach(function (field) {
                field.dispatchEvent(new CustomEvent('change'));
            });

            this.setFilters(page);
        },

        // *** Sync *** //
        setChangesFlag: function(indexToAvoid=null) {
            for(let pageIndex=0;indexToAvoid != null && pageIndex<totalPages;pageIndex++)
                   this.changesObject[pageIndex]['hasChanges'] = pageIndex != indexToAvoid;
        },

        setSyncInterval() {
            this.syncTimeout = setInterval(() => this.refreshComponents(), this.syncTime);
        },

        clearSyncInterval() {
            clearInterval(this.syncTimeout);
        },

        changeSyncTime(newSyncTime) {
            this.syncTime = newSyncTime;
            this.clearSyncInterval();

            if (this.sync) {
                this.refreshComponents();
                this.setSyncInterval();
            }
        },

        startStopSync() {
            this.clearSyncInterval();

            if (this.sync) {
                this.refreshComponents();
                this.setSyncInterval();
                this.setChangesFlag(this.currentPage);
            }
        },

        // *** Print & Export *** //
        print: function () {
            let printElement = `#page-${this.currentPage} > .grid-wrapper`;

            // Necessary to fix the html2canvas bug when the content is scrolled down
            document.querySelector(printElement).scrollTo(0,0);

            html2canvas(document.querySelector(printElement), {height: document.querySelector(printElement).scrollHeight}).then(canvas => {
                let link = document.createElement('a');

                if (typeof link.download === 'string') {
                    link.href = canvas.toDataURL();
                    link.download = `dashboard-page-${this.currentPage + 1}.png`;

                    // Firefox requires the link to be in the body
                    document.body.appendChild(link);

                    // Simulate click
                    link.click();

                    // Remove the link when done
                    document.body.removeChild(link);
                } else {
                    window.open(canvas.toDataURL());
                }
            });
        },

        exportToPDF: function () {
            let printElement = `#page-${this.currentPage} > .grid-wrapper`;

            // Necessary to fix the html2canvas bug when the content is scrolled down
            document.querySelector(printElement).scrollTo(0,0);

            html2canvas(document.querySelector(printElement), {height: document.querySelector(printElement).scrollHeight}).then(canvas => {
                let imgData = canvas.toDataURL();

                let orientation = (canvas.height > canvas.width) ? 'p': 'l';
                let doc = new jsPDF(orientation, 'pt', 'a4', true);

                let maxWidth = doc.internal.pageSize.width;
                let maxHeight = doc.internal.pageSize.height;
                let width = canvas.width;
                let height = canvas.height;
                let ratio = 0;

                if (width > maxWidth) {
                    ratio = maxWidth / width;
                    height = height * ratio;
                    width = width * ratio;
                }

                if (height > maxHeight) {
                    ratio = maxHeight / height;
                    width = width * ratio;
                    height = height * ratio;
                }

                doc.addImage(imgData, 'PNG', 0, 0, width, height,'','FAST');
                doc.save(`dashboard-page-${this.currentPage + 1}.pdf`);
            });
        },

        // *** Custom Actions (triggered by mouse Right-click button) *** //
        showCustomActionModal: function(customAction) {
           let modal = `#${customAction}-custom-action-modal`;
           showModalElement(modal);
        },

        clearCustomActionModal: function (customAction) {
           let form = `#${customAction}-form`;
           document.querySelector(form).reset();
        },

        insertEvents: function () {
            let componentId = document.querySelector('#insert-events-component-id').value;

            if (!componentId) {
                return;
            }

            let component = this.$children.find((component) => { return component.id == componentId });

            if (!component || !component.insertEvent) {
                return;
            }

            let selectedEvent = document.querySelector('#insert-events-events-list').value;
            let selectedColor = document.querySelector('#insert-events-colors-list').value;
            let eventText = document.querySelector('#insert-events-text').value;
            let insertEventToAll = document.querySelector('#insert-events-insert-to-all').checked;

            if (!insertEventToAll) {
                component.insertEvent(selectedEvent, selectedColor, eventText);
            } else {
                let components = this.$children.filter((c) => {
                    return c.position &&
                        c.position.page == this.currentPage &&
                        c.chart &&
                        c.$children[0].customActionsData &&
                        'insertEvents' in c.$children[0].customActionsData &&
                        c.$children[0].customActionsData['insertEvents']['data'].includes(selectedEvent);
                });

                components.forEach((component) => {
                    component.insertEvent(selectedEvent, selectedColor, eventText);
                });
            }
        },

        clearEvents: function () {
            let componentId = document.querySelector('#clear-events-component-id').value;

            if (!componentId) {
                return;
            }

            let component = this.$children.find((component) => { return component.id == componentId });

            if (!component || !component.clearEvent) {
                return;
            }

            let selectedEvent = document.querySelector('#clear-events-events-list').value;

            component.clearEvent(selectedEvent);
        },

        clearAllPageEvents: function() {
            let components = this.$children.filter((c) => {
                return c.position &&
                    c.position.page == this.currentPage &&
                    c.chart &&
                    c.$children[0].customActionsData &&
                    'insertEvents' in c.$children[0].customActionsData;
            });

            components.forEach((component) => {
                component.clearAllEvents();
            });
        }
    }
});

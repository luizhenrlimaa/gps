let chart;

var MapControl = (function(){

    splitScreen = function(){
        Split(['#map_container', '#info_area_container'], {
            gutterSize: 10,
            sizes: [53, 32.5],
            direction: 'vertical',
            minSize: [100, 50]
        });
    };

    setEvents = function() {

        // Map resize
        $(window).on("resize", function () {
            map_control.resizeMap();
            info_area_control.handleAreasHeight();

            let infoAreaIsMinimized = $('#info-area-icon.fa.fa-chevron-left').length == 1;

            if (infoAreaIsMinimized) {
                info_area_control.decreaseAreaControl();
            } else {
                info_area_control.increaseAreaControl();
            }
        }).trigger("resize");

        // Split bar change
        $('.gutter').mousemove(function() {
            map_control.resizeMap();
            info_area_control.handleAreasHeight();
        });

        let sandwichBtn = document.querySelector('a[href="#home"]');

        if (!sandwichBtn) {
            return;
        }

        sandwichBtn.click();
    };

    init = function() {
        splitScreen();
        setEvents();
        map_control.resizeMap();
    }

    return {
        init: init
    }
})();

function ChartLoad() {

    var dom = document.getElementById("chart");
    chart = echarts.init(dom);
    var app = {};
    option = null;
    var data = genData();

    option = {
        title: {
            text: "Cluster's Sites Status",
            subtext: '',
            left: 'left',
            padding: [
                5,  // up
                10, // right
                5,  // down
                14, // left
            ]
        },
        color: json.chart_data.map((data) => data.color),
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
            type: 'scroll',
            orient: 'vertical',
            right: 10,
            top: 20,
            bottom: 20,
            textStyle: {
                fontSize: 12,
            },
            bottom: 0,
            data: data.legendData,
            selected: data.selected
        },
        series: [
            {
                name: 'Detail:',
                type: 'pie',
                radius: ['0', '75%'],
                center: ['35%', '50%'],
                top: '2%',
                data: data.seriesData,
                label : {
                    show: true,
                    fontSize: 30,
                    fontStyle: 'bold',
                    position: 'auto',
                    margin: '25%',
                    formatter : function (params) {
                          return  params.value
                    },
                },
                labelLine: {
                    show: true,
                    type: 'dashed'
                },
            }
        ]
    };

    function genData() {
        var legendData = [];
        var seriesData = [];
        var selected = {};

        json.chart_data.forEach((status) => {
            legendData.push(status.name);
            seriesData.push({name: status.name, value: status.value});
        });

        return { legendData: legendData, seriesData: seriesData, selected: selected };
    };

    if (option && typeof option === "object") {
        chart.setOption(option, true);
    }
}

$(document).ready(function(){
    MapControl.init();
});
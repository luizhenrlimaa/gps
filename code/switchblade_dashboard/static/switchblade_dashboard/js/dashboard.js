
const MODAL_CONTENT_TYPE = {
    HTML_API: 'htmlApi',
    CACHE_TABLE: 'cacheTable',
};

function clearFilters() {
    document.dispatchEvent(new CustomEvent('clear-all-filters'));
}

function openChartConfigurationModal(chartId) {
    document.dispatchEvent(new CustomEvent('open-chart-configuration-modal', {
        'detail':
            {
                'chartId': chartId,
            }
        }
    ));
}

function stopStartRefreshTime() {
    document.dispatchEvent(new CustomEvent('stop-start-refresh-data'));
}

//TODO-DEV: MERGE Refact changeOutOfDemandFilter and updateMilestone to "UPDATE FILTER BTN"
function changeOutOfDemandFilter(value) {

    document.dispatchEvent(new CustomEvent('filter-change', {
        'detail':
            {
                'name': 'out_of_demand',
                'value': value,
            }
        }
    ));
    setTimeout(() => { document.dispatchEvent(new CustomEvent('force-page-refresh-data')); }, 500);
}

function updateMilestone(value) {

    document.dispatchEvent(new CustomEvent('filter-change', {
        'detail':
            {
                'name': 'milestone',
                'value': value,
            }
        }
    ));
    setTimeout(() => { document.dispatchEvent(new CustomEvent('force-page-refresh-data')); }, 500);
}

function updateRefreshTimer(value) {
     document.dispatchEvent(new CustomEvent('change-refresh-time', {
        'detail':
            {
                'value': value,
            }
        }
    ));
}

function updateDetailModalContent(value, type) {
     document.dispatchEvent(new CustomEvent('change-detail-modal-content', {
        'detail':
            {
                'type': type,
                'value': value,
            }
        }
    ));
}

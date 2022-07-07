function showHelpModal(parameters) {

    document.getElementById('help-data').innerHTML = '';
    showModalElement("#help");

    axios.get('/api/help-text', {
        params: {
            slug: parameters
        }
    }).then((response) => {
        document.getElementById('help-data').innerHTML = response.data;
    }).catch(() => {
        $.notify('Error.', {type:'danger'});
    });
}
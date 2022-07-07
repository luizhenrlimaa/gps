function autoFillAtividadeByCertificado() {
    let idCategoria = $('#id_categoria').val();

    console.log('#id_categoria')

    $.ajax({
        url: {% url 'autoFillAtividade' %},
        type: "GET",
        data: {
            pk: idCategoria,
        },
        contentType: "json",
        success: function(response) {
            if (!response || !response.pk) {
                return;
            }

        },
        error: function(error) {
            console.log(error);
        }
    });
};

            options += '<option value="' + item.pk + '">' + item.fields['descricao'] + '</option>';

            console.log(options); //This should show the new listing of filtered options.


            trHTML += '<tr><td><input type="checkbox" name="selected" value="'+item.pk+'"></td><td>' + item.fields.placa + '</td><td>' + item.fields.nome + '</td></tr>';
            });
            $('#table-vinculo').append(trHTML);


function autoFillCnpj() {
    let id_tomador = $('#id_cliente').val();

    $.ajax({
        url: url_parceiro_comercial,
        type: "GET",
        data: {
            pk: id_tomador
        },
        contentType: "application/json; charset=UTF-8",
        success: function(response) {
            $('#id_cnpj').val(response.cnpj);
        },
        error: function(error) {
            console.log(error);
        }
    });

};

function showAlocacaoCargaFinalizada(el) {
    let idEl = el.id.toString() +"_input";
    let checked = $('#'+idEl)[0].checked;
    debugger;
    if (!checked) {
        $('tr').map((item) => {
            if (item >= 2) {
                if ($(`#id_alocacaocarga-${item - 2}-status`).val() === 'Finalizada') {
                    $('tr').eq(item).removeClass('hidden')
                }
            }
        })
    } else {
        $('tr').map((item) => {
            if (item >= 2) {
                if ($(`#id_alocacaocarga-${item - 2}-status`).val() === 'Finalizada') {
                    $('tr').eq(item).addClass('hidden')
                }
            }
        })
    }
}


function busca_veiculos_prox(){
    console.log("create post is working!") // sanity check

    let num = $('#numero').val()
    let id = $('#id_demanda').val()


    $.ajax({
        type: 'GET',
        url: url_veiculos_proximos,
        data: {
            num: num,
            id: id,
        },
        dataType: 'json',
        success: function(response){

            console.log("success");
            $('#num-vei-form').val('');

            console.log("success");

            console.log(response);

            var trHTML = '';
            $.each(response, function (i, item) {
            trHTML += '<tr><td><input type="checkbox" name="selected" value="'+item.pk+'"></td><td>' + item.fields.placa + '</td><td>' + item.fields.nome + '</td></tr>';
            });
            $('#table-vinculo').append(trHTML);

        },
        error: function(xhr,errmsg,err){
            console.log(xhr,errmsg,err);
        }
    });
}
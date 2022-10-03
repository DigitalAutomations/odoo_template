odoo.define('addoons_website_theme.acquista_ore', function(require) {

    'use strict';
    require('web.dom_ready');

    var rpc = require('web.rpc');
    var base = require('web_editor.base');
    var session = require('web.session');
    var Dialog = require('web.Dialog');

    base.ready().then(function(){


        $('#input_ore_sviluppo').change(function () {
             var self = this;
            rpc.query({
            model: 'sale.order.line',
            method: 'get_portal_pricelist_price',
            args: [{
                'user_id': session.user_id,
                'qty_sviluppo': parseInt($('#input_ore_sviluppo')[0].value),
                'qty_formazione': parseInt($('#input_ore_formazione')[0].value),
            }],
            }).then(function (data) {


                $("#qty_sviluppo")[0].innerText = $('#input_ore_sviluppo')[0].value + 'h';
                $("#qty_formazione")[0].innerText = $('#input_ore_formazione')[0].value + 'h';

                $('#prezzo_sviluppo')[0].innerText = data['price_unit_sviluppo'] ;
                $('#prezzo_formazione')[0].innerText = data['price_unit_formazione'];
                $('#totale_prezzo_pachetto')[0].innerText = data['totale'] + '€';

            });
        });

        $('#input_ore_formazione').change(function () {
             var self = this;
            rpc.query({
            model: 'sale.order.line',
            method: 'get_portal_pricelist_price',
            args: [{
                'user_id': session.user_id,
                'qty_sviluppo': parseInt($('#input_ore_sviluppo')[0].value),
                'qty_formazione': parseInt($('#input_ore_formazione')[0].value),
            }],
            }).then(function (data) {


                $("#qty_sviluppo")[0].innerText = $('#input_ore_sviluppo')[0].value + 'h';
                $("#qty_formazione")[0].innerText = $('#input_ore_formazione')[0].value + 'h';

                $('#prezzo_sviluppo')[0].innerText = data['price_unit_sviluppo'] ;
                $('#prezzo_formazione')[0].innerText = data['price_unit_formazione'];
                $('#totale_prezzo_pachetto')[0].innerText = data['totale'] + '€';

            });
        });

        if (document.getElementById("qty_sviluppo")){
            $('#input_ore_sviluppo').trigger('change');
        }


        $('#btn-acquista').click(function () {
            Dialog.confirm(this, "Sei sicuro di confermare l'ordine?", {
                confirm_callback: function () {
                    var prova = document.getElementById('input_ore_sviluppo');
                    rpc.query({
                    model: 'sale.order',
                    method: 'create_from_portal',
                    args: [{
                        'user_id': session.user_id,
                        'qty_sviluppo': document.getElementById('input_ore_sviluppo').value,
                        'qty_formazione': document.getElementById('input_ore_formazione').value,
                        'prezzo_formazione':parseInt(document.getElementById('prezzo_formazione').innerText),
                        'prezzo_sviluppo':parseInt(document.getElementById('prezzo_sviluppo').innerText),
                    }],
                    }).then(function (data) {

                        if(data['success']){
                            Dialog.confirm(this, "Clicca Ok per aprire l'ordine e visualizzare i dati per eseguire il pagamento", {
                                confirm_callback: function () {
                                    window.location.replace('/my/orders/'+ data['id']);
                                },
                                title: 'Ordine Creato con Successo',
                            })
                        }else{
                            Dialog.alert(this, ("Attenzione c'è stato un problema durante la creazione dell'ordine"), {title: "Errore"});
                        }

                    });
                },
            });
        });
    });
});
odoo.define('addoons_website_theme.ore_editor', function(require) {

    'use strict';

    var options = require('web_editor.snippets.options');
    var rpc = require('web.rpc');
    var session = require('web.session');
    options.registry.ore_editor = options.Class.extend({

        start: function() {

            rpc.query({
            model: 'res.partner',
            method: 'get_ore_disponibili',
            args: [{
                'user_id': session.user_id,//china export
            }],
            }).then(function (returned_value) {
                $('.ore_sv').html(returned_value['ore_sviluppo']);
                $('.ore_fc').html(returned_value['ore_formazione']);
            });

        },

    });
});
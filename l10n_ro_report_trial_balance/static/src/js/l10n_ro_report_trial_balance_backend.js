odoo.define('l10n_ro_report_trial_balance.l10n_ro_report_trial_balance_backend', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');
var session = require('web.session');
var ReportWidget = require('l10n_ro_report_trial_balance.l10n_ro_report_trial_balance_widget');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;

var report_backend = Widget.extend(ControlPanelMixin, {
    // Stores all the parameters of the action.
     events: {
        'click .o_l10n_ro_report_trial_balance_print': 'print',
        'click .o_l10n_ro_report_trial_balance_export': 'export',
    },
    init: function(parent, action) {
        this.actionManager = parent;
        this.given_context = {};
        this.odoo_context = action.context;
        this.controller_url = action.context.url;
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        this.buttons = [
            { action: "print_pdf", name: "Print Preview"},
            { action: "print_xlsx", name: "Export (XLSX)"}
        ]
        this.given_context.active_id = action.context.active_id || action.params.active_id;
        this.given_context.model = action.context.active_model || false;
        this.given_context.ttype = action.context.ttype || false;
        return this._super.apply(this, arguments);
    },
    willStart: function() {
        return $.when(this.get_html());
    },
    set_html: function() {
        var self = this;
        var def = $.when();
        if (!this.report_widget) {
            this.report_widget = new ReportWidget(this, this.given_context);
            def = this.report_widget.appendTo(this.$el);
        }
        def.then(function () {
            self.report_widget.$el.html(self.html);
        });
    },
    start: function() {
        this.set_html();
        return this._super();
    },
    // Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        var defs = [];
        return this._rpc({
                model: this.given_context.model,
                method: 'get_html',
                args: [self.given_context],
                context: self.odoo_context,
            })
            .then(function (result) {
                self.html = result.html;
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
    },
    // Updates the control panel and render the elements that have yet to be rendered
    update_cp: function() {
         if (!this.$buttons) {
            this.renderButtons();
        }
        var status = {
            breadcrumbs: this.actionManager.get_breadcrumbs(),
            cp_content: {$buttons: this.$buttons},
        };
        return this.update_control_panel(status);
    },
    do_show: function() {
        this._super();
        this.update_cp();
    },
    print: function(e) {
        var self = this;
        this._rpc({
            model: this.given_context.model,
            method: 'print_report',
            args: [this.given_context.active_id, 'qweb-pdf'],
            context: self.odoo_context,
        }).then(function(result){
            self.do_action(result);
        });
    },
    export: function(e) {
        var self = this;
        this._rpc({
            model: this.given_context.model,
            method: 'print_report',
            args: [this.given_context.active_id, 'xlsx'],
            context: self.odoo_context,
        })
        .then(function(result){
            self.do_action(result);
        });
    },
    canBeRemoved: function () {
        return $.when();
    },

    renderButtons: function() {
        var self = this;
        this.$buttons = $(QWeb.render("trial_balance.buttons", {buttons: this.buttons}));
        // bind actions
        _.each(this.$buttons.siblings('button'), function(el) {
            $(el).click(function() {
                return self._rpc({
                        model: self.given_context.model,
                        method: $(el).attr('action'),
                        args: [self.given_context.active_id],
                        context: self.odoo_context,
                    })
                    .then(function(result){
                        return self.do_action(result);
                    });
            });
        });
        return this.$buttons;
    },
});

core.action_registry.add("l10n_ro_report_trial_balance_backend", report_backend);
return report_backend;
});

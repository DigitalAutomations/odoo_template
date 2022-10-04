<odoo>
    <record id="aliquid_res_partner_form_view" model="ir.ui.view">
        <field name="name">aliquid.res.partner.form</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="type">form</field>
        <field name="arch" type="xml">
            <field name="company_type" position="after">
                <div attrs="{'invisible': [('is_company','=', False)]}" class="oe_edit_only">
                    <field name="is_holding"/><label for="is_holding" string="È una holding"/><br/>
                </div>
            </field>
            <notebook position="inside">
                <page name="aziende_collegate" string="Aziende Collegate" attrs="{'invisible': [('is_holding','=', False)]}">
                    <field name="holding_child_ids" widget="many2many"/>
                </page>
            </notebook>
            <field name="vat" position="after">
                <field name="holding_company_id" string="Azienda Holding Padre"/>
            </field>
            <field name="phone" position="after">
                <field name="fax" string="Fax"/>
            </field>
        </field>
    </record>

    <!--<record id="aliquid_res_partner_form_view" model="ir.ui.view">
        <field name="name">addoons.res.partner.form</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="l10n_it_fatturapa.view_partner_form_fatturapa"/>
        <field name="type">form</field>
        <field name="arch" type="xml">
            <page name="fatturapa" position="replace">
                <page name="fatturapa" string="Fattura Elettronica" groups="account.group_account_invoice" attrs="{'invisible': [('electronic_invoice_subjected','=', False)]}">
                    <group name="fatturapa_group">
                        <group attrs="{'invisible': [('electronic_invoice_subjected', '=', False)]}">
                            <field name="ipa_code" string="Codice IPA" placeholder="IPA123"/>
                            <field name="codice_destinatario" string="Codice Destinatario" attrs="{'invisible': [('is_pa', '=', True)]}"/>
                            <field name="pec_destinatario" string="PEC Destinatario" attrs="{'invisible': ['|',('is_pa', '=', True), ('codice_destinatario', '!=', '0000000')]}"/>
                            <field name="eori_code" string="Codice EORI"/>
                        </group>
                    </group>
                    <group name="pa_fields">
                        <field name="avoid_pa_checks" string="Disabilita Controlli P.A"/>
                        <field name="procurement_type" string="Tipo" attrs="{'required':[('avoid_pa_checks', '=', False)]}"/>
                        <field name="procurement_name" string="Nome" attrs="{'required':[('avoid_pa_checks', '=', False)]}"/>
                        <field name="procurement_date" string="Data"/>
                        <field name="procurement_code" string="Codice"/>
                        <field name="procurement_cig" string="CIG"/>
                        <field name="procurement_cup" string="CUP"/>
                    </group>
                </page>
            </page>

            <field name="company_type" position="after">
                <div attrs="{'invisible': [('is_company','=', False)]}" class="oe_edit_only">
                    <field name="is_holding"/><label for="is_holding" string="È una holding"/><br/>
                </div>
            </field>
            <notebook position="inside">
                <page name="aziende_collegate" string="Aziende Collegate" attrs="{'invisible': [('is_holding','=', False)]}">
                    <field name="holding_child_ids" widget="many2many"/>
                </page>
            </notebook>
            <field name="vat" position="after">
                <field name="holding_company_id" string="Azienda Holding Padre"/>
            </field>
            <xpath expr="//div[@name='button_box']" position="inside">

                <button name="addoons_action_view_ore_dev" type="object" class="oe_stat_button" icon="fa-indent"  >
                    <field name="ore_sviluppo_disponibili" string="Ore disponibili" widget="statinfo"/>
                </button>

                <button name="addoons_action_view_ore_training" type="object" class="oe_stat_button" icon="fa-university" >
                    <field name="ore_formazione_consulenza_disponibili" string="Ore formazione" widget="statinfo"/>
                </button>

                <button name="addoons_action_view_ore_internal" type="object" class="oe_stat_button" icon="fa-clock-o" >
                    <field name="ore_interne_accumulate" string="Ore interne" widget="statinfo"/>
                </button>

            </xpath>
            <xpath expr="//field[@name='vat']" position="after">
                <field name="soglia_ore_sviluppo" string="Soglia Notifica Ore Sviluppo" />
                <field name="soglia_ore_formazione" string="Soglia Notifica ore Formazione" />
            </xpath>

            <xpath expr="//notebook/page[1]" position="after">
                <page string="Ore Interne">
                    <field name="ore_interne_ids" readonly="1" ></field>
                </page>
            </xpath>
        </field>
    </record>

    <record model="ir.ui.view" id="aliquid_partner_kanban_view">
        <field name="name">aliquid.res.partner.kanban.inherit</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.res_partner_kanban_view"/>
        <field name="arch" type="xml">
            <field name="mobile" position="after">
                <field name="ref"/>
            </field>
            <xpath expr="//strong[hasclass('oe_partner_heading')]" position="after">
                <div t-if="record.ref.value">Rif. Interno: <field name="ref"/></div>
            </xpath>
        </field>
    </record>

    <record model="ir.ui.view" id="aliquid_partner_view_ticket_button_view">
        <field name="name">aliquid_partner_view_ticket_button_view</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="helpdesk.view_partner_form_inherit_helpdesk"/>
        <field name="arch" type="xml">
            <button name="action_open_helpdesk_ticket" position="replace">
                <button class="oe_stat_button" type="object"
                        name="action_open_helpdesk_ticket" context="{'default_partner_id': active_id}" icon="fa-life-ring">
                    <div class="o_stat_info">
                        <field name="ticket_count" class="o_stat_value"/>
                        <span class="o_stat_text"> Tickets</span>
                    </div>
                </button>
            </button>
        </field>
    </record>
-->
</odoo>

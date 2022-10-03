from odoo import models, api, fields


class WebsitePageInherit(models.Model):
    _inherit = 'website.menu'

    @api.one
    def _compute_visible(self):
        """Non mostra i menù del sito agli utenti portale."""
        super()._compute_visible()
        if not self.env.user.has_group('base.group_portal'):
            self.is_visible = False
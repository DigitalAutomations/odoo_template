from odoo import models, api, fields, exceptions
from odoo.addons.base.models.ir_mail_server import MailDeliveryException, _logger
from odoo.tools import pycompat


class HelpdeskTicketInh(models.Model):
    _inherit = 'helpdesk.ticket'

    tot_worked_hours = fields.Float(help="Totale ore lavorate",compute="compute_tot_worked_hours",store=True)
    attachment_ids = fields.Many2many('ir.attachment')
    partner_child_id = fields.Many2one('res.partner', domain="[('parent_id', '=', partner_id)]")

    @api.onchange('partner_child_id')
    def onchange_contact_id(self):
        if self.partner_child_id:
            self.partner_email = self.partner_child_id.email

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            if not self.partner_email:
                self.partner_email = self.partner_id.email
            if self.partner_id.parent_id:
                self.partner_child_id = self.partner_id.id
                self.partner_id = self.partner_id.parent_id.id
            if self.partner_child_id and self.partner_id.id != self.partner_child_id.parent_id.id:
                self.partner_child_id = False
                self.partner_email = False

    @api.depends('timesheet_ids')
    def compute_tot_worked_hours(self):
        for record in self:
            sum = 0.0
            for line in record.timesheet_ids:
                sum += line.unit_amount
            record.tot_worked_hours = sum

    def _message_post_after_hook(self, message,*args, **kwargs):
        """
        Tolta assegnazione automatica partner_id.email = partner_email
        """
        if self.partner_email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.partner_email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('partner_email', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        attachment_list = []
        for attachment in self.attachment_ids:
            attachment.res_id = self.id
            attachment_list.append((4, attachment.id))

        args[0]['attachment_ids'] = attachment_list
        return super(models.Model, self)._message_post_after_hook(message, *args, **kwargs)



class MailMailInherit(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """
        for server_id, batch_ids in self._split_by_server():
            # allegati
            for record in self:
                if record.model == 'helpdesk.ticket':
                    if not record.attachment_ids:
                        ticket = self.env[record.model].browse(record.res_id)
                        record.attachment_ids = ticket.attachment_ids
            smtp_session = None
            try:
                smtp_session = self.env['ir.mail_server'].connect(mail_server_id=server_id)
            except Exception as exc:
                if raise_exception:
                    # To be consistent and backward compatible with mail_mail.send() raised
                    # exceptions, it is encapsulated into an Odoo MailDeliveryException
                    raise MailDeliveryException('Unable to connect to SMTP Server', exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({'state': 'exception', 'failure_reason': exc})
                    batch._postprocess_sent_message(success_pids=[], failure_type="SMTP")
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session)
                _logger.info(
                    'Sent batch %s emails via mail server ID #%s',
                    len(batch_ids), server_id)
            finally:
                if smtp_session:
                    smtp_session.quit()
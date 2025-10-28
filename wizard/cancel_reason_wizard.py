from odoo import models, fields, api

class CancelReasonWizard(models.TransientModel):
    _name = 'cancel.reason.wizard'
    _description = 'Motif d’annulation de session'

    reason = fields.Text(string="Motif d’annulation", required=True)

    def confirm_cancel(self):
        """Annule la session et enregistre le motif."""
        active_ids = self.env.context.get('active_ids')
        sessions = self.env['academy.session'].browse(active_ids)

        for session in sessions:
            session.cancel_reason = self.reason
            session.state = 'cancel'
            # message dans le chatter
            session.message_post(body=f"Session annulée. Motif : {self.reason}")

        return {'type': 'ir.actions.act_window_close'}

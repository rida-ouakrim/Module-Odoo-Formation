import io
import base64
import csv
from odoo import models, fields, api
from datetime import datetime
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class Session(models.Model):
    _name = 'academy.session'
    _description = 'Session de formation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom de la session', required=True)
    duration = fields.Float(string='Durée (heures)')
    date_debut = fields.Date(string="Date début")
    date_fin = fields.Date(string="Date fin")
    trainer_id = fields.Many2one('res.partner', string='Formateur')
    attendee_ids = fields.Many2many('res.partner', string='Participants')
    cancel_reason = fields.Text(string="Motif d’annulation")

    # 🟢 Champ de workflow
    state = fields.Selection([
        ('draft', 'Préparation'),
        ('open', 'Ouvert'),
        ('done', 'Clôturé'),
        ('cancel', 'Annulé'),
    ], string="État", default='draft', tracking=True)

    # 🟡 Actions du workflow
    def action_open(self):
        """Passer la session à l'état 'Ouvert'"""
        for rec in self:
            rec.state = 'open'

    def action_done(self):
        """Passer la session à l'état 'Clôturé'"""
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        """Annuler la session"""
        for rec in self:
            rec.state = 'cancel'

    def action_open_cancel_wizard(self):
        """Ouvre la popup (wizard) pour saisir le motif d’annulation."""
        return {
            'name': 'Motif d’annulation',
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids},
        }
        # 🟢 Champ technique pour compatibilité
    dummy = fields.Binary(string="Fichier exporté")

    # ==================================================
    # EXPORT CSV
    # ==================================================
    def action_export_csv(self):
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # 🟢 En-têtes
        writer.writerow(['Nom', 'Date début', 'Date fin', 'Durée', 'Formateur', 'État'])

        # 🟢 Données — on parcourt self (les sessions sélectionnées)
        for session in self:
            writer.writerow([
                session.name or '',
                session.date_debut or '',
                session.date_fin or '',
                session.duration or '',
                session.trainer_id.name or '',
                session.state or '',
            ])

        # 🟢 Générer fichier
        file_data = output.getvalue().encode('utf-8')
        output.close()

        filename = f"Sessions_{datetime.today().strftime('%Y%m%d_%H%M%S')}.csv"

        # ⚠️ Ici on attache le fichier à un seul enregistrement pour éviter l’erreur singleton
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'mimetype': 'text/csv',
            'res_model': 'academy.session',
            'res_id': self[0].id,  # 🟢 premier enregistrement uniquement
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
    }
    # ==================================================
    # EXPORT XLS
    # ==================================================
    def action_export_xls(self):
        if not xlsxwriter:
            raise UserError("Le module xlsxwriter n'est pas installé sur le serveur.")

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet('Sessions')

        headers = ['Nom', 'Date début', 'Date fin', 'Durée', 'Formateur', 'État']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#d3d3d3'})

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        row = 1
        for session in self:
            sheet.write(row, 0, session.name or '')
            sheet.write(row, 1, str(session.date_debut or ''))
            sheet.write(row, 2, str(session.date_fin or ''))
            sheet.write(row, 3, session.duration or 0)
            sheet.write(row, 4, session.trainer_id.name or '')
            sheet.write(row, 5, session.state or '')
            row += 1

        workbook.close()
        file_data = output.getvalue()
        output.close()

        filename = f"Sessions_{datetime.today().strftime('%Y%m%d_%H%M%S')}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'academy.session',
            'res_id': self[0].id,  # 🟢 premier enregistrement
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
from odoo import models, fields, api
from odoo.exceptions import UserError


class CreatePartnerWizard(models.TransientModel):
    _name = 'create.partner.wizard'
    _description = 'Create Partner Wizard'

    name = fields.Char(
        string="Имя",
        required=True,
    )
    is_company = fields.Boolean(
        string="Это компания?",
        default=False,
    )

    def action_create(self):
        """
        Creates new partner and redirect to partner card
        """
        partner = self.env['res.partner'].create({
            'name': self.name,
            'is_company': self.is_company,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }

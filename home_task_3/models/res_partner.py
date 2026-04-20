from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """
    Extends the res.partner model to implement a "Primary Contact" logic
    for companies. Ensures that each company has exactly one primary contact.
    """
    _inherit = "res.partner"

    is_primary = fields.Boolean(
        string="Primary Contact",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create multiple partner records and automatically assign "is_primary"
        to the first contact of a company.
        """
        parent_ids = [v.get("parent_id") for v in vals_list if v.get("parent_id")]
        existing_parents_with_contacts = set()
        if parent_ids:
            contacts_data = self.env["res.partner"].read_group(
                [("parent_id", "in", parent_ids), ("type", "=", "contact")],
                ["parent_id"],
                ["parent_id"]
            )
            existing_parents_with_contacts = {d["parent_id"][0] for d in contacts_data}

        parents_assigned_in_batch = set()
        for vals in vals_list:
            parent_id = vals.get("parent_id")
            if parent_id and parent_id not in existing_parents_with_contacts and parent_id not in parents_assigned_in_batch:
                vals["is_primary"] = True
                parents_assigned_in_batch.add(parent_id)

        return super().create(vals_list)

    def write(self, vals):
        """
        Update partner records. Prevents unchecking the primary flag if no
        other primary contact exists, and handles the exclusive selection logic.
        """
        if "is_primary" in vals and not vals.get("is_primary"):
            for contact in self:
                if contact.is_primary:
                    others = (contact.parent_id.child_ids - contact).filtered(lambda c: c.is_primary)
                    if not others:
                        raise UserError(_("Company cannot have no primary contact."))

        contacts = super().write(vals)
        if vals.get("is_primary"):
            for contact in self:
                contact._ensure_single_primary()
        return contacts

    def _ensure_single_primary(self):
        """
        Maintains the "single primary" constraint by resetting the "is_primary" flag
        on all sibling contacts of the current record.
        """
        self.ensure_one()
        if self.parent_id:
            others = self.parent_id.child_ids.filtered(lambda c: c.id != self.id)
            others.with_context(skip_primary_check=True).write({"is_primary": False})

    def unlink(self):
        """
        Handle partner deletion. Prevents deleting the last contact of a company
        and automatically transfers the primary status to a successor if the
        primary contact is removed.
        """
        for contact in self:
            if contact.parent_id:
                children = contact.parent_id.child_ids
                if len(children) <= 1:
                    raise UserError(_("Cannot delete the last contact."))

                if contact.is_primary:
                    successor = (children - contact)[0]
                    successor.with_context(skip_primary_check=True).write({"is_primary": True})

        return super().unlink()

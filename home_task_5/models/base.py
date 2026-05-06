from odoo import api, models


_DISPLAY_ATTRIBUTES = frozenset({
    "string", "help", "placeholder", "title", "confirm",
    "sum", "avg", "text", "label",
})


def _replace_customer(value):
    return value.replace("Customer", "Partner").replace("customer", "partner")


class Base(models.AbstractModel):
    """
    Inherit base model to replace 'Customer' with 'Partner'
    across all field labels and views without .po files.
    """
    _inherit = "base"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        for field_data in res.values():
            if "string" in field_data:
                field_data["string"] = _replace_customer(field_data["string"])
        return res

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        for element in arch.iter():
            if element.text and "Customer" in element.text:
                element.text = _replace_customer(element.text)
            if element.tail and "Customer" in element.tail:
                element.tail = _replace_customer(element.tail)
            for attr_name in _DISPLAY_ATTRIBUTES:
                attr_value = element.get(attr_name)
                if attr_value and "Customer" in attr_value:
                    element.set(attr_name, _replace_customer(attr_value))
        return arch, view

from odoo import api, fields, models


class HomeTask1(models.Model):
    """
    HomeTask1 educational model for internship
    """
    _name = 'home.task.1'
    _description = 'Home Task 1 model'

    text = fields.Char(
        string='Текстовое поле',
    )

    check1 = fields.Boolean(
        string='Test 1',
        default=False,
    )
    check2 = fields.Boolean(
        string='Test 2',
        default=False,
    )
    check_all = fields.Boolean(
        string='Select all',
        default=False,
        compute='_compute_check_all',
        inverse='_inverse_check_all',
        store=True,
        readonly=False,
    )

    select1 = fields.Selection(
        [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
        ],
        string='Селектор 1',
    )

    select2 = fields.Selection(
        [
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
        ],
        string='Селектор 2',
    )

    boolean1 = fields.Boolean(
        string='1',
        default=False,
    )
    boolean2 = fields.Boolean(
        string='2',
        default=False,
    )
    boolean3 = fields.Boolean(
        string='3',
        default=False,
    )
    boolean4 = fields.Boolean(
        string='4',
        default=False,
    )
    boolean5 = fields.Boolean(
        string='5',
        default=False,
    )
    boolean6 = fields.Boolean(
        string='6',
        default=False,
    )
    boolean7 = fields.Boolean(
        string='7',
        default=False,
    )
    boolean8 = fields.Boolean(
        string='8',
        default=False,
    )
    boolean9 = fields.Boolean(
        string='9',
        default=False,
    )

    text_field = fields.Text(
        string='Текстовое поле(тип Text)',
    )
    html_field = fields.Html(
        string='HTML поле',
    )

    integer_field = fields.Integer(
        string='Целочисленное поле',
    )
    float_field = fields.Float(
        string='Число с плавающей точкой',
    )
    monetary_field = fields.Monetary(
        string='Денежное поле',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Валюта',
        default=lambda self: self.env.company.currency_id,
    )

    date_field = fields.Date(
        string='Дата',
    )
    datetime_field = fields.Datetime(
        string='Дата и время',
    )

    binary_field = fields.Binary(
        string='Загрузка файла/фото',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Many to one поле',
    )

    is_company = fields.Boolean(
        string='Это компания?',
        default=False,
    )

    @api.depends('check1', 'check2')
    def _compute_check_all(self):
        """
        Sets check_all to True only if both checkboxes are checked.
        Triggered automatically when check1 or check2 changes.
        """
        for record in self:
            record.check_all = record.check1 and record.check2

    def _inverse_check_all(self):
        """
        Distributes the value from Select All across child fields.
        Triggered when saving a record if check_all was manually changed.
        """
        for record in self:
            record.check1 = record.check2 = record.check_all

    @api.onchange('check_all')
    def _onchange_check_all(self):
        """
        Ensures instant UI response when clicking Select All.
        Toggles the state of check1 and check2.
        """
        if self.check_all:
            self.check1 = self.check2 = True
        elif self.check1 and self.check2:
            self.check1 = self.check2 = False

    @api.onchange('check1')
    def _onchange_check1(self):
        """
        Inserts in text field check1 label value when True.
        Removes check1 label value when False.
        """
        current_text = self.text or ""
        check1_label = self._fields['check1'].string
        if self.check1:
            self.text = current_text + f"[{check1_label}]"
        else:
            self.text = current_text.replace(f"[{check1_label}]", "")

    @api.onchange('check2')
    def _onchange_check2(self):
        """
        Inserts in text field check1 label value when True.
        Removes check2 label value when False.
        """
        current_text = self.text or ""
        check2_label = self._fields['check2'].string
        if self.check2:
            self.text = current_text + f"{{{check2_label}}}"
        else:
            self.text = current_text.replace(f"{{{check2_label}}}", "")

    def action_create_partner(self):
        """
        Open a modal form view to create a new res.partner.
        Passes the 'text' field value as the default name and the 'is_company'
        boolean to determine the partner type (Individual or Company)
        via the context.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Добавить партнера',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.text,
                'default_is_company': self.is_company,
            }
        }

    def action_open_wizard(self):
        """
        Opens a wizard to create partner card
        """
        return {
            'name': 'Модальное окно создания партнера',
            'type': 'ir.actions.act_window',
            'res_model': 'create.partner.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

from odoo import models, fields, api
from odoo.tools.translate import _


class Cabang(models.Model):
    _name = 'cabang.cabang'
    _description = 'VIO Clinic Branch'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Nama Cabang',
        required=True,
        translate=True,
        help='Nama cabang klinik VIO'
    )
    address = fields.Text(
        string='Alamat',
        translate=True,
        help='Alamat lengkap cabang klinik'
    )
    phone = fields.Char(
        string='Nomor Telepon',
        translate=True,
        help='Nomor telepon kontak untuk cabang'
    )
    map_link = fields.Char(
        string='Tautan Peta',
        translate=True,
        help='Tautan Google Maps untuk lokasi cabang'
    )
    active = fields.Boolean(
        string='Aktif',
        default=True,
        help='Mengaktifkan atau menonaktifkan cabang'
    )

    @api.model
    def create(self, vals_list):
        """
        Create a new branch record.

        This method extends the default create behavior to add
        custom logic if needed in the future.

        :param vals_list: Dictionary of field values
        :return: New branch record
        """
        return super(Cabang, self).create(vals_list)

    def write(self, vals):
        """
        Update branch record.

        This method extends the default write behavior to add
        custom logic if needed in the future.

        :param vals: Dictionary of field values to update
        :return: Write operation result
        """
        return super(Cabang, self).write(vals)

    def action_toggle_active(self):
        """
        Toggle the active status of selected branches.

        This method allows users to quickly activate or deactivate
        branches from the tree or form view.

        :return: None
        """
        for record in self:
            record.active = not record.active

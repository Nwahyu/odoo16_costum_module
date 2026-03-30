from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose DB blocking toggle and header value in Odoo Settings."""

    _inherit = "res.config.settings"

    enable_db_block = fields.Boolean(
        string="Enable DB blocking",
        config_parameter="enable_db_block",
        default=True,
    )
    backup_header_value = fields.Char(
        string="Authorized backup header value",
        config_parameter="backup_header_value",
        default="04julidarsana",
    )

    def set_values(self):
        """Save configuration values to system parameters."""
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "enable_db_block", self.enable_db_block
        )
        # print("aaaaaaaaaaaaaaaaaaaaaaaaaa")
        # print(self.env['ir.config_parameter'].sudo().get_param("enable_db_block"))

    def get_values(self):
        """Retrieve configuration values from system parameters."""
        res = super().get_values()
        res["enable_db_block"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("enable_db_block")
        )
        return res

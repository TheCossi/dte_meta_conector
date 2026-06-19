# -- coding: utf-8 --
from odoo import models, fields, api
import requests

class MetaChannel(models.Model):
    _name = 'meta.channel'
    _description = 'Configuración de Canales Meta'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nombre del Canal', required=True, tracking=True)
    channel_type = fields.Selection([
        ('whatsapp', 'WhatsApp Business'),
        ('facebook', 'Facebook Messenger'),
        ('instagram', 'Instagram Direct')
    ], string='Tipo de Canal', required=True, default='whatsapp', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('maintenance', 'En Mantenimiento')
    ], string='Estado', default='draft', tracking=True)

    middleware_url = fields.Char(string='URL del Middleware', required=True)
    bearer_token = fields.Char(string='Bearer Token Backend', required=True)
    page_id = fields.Char(string='Page ID / WABA ID', required=True)
    meta_access_token = fields.Char(string='Meta Access Token', required=True)

    def action_test_connection(self):
        self.ensure_one()
        url = f"{self.middleware_url}/v1/health"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                self.state = 'active'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Conexión Exitosa',
                        'message': 'El conector se comunicó con el Middleware de forma óptima.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except Exception as e:
            self.state = 'maintenance'
            self.env['meta.log.error'].create({
                'name': 'Fallo de diagnóstico',
                'error_message': str(e),
                'channel_id': self.id
            })
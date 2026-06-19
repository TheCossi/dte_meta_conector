# -- coding: utf-8 --
from odoo import models, fields

class MetaLogError(models.Model):
    _name = 'meta.log.error'
    _description = 'Bitácora de Errores e Incidencias Meta'
    _order = 'create_date desc'

    name = fields.Char(string='Incidencia / Endpoint', required=True)
    create_date = fields.Datetime(string='Fecha y Hora', readonly=True)
    error_message = fields.Text(string='Mensaje Descriptivo del Error', readonly=True)
    channel_id = fields.Many2one('meta.channel', string='Canal de Origen', readonly=True)
    lead_id = fields.Many2one('crm.lead', string='Lead Afectado', readonly=True)
# -- coding: utf-8 --
from odoo import http
from odoo.http import request
import json

class MetaWebhookController(http.Controller):

    @http.route('/v1/meta/webhook/receive', type='json', auth='public', methods=['POST'], csrf=False)
    def procesar_interaccion_meta(self, **kwargs):
        req_headers = request.httprequest.headers
        auth_header = req_headers.get('Authorization', '')
        
        # Busca el token configurado en Odoo para validar el acceso seguro
        channel_env = request.env['meta.channel'].sudo()
        canal = channel_env.search([('state', '=', 'active')], limit=1)
        
        expected_token = f"Bearer {canal.bearer_token}" if canal else "Bearer conector_seguro"
        if auth_header != expected_token:
            return {'status': 'error', 'message': 'Unauthorized'}

        payload = json.loads(request.httprequest.data)
        email = payload.get('email')
        phone = payload.get('phone')
        first_name = payload.get('first_name')
        last_name = payload.get('last_name', '')
        message_content = payload.get('message', '')

        lead_env = request.env['crm.lead'].sudo()
        
        # Lógica inteligente para evitar duplicados por teléfono o por correo
        domain = ['|', ('email_from', '=', email), ('phone', '=', phone)] if email else [('phone', '=', phone)]
        lead_existente = lead_env.search(domain, limit=1)

        if lead_existente:
            # SI YA EXISTE: No crea otro lead, añade el mensaje directamente al Chatter (historial)
            lead_existente.message_post(
                body=f"<b>[Mensaje Entrante - {payload.get('channel').upper()}]:</b> {message_content}",
                subtype_xmlid="mail.mt_comment"
            )
            lead_existente.meta_conversation_state = 'nuevo'
            return {'status': 'updated', 'lead_id': lead_existente.id}
        else:
            # SI NO EXISTE: Crea un registro nuevo e impecable en el CRM
            nuevo_lead = lead_env.create({
                'name': f"{first_name} {last_name} - Prospecto Meta",
                'contact_name': f"{first_name} {last_name}",
                'phone': phone,
                'email_from': email,
                'description': message_content,
                'meta_campaign_name': payload.get('campaign'),
                'meta_conversation_state': 'nuevo',
                'user_id': False # Queda libre sin vendedor asignado para que cualquiera lo atienda
            })
            return {'status': 'created', 'lead_id': nuevo_lead.id}
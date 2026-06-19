# -- coding: utf-8 --
{
    'name': 'DTE Meta CRM Connector',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Integración Omnicanal de Meta con CRM Chatter sin duplicados',
    'author': 'DTE Bolivia',
    'website': 'https://www.dte.bo',
    'depends': [
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/meta_channel_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': True,
}
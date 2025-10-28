{
    'name': 'Academy',
    'version': '1.0',
    'summary': 'Module de gestion de sessions de formation',
    'author': 'Rida OUAKRIM',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/session_views.xml',
        'views/cancel_reason_wizard_view.xml',
        'views/session_export_actions.xml',
        'report/report.xml',
        'report/report_session_template.xml',
    ],
    'application': True,
}

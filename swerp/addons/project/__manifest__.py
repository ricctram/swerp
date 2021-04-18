# -*- coding: utf-8 -*-
# Part of Swerp. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project',
    'version': '1.1',
    'website': 'https://www.swerp.it/page/project-management',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Organize and schedule your projects ',
    'depends': [
        'base_setup',
        'mail',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
    ],
    'description': "",
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'report/project_report_views.xml',
        'views/digest_views.xml',
        'views/rating_views.xml',
        'views/project_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_activity_views.xml',
        'views/project_assets.xml',
        'views/project_portal_templates.xml',
        'views/project_rating_templates.xml',
        'data/digest_data.xml',
        'data/project_mail_template_data.xml',
        'data/project_data.xml',
    ],
    'qweb': ['static/src/xml/project.xml'],
    'demo': ['data/project_demo.xml'],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

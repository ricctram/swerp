# -*- coding: utf-8 -*-
# Part of Swerp. See LICENSE file for full copyright and licensing details.
{
    'name': 'Initial Setup Tools',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module helps to configure the system at the installation of a new database.
================================================================================

Shows you a list of applications features to install from.

    """,
    'depends': ['base', 'web'],
    'data': [
        'data/base_setup_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

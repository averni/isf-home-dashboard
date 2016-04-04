# -*- encoding: utf-8 -*-

{
    'name': 'ISF Home Dashboard',
    'version': '0.9',
    'depends': ['base', 'web'],
    'author': 'Antonio Verni(antonio.verni@informaticisenzafrontiere.org)',
    'description': """
ISF HGH Dashboard
================================================

Add a customizable Home Tab
    """,
    'license': 'AGPL-3',
    'category': 'Tools',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'isf_home_dashboard_view.xml',
        'data/isf.home.dashboard.action.group.csv'
    ],
    'demo': [
        'demo/isf_home_dashboard_demo.xml'
    ],
    'qweb' : [
        "static/src/xml/isf_home_dashboard_templates.xml",
    ],
    'css' : [
    	"static/src/css/*.css",
    ],
    'js' : [
    	"static/src/js/*.js",
    ],
    'installable': True,
    'auto_install': False,
}

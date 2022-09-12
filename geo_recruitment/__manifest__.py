

{
    'name': 'Geo Recruit|Staffing Agency Solution|Recruitment Agency Solution',
    'version': '14.0.1.1.1',
    'summary': """Geo Recruite""",
    'description': """Recruitment,recruitment,job position,hiiring,odoo recruitment,recruitment agency,client,
    candidate,recruitment apps,hr recruitment,hr applicant,odoo hr recruitemnt,RECRUITMENT,HR RECRUITMENT,HR APPLICANT,
    CANDIDATE RECRUITMENT,candidate recruitment,jobposition,hiiring,odoorecruitment,recruitmentagency,client,
    candidate,recruitmentapps,hrrecruitment,hrapplicant,odoohrrecruitemnt,RECRUITMENT,HR RECRUITMENT,HR APPLICANT,
    CANDIDATERECRUITMENT,candidaterecruitment,job,interview,jobskills,gts recruitment,gtsrecruitment,GTSRECRUITMENT""",
    'author': 'Geotechnosoft',
    'depends': ['base', 'hr','hr_recruitment','mail'],
    'assets': {
              "web.assets_backend": [
                    "odoo_web_login/static/src/css/web_login_style.css"
                    "web/static/src/core/network/rpc_service.js"
                    # "hr_applicant/static/src/js/min.js"
                ]
    },

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/recruitment_report_view.xml',
        'views/hr_applicant_view.xml',
        'views/hr_recruitment.xml',
        'views/hr_stage_view.xml',
        'views/job_position_stage_view.xml',
        'views/hr_token_key_view.xml',
        'views/res_partner_view.xml',
        'wizard/pdf_attachment_view.xml',
        'wizard/candidate_resume_attachment_view.xml',
        'wizard/candidate_profile_view.xml',
        'wizard/applicant_wizard_view.xml',
        # 'wizard/applicant_multiple_wizard_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'author': 'Geotechnosoft',
    'maintainer': 'Geotechnosoft',
    'website': 'http://www.geotechnosoft.com/',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    "price": 149,
    "currency": 'USD'
}

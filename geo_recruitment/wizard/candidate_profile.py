from odoo import fields, models, api, _
from pyresparser import ResumeParser as resume
from pyresparser import utils
from odoo.tools import config
import base64
import spacy
import os
from spacy.matcher import Matcher
import requests
import json


class ApplicantId(models.TransientModel):
    _name = 'applicant.id'

    Linkedin_profile_id = fields.Char('LinkedIn Profile ID')


    # def action_confirm(self):
    #     print("Button is working----------------------------->",self)
    #     for profile in self.Linkedin_profile_id:
    #         __details = {
    #             'name': None,
    #             'email': None,
    #             'mobile_number': None,
    #             'skills': None,
    #             'degree': None,
    #             'designation': None,
    #             'experience': None,
    #             'total_experience': None,
    #         }
    #         nlp = spacy.load('en_core_web_sm')
    #         custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)))
    #         path = profile._full_path(profile.store_fname)
    #         if self.doc_type == 'pdf':
    #             __raw_text = utils.extract_text(path, '.pdf')
    #         if self.doc_type == 'doc':
    #             __raw_text = utils.extract_text(path, '.docx')
    #         __text = ' '.join(__raw_text.split())
    #         __nlp = nlp(__text)
    #         __custom_nlp = custom_nlp(__raw_text)
    #         __noun_chunks = list(__nlp.noun_chunks)
    #         __matcher = Matcher(nlp.vocab)
    #
    #         name = utils.extract_name(__nlp, matcher=__matcher)
    #         email = utils.extract_email(__text)
    #         mobile = utils.extract_mobile_number(__text, None)
    #         skills = utils.extract_skills(
    #             __nlp,
    #             __noun_chunks,
    #             None
    #         )
    #         entities = utils.extract_entity_sections_grad(__raw_text)
    #
    #         # extract name
    #         __details['name'] = name
    #         # extract email
    #         __details['email'] = email
    #         # extract mobile number
    #         __details['mobile_number'] = mobile
    #         # extract skills
    #         __details['skills'] = skills
    #
    #         try:
    #             __details['experience'] = entities['experience']
    #             try:
    #                 exp = round(
    #                     utils.get_total_experience(entities['experience']) / 12,
    #                     2
    #                 )
    #                 __details['total_experience'] = exp
    #             except KeyError:
    #                 __details['total_experience'] = 0
    #         except KeyError:
    #             __details['total_experience'] = 0
    #
    #         print(__details)
    #         skill_ids = []
    #         skill_obj = self.env['hr.applicant.skill']
    #         for skill in __details['skills']:
    #             temp = skill_obj.search([('name', '=ilike', skill)])
    #             if temp:
    #                 skill_ids.append(temp.id)
    #             if not temp:
    #                 temp_create = self.env['hr.applicant.skill'].create({
    #                     'name': skill,
    #                     'color': index
    #                 })
    #                 skill_ids.append(temp_create.id)
    #
    #         res = {
    #             'name': __details['name'],
    #             'partner_name': __details['name'],
    #             'email_from': __details['email'],
    #             'partner_mobile': __details['mobile_number'],
    #             'skill_ids': skill_ids,
    #             'job_id': self.env.context.get('active_id'),
    #             'company_id': self.env.company.id,
    #         }
    #         applicant = self.env['hr.applicant'].create(res)
    #         print('creating res----------->', res )
    #         print('creating res----------->', self )
    #
    #         applicant.res_model = 'hr.applicant'
    #         applicant.res_id = applicant.id
    #         for job in self.job_ids:
    #             stage_id = job._get_first_stage().id
    #             val = {
    #                 'job_id': job.id,
    #                 'applicant_id': applicant.id,
    #                 'stage_id': stage_id
    #             }
    #             self.env['job.applicant'].create(val)
    #         print(applicant)

    # ------------------------------------------------------------------------------

    def action_confirm(self):
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        api_key = '205eff9f-b617-4ac5-acc9-8cbcc484faa4'
        header_dic = {'Authorization': 'Bearer ' + api_key}
        url = 'https://www.linkedin.com/in/{profile_id}/'.format(profile_id=self.Linkedin_profile_id)
        params = {
            # 'url': 'https://www.linkedin.com/in/johnrmarty/',
            'url': url,
            'fallback_to_cache': 'on-error',
            'use_cache': 'if-present',
            'skills': 'include',
            'inferred_salary': 'include',
            'personal_email': 'include',
            'personal_contact_number': 'include',
            'twitter_profile_id': 'include',
            'facebook_profile_id': 'include',
            'github_profile_id': 'include',
            'extra': 'include',
        }
        response = requests.get(api_endpoint,
                                params=params,
                                headers=header_dic)
        # res = response.get(params)
        # print("the value of response ----------->", response)
        data = json.loads(response.content.decode('utf-8'))
        print("the value of response ----------->",data)

        json_object = json.dumps(data, indent=4)
        res = json.loads(json_object)
        # res = {'public_identifier': 'johnrmarty',
        #        'profile_pic_url': 'https://s3.us-west-000.backblazeb2.com/proxycurl/person/johnrmarty/profile?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0004d7f56a0400b0000000001%2F20220607%2Fus-west-000%2Fs3%2Faws4_request&X-Amz-Date=20220607T130323Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=42906efa9d1e7ba4b81bb30bacadb6ec0364688a11c408339a79a6c89cb2678a',
        #        'background_cover_image_url': 'https://s3.us-west-000.backblazeb2.com/proxycurl/person/johnrmarty/cover?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=0004d7f56a0400b0000000001%2F20220607%2Fus-west-000%2Fs3%2Faws4_request&X-Amz-Date=20220607T130323Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e01d20c194a448d576455975cc887af2b54c4fa30b710410b8985ad43bda1924',
        #        'first_name': 'John', 'last_name': 'Marty', 'full_name': 'John Marty',
        #        'occupation': 'Co-Founder at Freedom Fund Real Estate',
        #        'headline': 'Financial Freedom through Real Estate - LinkedIn Top Voice',
        #        'summary': 'Most people go through life lost, disengaged, and unhappy at work and in their lives - I\'m on a mission to solve that.\n\nI spent 10 years as the founder of Axxis Audio, an electronics company that grew to multi-million dollar sales, which I sold in 2012. At that time, I funneled my earnings into the creation of an Internet of Things company, but numerous factors lead to its demise after 2 hard fought years. \n\nAt 31, I was penny-less, had a baby on the way, and had zero job prospects (despite applying to 150 companies). My desperate situation led me to take a job at Best Buy for $12 an hour while reinventing myself through the completion of an MBA at the University of Colorado, and a 6-month software development boot camp. \n\nAfter graduation, I landed at American Express as a Senior Product Manager and then got poached by Amazon in 2017 (because of my LinkedIn profile). My journey has led to a deep sense of perspective, humility, and purpose that I draw on to help others find clarity, meaning, and happiness in their careers and lives. \n\nCheck out my website for details on my Mindset Reset Podcast, Public Speaking, Consulting, or my free 40 page LinkedIn guide\n\nhttp://www.johnraphaelmarty.com/\n\nFAQ\'s\n\nQ: Can you speak at my Company, University, event or podcast?\nA: I\'d love to! I\'ve shared my message on the future of employment, breaking into big tech, and my personal story of reinventing myself and discovering my sense of purpose (and how you can too!).\n\n☑️  YouTube Channel #1 (John Marty) : http://www.youtube.com/c/JohnMarty-uncommon\n☑️  YouTube Channel #2 (Tech Careers for non-engineers: https://www.youtube.com/channel/UC900gMMPLwRGGXSTW1gdZHA\n\nFUN FACTS:\n☑️ I am an Avid cyclist and runner, and I just started learning to skateboard a half-pipe.\n☑️ Into the Enneagram? - I\'m a #3 (The Achiever)\n\nLETS CONNECT:\n☑️ Email: JohnRmarty@gmail.com (don\'t forget that "R"....The other guy gets my emails all the time)',
        #        'country': 'US', 'country_full_name': 'United States of America', 'city': 'Seattle',
        #        'state': 'Washington', 'experiences': [
        #         {'starts_at': {'day': 1, 'month': 8, 'year': 2021}, 'ends_at': None,
        #          'company': 'Freedom Fund Real Estate',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/freedomfund', 'title': 'Co-Founder',
        #          'description': 'Our mission is to provide everyday people seeking financial freedom long before the age of 65 with the ability to invest in high yield, short-term real estate investments that were only accessible in the past for a select few wealthy individuals. Each of our single family rehab projects require a minimum investment contribution of only $10K, we have simple terms, no multi-year hold periods, and no fees. With our unique model investors can log into our easy to use website, select the projects that they want to invest in, and get realtime updates on the status of their investments.\n\nWebsite: https://www.freedomfundinvestments.com/home',
        #          'location': None,
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQEYxazZM_hXgQ/company-logo_100_100/0/1634934418976?e=1660176000&v=beta&t=0VgBUzkiLCkNkjuO1CgOWKNq3UsyhCTQSrZAieKXUHo'},
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2021}, 'ends_at': None, 'company': 'Mindset Reset Podcast',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/mindset-reset-podcast',
        #          'title': 'Founder',
        #          'description': 'We dive into the mindsets of the world’s foremost thought leaders and turn them into actionable insights so that others can discover greater happiness, success, and fulfillment.\n\nhttps://podcasts.apple.com/us/podcast/mindset-reset/id1553212607',
        #          'location': 'Denver, Colorado, United States',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQF9QJVQm3SOvA/company-logo_100_100/0/1614527476576?e=1660176000&v=beta&t=8HJU7f4IqghFhOmrdMU0z5kP_OLa2QliF2Q05VoZ1u0'},
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2020}, 'ends_at': {'day': 31, 'month': 12, 'year': 2020},
        #          'company': 'Product School',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/product-school',
        #          'title': 'Featured Speaker',
        #          'description': 'Product School is a global leader in Product Management training with a community of over one million product professionals. As a featured speaker, I help inspire the next generation of Product Managers to create innovative products and apply best practices in their work.',
        #          'location': 'Seattle, Washington, United States',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C4E0BAQFZfSlbfUe9yA/company-logo_100_100/0/1648642857246?e=1660176000&v=beta&t=-elfNcnhj6y9K9Cwrsp8LXzSjo-DfmnPz-plBNy8_VE'},
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2020}, 'ends_at': None, 'company': 'Project 1B',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/project-1b', 'title': 'Founder',
        #          'description': 'The mission of Project 1B is to help 1 Billion people around the world maximize their sense of meaning so that they can lead more fulfilling lives. We do this through exposing the truth about success and happiness through the Mindset Reset Podcast, corporate training, youth education programs, group coaching, and investments in tech startups aligned with our mission.\n\nThe word success is widely understood as the attainment of financial gain, but somewhere along the lines we began believing that money = happiness, self worth, and meaning even though money has nothing to do with these things. Because of this twisted equation, young adults often make career decisions that solely maximize earning potential. And Ironically, if they manage to achieve society’s definition of success, It often leaves many with a sense of meaninglessness.\n\nIf you want to live a meaningful life chase the word meaning as opposed to the word success - this simple shift in mindset will lead to a more authentic set of questions about the direction you should take your life.',
        #          'location': 'Denver, Colorado, United States',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQFG_MrwBC_iZg/company-logo_100_100/0/1594610187483?e=1660176000&v=beta&t=4lFRlKepnfz4X2OZTDeURxzCHfX2duvC35gtCbclnlM'},
        #         {'starts_at': {'day': 1, 'month': 2, 'year': 2019}, 'ends_at': {'day': 31, 'month': 3, 'year': 2021},
        #          'company': 'Amazon', 'company_linkedin_profile_url': 'https://www.linkedin.com/company/amazon',
        #          'title': 'Sr. Product Manager - New Business Innovation', 'description': None,
        #          'location': 'Greater Seattle Area',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQHTvZwCx4p2Qg/company-logo_100_100/0/1612205615891?e=1660176000&v=beta&t=Z51ybUs19PBmhvOYu053c5DOR0SEIn29jrdagEYLImA'},
        #         {'starts_at': {'day': 1, 'month': 3, 'year': 2017}, 'ends_at': {'day': 28, 'month': 2, 'year': 2019},
        #          'company': 'Amazon', 'company_linkedin_profile_url': 'https://www.linkedin.com/company/amazon',
        #          'title': 'Senior Manager of Product Management - Marketplace Product Quality', 'description': None,
        #          'location': 'Seattle, Washington, United States',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQHTvZwCx4p2Qg/company-logo_100_100/0/1612205615891?e=1660176000&v=beta&t=Z51ybUs19PBmhvOYu053c5DOR0SEIn29jrdagEYLImA'},
        #         {'starts_at': {'day': 1, 'month': 2, 'year': 2019}, 'ends_at': None, 'company': 'YouTube',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/youtube',
        #          'title': 'YouTube Content Creator - "Tech Careers for Non-Engineers"',
        #          'description': 'Mission: to help others land their dream jobs at a top tech companies that aligns with their passions.',
        #          'location': 'Greater Seattle Area',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C4D0BAQEfoRsyU4yUzg/company-logo_100_100/0/1631053379295?e=1660176000&v=beta&t=qzJ4JEry9ff6_yUgAbYSLPJunRlRH0TcviAG7qMlbPc'},
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2017}, 'ends_at': None, 'company': 'YouTube',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/youtube',
        #          'title': 'Youtube Content Creator - "John Marty"', 'description': None,
        #          'location': 'Seattle, Washington',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C4D0BAQEfoRsyU4yUzg/company-logo_100_100/0/1631053379295?e=1660176000&v=beta&t=qzJ4JEry9ff6_yUgAbYSLPJunRlRH0TcviAG7qMlbPc'},
        #         {'starts_at': {'day': 1, 'month': 7, 'year': 2015}, 'ends_at': {'day': 31, 'month': 3, 'year': 2017},
        #          'company': 'American Express',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/american-express',
        #          'title': 'Senior Global Product Manager', 'description': None, 'location': 'Phoenix, Arizona Area',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C4D0BAQGRhsociEn4gQ/company-logo_100_100/0/1523269243842?e=1660176000&v=beta&t=oi7LeuxdrJCYWypHGxQuDxszQ-LwItz-ZX69m26ebPY'},
        #         {'starts_at': {'day': 1, 'month': 3, 'year': 2014}, 'ends_at': {'day': 31, 'month': 7, 'year': 2014},
        #          'company': 'Mile High Automation, Inc.',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/mile-high-automation-inc-',
        #          'title': 'Sr. Product Manager',
        #          'description': 'Mile High Automation is a Smart Home Technology (Internet of Things) software and hardware development company. Our mission is to flawlessly develop and deliver impeccable software, hardware and system design for the high-end consumer market nationally and internationally. \n\n•  Performed a short term change management engagement to lead a 12 member cross functional team through a major strategy and vision transition\n•  Developed an international supply chain that increased profit margin by 30% on core products\n•  Conceptualized, implemented, and rolled out a CRM that led to a 15% higher month over month close rate; trained sales team on newly created key performance indicators to maximize growth\n•  Developed, implemented and oversaw a training process that scaled to 180+ national subcontractors\n•  Translated user stories into detailed product requirements documents that the software development team used to build new features and functionality \n•  Developed benchmarks for customer service, sales, and traffic conversion to maximize profit',
        #          'location': 'Denver Colorado',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C4E0BAQHofg3toK4P7A/company-logo_100_100/0/1519903210468?e=1660176000&v=beta&t=X1octZaXtJWus67ZxCrYJaQnda-XApiUY3zbHyqLZkg'},
        #         {'starts_at': {'day': 1, 'month': 2, 'year': 2012}, 'ends_at': {'day': 31, 'month': 5, 'year': 2014},
        #          'company': 'EOS Controls',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/eos-controls',
        #          'title': 'Founder/ Chief Operating Officer',
        #          'description': 'A Smart Home Technology (Internet of Things) software and hardware development company specializing in the mid to high-end condominium market in the United States and South America. \nEOS Controls supports the advancement of affordable and easy to user smart home technology through a network of non-traditional sales channels of architects, designers, and contractors. \n\n•  Coordinated engineering, design, and marketing strategy for the launch of 6 iOS apps\n•  Led a 5 member product team of engineers; conducted daily stand-ups and weekly design review meetings\n•  Managed and prioritized product backlog for development Sprints as well as tested products before release\n•  Effectively placed products through non-traditional distribution channels by identifying and developing relationships with over 100 national and international builders, architects, and designers',
        #          'location': 'Miami, Florida',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQFV1hvbuwyU-A/company-logo_100_100/0/1519867781218?e=1660176000&v=beta&t=Uh3UX6CHYGy-PfkXnkH3XR8J84o6Gt-AhIAvYVyLRAw'},
        #         {'starts_at': {'day': 1, 'month': 11, 'year': 2002}, 'ends_at': {'day': 31, 'month': 1, 'year': 2012},
        #          'company': 'Axxis Audio',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/axxis-audio',
        #          'title': 'President/Founder',
        #          'description': 'Specializing in Smart Home Technology - Home Automation, Internet of Things\n\n•  Raised $10,000 in investment to develop a home theater and home automation sales and installation business that grew to multi-million dollar sales (sold the company in 2011)\n•  Developed mission-centric training, responsibility, and accountability framework \n•  10 Direct Reports\n•  Responsible for resource planning, scheduling, and project management \n•  Filled the role of HR and developed a team building program for 10 direct reports, that included formal training, personal and professional peer support, mentoring and professional development; resulting in 20% higher retention rate and improved trust and communication\n•  Deployed an ERP Solution in 2007 that unified 5 departments and provided a central reporting and accountability framework for a 23% employees productivity gain\n•  Handled acquisition of 2nd largest competitor Cobalt Automation',
        #          'location': 'Durango Colorado',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQHI-DLifzJs9Q/company-logo_100_100/0/1519868629336?e=1660176000&v=beta&t=brTv86KO_JXkym5AI33_qNUHJ2iG3zgKKt0n8vPw_84'}],
        #        'education': [{'starts_at': {'day': 1, 'month': 1, 'year': 2013},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 2015},
        #                       'field_of_study': 'Finance + Economics',
        #                       'degree_name': 'Master of Business Administration (MBA)',
        #                       'school': 'University of Colorado Denver',
        #                       'school_linkedin_profile_url': 'https://www.linkedin.com/school/university-of-colorado-denver/',
        #                       'description': None,
        #                       'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQGbanOkHdRLiQ/company-logo_100_100/0/1600382740152?e=1660176000&v=beta&t=xSi92mqnuVLzxnVoEvCKHvSkjdDxGCxxBn--tDDi_Y8'},
        #                      {'starts_at': {'day': 1, 'month': 1, 'year': 2015},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 2015}, 'field_of_study': None,
        #                       'degree_name': 'School of Software Development', 'school': 'Galvanize Inc',
        #                       'school_linkedin_profile_url': 'https://www.linkedin.com/school/galvanize-it/',
        #                       'description': 'rails, ruby, rspec, capybara, bootstrap, css, html, api integration, Jquery, Javascript',
        #                       'logo_url': 'https://media-exp1.licdn.com/dms/image/C4E0BAQG1D1RHEvbQZQ/company-logo_100_100/0/1519872735270?e=1660176000&v=beta&t=dFyI-T0xFlE7f5yDw0WG2T4UW9M27A1OPVxwNE9sMyo'},
        #                      {'starts_at': {'day': 1, 'month': 1, 'year': 1999},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 2005}, 'field_of_study': 'Business',
        #                       'degree_name': 'BA', 'school': 'Fort Lewis College',
        #                       'school_linkedin_profile_url': 'https://www.linkedin.com/school/fort-lewis-college/',
        #                       'description': None,
        #                       'logo_url': 'https://media-exp1.licdn.com/dms/image/C4D0BAQGs5hZ3ROf-iw/company-logo_100_100/0/1519856111543?e=1660176000&v=beta&t=eZYfxxhbkuIXRn9hBntmhkCp53UBQHQ4-gQfmxAq1aM'},
        #                      {'starts_at': {'day': 1, 'month': 1, 'year': 2002},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 2002}, 'field_of_study': None,
        #                       'degree_name': 'Japanese Language and Literature',
        #                       'school': 'Yamasa Institute Okazaki Japan', 'school_linkedin_profile_url': None,
        #                       'description': None, 'logo_url': None},
        #                      {'starts_at': {'day': 1, 'month': 1, 'year': 2000},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 2000}, 'field_of_study': None,
        #                       'degree_name': 'Spanish Language and Literature',
        #                       'school': 'Inter American University of Puerto Rico',
        #                       'school_linkedin_profile_url': 'https://www.linkedin.com/school/inter-american-university-of-puerto-rico/',
        #                       'description': None, 'logo_url': None},
        #                      {'starts_at': {'day': 1, 'month': 1, 'year': 1996},
        #                       'ends_at': {'day': 31, 'month': 12, 'year': 1999}, 'field_of_study': None,
        #                       'degree_name': 'High School', 'school': 'Western Reserve Academy',
        #                       'school_linkedin_profile_url': None, 'description': None, 'logo_url': None}],
        #        'languages': ['English', 'Spanish', 'Japanese'], 'accomplishment_organisations': [],
        #        'accomplishment_publications': [], 'accomplishment_honors_awards': [], 'accomplishment_patents': [],
        #        'accomplishment_courses': [], 'accomplishment_projects': [
        #         {'starts_at': {'day': 1, 'month': 3, 'year': 2015}, 'ends_at': None, 'title': 'gMessenger',
        #          'description': "gMessenger was built using Ruby on Rails, and the Bootstrap HTML, CSS, and JavaScript framework. It uses a Websocket-Rails integration to post a user's message content to the page in real time, with no page refresh required. gMessenger also includes custom authentication with three different permissions levels.",
        #          'url': 'http://gmessenger.herokuapp.com/'},
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2015}, 'ends_at': None, 'title': 'Taskly',
        #          'description': 'A task and project management responsive web app utilizing Ruby on Rails - CSS and HTML',
        #          'url': 'https://hidden-coast-7204.herokuapp.com/'},
        #         {'starts_at': {'day': 1, 'month': 5, 'year': 2013}, 'ends_at': None, 'title': 'Simple Wall Mount',
        #          'description': 'Injection molded residential and commercial wall mounts for iPads and iPods. This stylish flush wall mounted solution is meant to be used in conjunction with any Home Automation System.',
        #          'url': 'http://www.simplewallmount.com'},
        #         {'starts_at': None, 'ends_at': None, 'title': 'Overwatch Safety Systems',
        #          'description': 'Overwatch Safety Systems is developing an advanced warning and information distribution system to assist law enforcement and first responders with active shooter situations in public and private venues. The system utilizes modern sonic detection algorithms to sense and announce the position of active threats to people and property. This technology is also being designed as a hi-tech electronic deterrent for high profile or vulnerable venues.',
        #          'url': None}], 'accomplishment_test_scores': [], 'volunteer_work': [
        #         {'starts_at': {'day': 1, 'month': 1, 'year': 2018}, 'ends_at': None, 'title': 'Mentor',
        #          'cause': 'Children', 'company': 'IDEO',
        #          'company_linkedin_profile_url': 'https://www.linkedin.com/company/ideo',
        #          'description': 'Early Childhood Innovation Prize Mentorship',
        #          'logo_url': 'https://media-exp1.licdn.com/dms/image/C560BAQGmdpnS6sur1A/company-logo_100_100/0/1625244393084?e=1660176000&v=beta&t=5wd6IThRhw8_YTiQt2EODvHkAKa3MUwvVaf-Yr86--A'}],
        #        'certifications': [{'starts_at': None, 'ends_at': None,
        #                            'name': 'SAFe Agile Framework Practitioner - ( Scrum, XP, and Lean Practices in the SAFe Enterprise)',
        #                            'license_number': None, 'display_source': None, 'authority': 'Scaled Agile, Inc.',
        #                            'url': None},
        #                           {'starts_at': None, 'ends_at': None, 'name': 'SCRUM Alliance Certified Product Owner',
        #                            'license_number': None, 'display_source': None, 'authority': 'Scrum Alliance',
        #                            'url': None},
        #                           {'starts_at': None, 'ends_at': None, 'name': 'Scaled Agile Framework PM/PO',
        #                            'license_number': None, 'display_source': None, 'authority': 'Scaled Agile, Inc.',
        #                            'url': None}], 'connections': 500, 'people_also_viewed': [
        #         {'link': 'https://in.linkedin.com/in/warikoo', 'name': 'Ankur Warikoo',
        #          'summary': 'Founder nearbuy.com, Mentor, Angel Investor, Public Speaker', 'location': 'India'},
        #         {'link': 'https://www.linkedin.com/in/hollylee', 'name': 'Holly Lee, SPCC (She/Her)',
        #          'summary': 'Ex-Amazon Recruiting Leader | Leadership Career Coach | Forbes Coaches Council | ➛ hollylee.co/interview-coaching',
        #          'location': 'Seattle, WA'}, {'link': 'https://www.linkedin.com/in/chloe-shih', 'name': 'Chloe Shih',
        #                                       'summary': 'Product @ Discord (Hiring!) • Previously Meta, TikTok, Google • Youtube Creator',
        #                                       'location': 'San Francisco Bay Area'},
        #         {'link': 'https://www.linkedin.com/in/renoperry', 'name': 'Reno Perry',
        #          'summary': 'Follow for Job Search Advice Used by the Top 1% | Founder @ Wiseful | Helping People Land Top Jobs in Tech | Feat. NBC, Business Insider, LinkedIn News, protocol',
        #          'location': 'Greater Chicago Area'},
        #         {'link': 'https://www.linkedin.com/in/jonathan-wonsulting', 'name': 'Jonathan Javier💡',
        #          'summary': 'CEO @ Wonsulting | Forbes 30U30 | FREE Job Resources in bio | Helping non-traditional backgrounds land jobs | Cisco, Google, Snap | Ft: Forbes, Insider, CNBC, Times, etc | TikTok+YouTube+LI Creator Accelerator Program💡',
        #          'location': 'Los Angeles, CA'},
        #         {'link': 'https://www.linkedin.com/in/jehakjerrylee', 'name': 'Jerry Lee 💡',
        #          'summary': 'Co-Founder @ Wonsulting & The20 | Need free resume feedback? Visit bit.ly/wonsulting-free-resume-review | LinkedIn Top Voice 2020, Tech, Forbes 30 under 30',
        #          'location': 'New York City Metropolitan Area'},
        #         {'link': 'https://www.linkedin.com/in/kevindnaughtonjr', 'name': 'Kevin Naughton',
        #          'summary': 'Software Engineer at Google', 'location': 'New York City Metropolitan Area'},
        #         {'link': 'https://www.linkedin.com/in/adamrbroda', 'name': 'Adam Broda',
        #          'summary': 'I Help People Break Into Technology & Engineering Careers | Sr. Manager, Product Management | Founder @ Broda Coaching | Hiring Manager | Wellness Advocate',
        #          'location': 'Greater Seattle Area'},
        #         {'link': 'https://www.linkedin.com/in/rohankamath', 'name': 'Rohan Kamath',
        #          'summary': 'Passionately curious, often wrong, always learning.', 'location': 'Seattle, WA'},
        #         {'link': 'https://www.linkedin.com/in/livelyliz', 'name': 'Elizabeth Morgan',
        #          'summary': "Career Content - 24M views | Amazon | Social Media Expert | Handmade Earring Etsy Shop Owner 'Lively Liz Creations'| Ex-Google Recruiting",
        #          'location': 'Greater Seattle Area'},
        #         {'link': 'https://www.linkedin.com/in/abelcak', 'name': 'Austin Belcak',
        #          'summary': 'I Teach People How To Land Amazing Jobs Without Applying Online // Need Help With Your Job Search? Head To 👉 CultivatedCulture.com/Coaching',
        #          'location': 'New York, NY'},
        #         {'link': 'https://www.linkedin.com/in/mayagrossman', 'name': 'Maya Grossman',
        #          'summary': 'I help ambitious professionals level up, earn more and find fulfillment | Career Coach | Best-Selling Author: Invaluable | Ex Google, Microsoft | Startup Adviser',
        #          'location': 'Austin, TX'},
        #         {'link': 'https://www.linkedin.com/in/gretchen-smith-56a234186', 'name': 'Gretchen Smith',
        #          'summary': 'Opinions are my own. Join. Donate. Share our mission. codeofvets.com',
        #          'location': 'Murfreesboro, TN'},
        #         {'link': 'https://www.linkedin.com/in/aishwarya-srinivasan', 'name': 'Aishwarya Srinivasan',
        #          'summary': 'Data Scientist - Google Cloud | LinkedIn Top Voice Data & AI 2020 | 310k Followers',
        #          'location': 'San Francisco Bay Area'},
        #         {'link': 'https://www.linkedin.com/in/diegogranadosh', 'name': 'Diego Granados',
        #          'summary': "Sr. Product Manager @ LinkedIn | Ask me for my free step-by-step guide to be a PM | I'll help you become a Product Manager! | DMs open! ✌️",
        #          'location': 'San Francisco Bay Area'},
        #         {'link': 'https://www.linkedin.com/in/mauricephilogene', 'name': 'Maurice Philogene',
        #          'summary': 'Investor | Public Servant | Philanthropist |                   Lifestyle Design & Financial Freedom Coach',
        #          'location': 'Washington, DC'},
        #         {'link': 'https://www.linkedin.com/in/jennifer-a-welsh', 'name': 'Jennifer Welsh',
        #          'summary': 'I demystify the stock market for new investors.', 'location': 'Nashville, TN'},
        #         {'link': 'https://www.linkedin.com/in/alliekmiller', 'name': 'Allie K. Miller',
        #          'summary': 'Global Head of Machine Learning BD, Startups and Venture Capital at AWS | 1MM+ followers | LinkedIn Top Voice 2019, 2020, 2021',
        #          'location': 'San Francisco Bay Area'},
        #         {'link': 'https://www.linkedin.com/in/danpriceseattle', 'name': 'Dan Price',
        #          'summary': 'Founder/CEO, Gravity Payments', 'location': 'Greater Seattle Area'},
        #         {'link': 'https://th.linkedin.com/in/lillianpierson', 'name': 'Lillian Pierson, P.E.',
        #          'summary': '🦄 Data / AI Expert ▪ CMO ▪ CEO / Head of Product ▪ Data Startup Mentor ▪ Data Strategy / Data Science Instructor (1.3 MM+ learners 🎉)',
        #          'location': 'Ko Samui'}], 'recommendations': [
        #         'Rebecca Canfield\n      \n          \n\n\n\n              \n                \n        \n              \n  \n\n      \n          John Marty is a genius at his craft. He is skilled in the art of making people feel empowered to seek out roles that they are qualified for, ask for salaries that they deserve, and creates a kind of pay it forward lifestyle. John helps you to get to places that you only thought were possible for other people. Anyone that is fortunate enough to learn from John should consider themselves extremely lucky. I know I do. ',
        #         "Zoe Sanoff\n      \n          \n\n\n\n              \n                \n        \n              \n  \n\n      \n          John is so focused on helping guide you through an interview process not just for Amazon but on interviewing in general.  I've generally done well at interviewing, my skills are top notch now.  John is so focused on on his clients and really goes above and beyond.  John is genuine, knowledgeable, well spoken and non-judgemental.  He is so encouraging, so positive and really easy to talk to.  Thank you John!"],
        #        'activities': [{
        #            'title': 'I want to caution the commonly held societal belief that taking a pay cut will equate to less hours and more freedom. Most jobs require us to work…',
        #            'link': 'https://www.linkedin.com/posts/johnrmarty_i-want-to-caution-the-commonly-held-societal-share-6929504579512385536-SZUp',
        #            'activity_status': 'Posted by John Marty'}, {
        #            'title': 'CASE STORY: GENERATING THEIR HIGHEST $$$ IN 14 YEARS!You’ll love this! A $4B #lifescience company engaged my digital marketing agency to increase…',
        #            'link': 'https://www.linkedin.com/feed/update/urn:li:activity:6929441439680540672',
        #            'activity_status': 'Liked by John Marty'}, {
        #            'title': "Did the cute puppy catch your attention? 🐶 Good! Cuz, we're hosting a free live resume review show tomorrow, Tuesday, May 10th at 12 pm ET and we…",
        #            'link': 'https://www.linkedin.com/posts/heather-austin_did-the-cute-puppy-catch-your-attention-share-6929413477941874688-RQZI',
        #            'activity_status': 'Liked by John Marty'}], 'similarly_named_profiles': [
        #         {'name': 'John Martinez', 'link': 'https://www.linkedin.com/in/john-martinez-90384a229',
        #          'summary': 'Owner of Fight or Flight Medical Consultants, LLC  , Owner Marty’s Hardwood Works',
        #          'location': 'San Antonio, TX'}, {'name': 'John Marty', 'link': 'https://www.linkedin.com/in/jomarty',
        #                                           'summary': 'John Michael Marty WSMI Show at WSMI-FM 106.1',
        #                                           'location': 'Springfield, Illinois Metropolitan Area'},
        #         {'name': 'John Marty', 'link': 'https://www.linkedin.com/in/senatormarty', 'summary': None,
        #          'location': 'St Paul, MN'}, {'name': 'John Marty', 'link': 'https://www.linkedin.com/in/johnmarty',
        #                                       'summary': 'Lead Software Engineer, Commerce at Disney Parks  & Resorts Digital',
        #                                       'location': 'Orlando, FL'}], 'articles': [], 'groups': [{
        #         'profile_pic_url': 'https://media-exp1.licdn.com/dms/image/C4E07AQF2EKTooicxbg/group-logo_image-shrink_92x92/0/1631006354581?e=1652335200&v=beta&t=ZAG_a8mJ4PMRydzfnnaMivhcxRoA44aVnnlS1-s-kLg',
        #         'name': 'Find Your Why (webinar follow-up)',
        #         'url': 'https://www.linkedin.com/groups/12431669'},
        #         {
        #             'profile_pic_url': 'https://media-exp1.licdn.com/dms/image/C5607AQFoObVGhIVOMw/group-logo_image-shrink_92x92/0/1631009516456?e=1652335200&v=beta&t=zOESoMPIMuNqonz7wiGqncSpHCG37kqczWQrPsZTYhQ',
        #             'name': 'Harvard Business Review Discussion Group',
        #             'url': 'https://www.linkedin.com/groups/3044917'},
        #         {
        #             'profile_pic_url': 'https://media-exp1.licdn.com/dms/image/C5607AQEF-0lU7YuvFw/group-logo_image-shrink_92x92/0/1631011968285?e=1652335200&v=beta&t=JGccw8QsyapjmKBnDkt_9X3UmgKfRDUTnUS6izHfReU',
        #             'name': 'Local Seattle Connections',
        #             'url': 'https://www.linkedin.com/groups/13612052'},
        #         {
        #             'profile_pic_url': 'https://media-exp1.licdn.com/dms/image/C4E07AQEpOgpQbQSzlw/group-logo_image-shrink_92x92/0/1631005705998?e=1652335200&v=beta&t=7viIX9nYE7q7kz-55c2a_zdf4bdmYrzfzVzsoU96qi4',
        #             'name': 'On Startups - The Community For Entrepreneurs',
        #             'url': 'https://www.linkedin.com/groups/2877'},
        #         {
        #             'profile_pic_url': 'https://static-exp1.licdn.com/sc/h/4h1ldzvvebtszyx75ve7dst1v',
        #             'name': 'University of Colorado Executive MBA Program Alumni (official)',
        #             'url': 'https://www.linkedin.com/groups/981'}],
        #        'extra': {'github_profile_id': 'github.com/johnrmarty', 'twitter_profile_id': 'twitter.com/johnrmarty',
        #                  'facebook_profile_id': 'facebook.com/johnraphaelmarty'},
        #        'skills': ['adobe creative suite', 'analysis', 'branding', 'budgets', 'business development',
        #                   'business planning', 'business strategy', 'consumer electronics', 'css', 'entrepreneurship',
        #                   'evangelism', 'html5', 'leadership', 'management', 'marketing', 'marketing strategy',
        #                   'new business development', 'product development', 'product management', 'product marketing',
        #                   'public speaking', 'ruby on rails', 'social media', 'start ups', 'strategic planning'],
        #        'inferred_salary': {'min': None, 'max': None}, 'gender': 'male',
        #        'birth_date': {'day': 1, 'month': 1, 'year': 1980}, 'industry': 'computer software',
        #        'interests': ['mountain biking', 'road cycling', 'road running', 'trail running', 'triathalons'],
        #        'personal_numbers': ['9707495020'], 'personal_emails': ['johnrmarty@gmail.com']}

        print("res value---------->", res)

        if self.env.context.get('active_id'):
            print('This is active id line 1')
            applicant = self.env['hr.applicant'].browse(self.env.context.get('active_id'))
            print('This is active id line 2', self)
            education_ids = []

            # education_obj = self.env['hr.applicant.degree']


            skill_ids = []
            skill_obj = self.env['hr.applicant.skill']
            for index, skill in enumerate(res['skills']):
                temp = skill_obj.search([('name', '=ilike', skill)])
                if temp:
                    skill_ids.append(temp.id)
                if not temp:
                    temp_create = self.env['hr.applicant.skill'].create({
                        'name': skill,
                        'color': index
                    })
                    skill_ids.append(temp_create.id)
                    # applicant.id.write({'skill_ids': [(4, [skill_ids.id])]})



        resp = {}
        if applicant.exists():
            resp = {'partner_name': res['full_name'], 'email_from': res['personal_emails'][0] if res['personal_emails'] else '',
                    'partner_mobile': res['personal_numbers'][0] if res['personal_numbers'] else '',
                    'type_id': [(6, 0, education_ids)],
                    'skill_ids': [(6, 0, skill_ids)],
                    }
            print('This is data------------------------------> ', resp)
            applicant.write(resp)

        # resp = ({'name': res['full_name'], 'email_from': res['personal_emails'],
        #                      'partner_mobile': res['personal_numbers'],
        #                      'type_id': res['education'][3]['degree_name'], 'skill_ids': skill_ids,
        #                      'salary_expected': res['inferred_salary']['min'],
        #                      'total_experience': res['experiences']})
        #

    # if self.env.context.get('active_id'):
    #     print('This is active id line 1')
    #     applicant = self.env['hr.applicant'].browse(self.env.context.get('active_id'))
    #     print('This is active id line 2', self)
    #     if applicant.exists():
    #         applicant.name = res['full_name']
    #         # move.partner_name = res['first_name']
    #         applicant.email_from = res['personal_emails']
    #         # move.email_cc = res['email_cc']
    #         # move.partner_phone = res['partner_phone']
    #         applicant.partner_mobile = res['personal_numbers']
    #         # move.type_id = res['degree_name']
    #         # move.skill_ids = res['skills']  1
    #         # move.user_id = res['user_id']
    #         # move.medium_id = res['medium_id']
    #         # move.source_id = res['source_id']
    #         # move.department_id = res['department_id']
    #         applicant.salary_expected = res['inferred_salary']['min']
    #         # move.salary_proposed = res['salary_proposed']
    #         # move.availability = res['availability']
    #         applicant.total_experience = res['experiences']
    #         print("if condition =====================",applicant.name)

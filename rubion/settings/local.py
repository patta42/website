import os

LOGGING = {
    'version' : 1,
    'disable_existing_loggers': False,
    'handlers' : {
        'cron': {
            'level' : 'INFO',
            'class' : 'logging.FileHandler',
            'filename' : '/var/log/rubion/cronjobs/info.log'
        }
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        }
    },
    'loggers' : {
        'warn_projects' : {
            'handlers' : [ 'cron' ],
            'level': 'INFO',
            'propagate' : True,
            'formatter' : 'simple'
        }
    }
}
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rubion3',
    }
}
COURSE_LATEX_TEMPLATES_DIR = '/usr/local/lib/rubion/tex-templates/'
COURSE_SCRIPT_HEADER =  os.path.join(COURSE_LATEX_TEMPLATES_DIR,'scriptheader')
COURSE_LATEX_VAR_DIR = os.path.dirname('/var/rubion/')
COURSE_LATEX_TEXFILE_DIR = os.path.dirname(os.path.join(COURSE_LATEX_VAR_DIR, 'texfiles/'))
COURSE_LATEX_PDFFILE_DIR = os.path.dirname(os.path.join(COURSE_LATEX_VAR_DIR, 'pdffiles/'))
COURSE_LATEX_PDFFILE_URI = '/autogenerated-pdfs/'

from distutils.core import setup

setup(
    name='OpenEthics',
    version='0.1.0',
    author='Jason Marshall',
    author_email='j.j.marshall@kent.ac.uk',
    packages=['applicationform', 
              'checklist', 
              'ethicsapplication',
              'publisher', 
              'review',
              'root',
              'settings',
              'workflowutils',],
      
    scripts=[],
    url='http://pypi.python.org/pypi/OpenEthics/',
    license='LICENSE',
    description='A basic framework for building RMAS adapters',
    long_description=open('README.md').read(),
    install_requires=[
                        'Django==1.4',
                        'Jinja2==2.6',
                        'Pygments==1.5',
                        'django-questionnaire',
                        'django-questionnaire',
                        'django-permissions',
                        'django-workflows==1.0.2',
                        'pika==0.9.6',
    ],
)
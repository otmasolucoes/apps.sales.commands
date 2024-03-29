from setuptools import find_packages, setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_requirements():
    return open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read().splitlines()
    #dependencies = [
    #    'Django>=2.0.5',
    #    'pytz>=2018.4',
    #    'apps.core.commons==0.1',
    #    'apps.core.communications==0.1'
    #]
    #return dependencies


setup(
    name='apps.sales.commands',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Command control components for sales module.',
    long_description=README,
    url='https://www.otmasolucoes.com/',
    author='Diego Pasti',
    author_email='diegopasti@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0.5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

    dependency_links=[
        "https://github.com/otmasolucoes/apps.core.commons/zipball/master#egg=apps.core.commons-0.1",
        "https://github.com/otmasolucoes/apps.core.communications/zipball/master#egg=apps.core.communications-0.1",
    ],

    install_requires=get_requirements(),
    setup_requires=get_requirements(),
)

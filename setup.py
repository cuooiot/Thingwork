from setuptools import setup

setup(
    name='cuoo.thingy',
    version='0.1',
    description='Make anything an IoT thingy',
    author='Jordan Bugbird',
    author_email='jordan@cuoo.io',
    url='https://l.cuoo.io/thingy',
    packages=['cuoo.thingy.core', 'cuoo.thingy.component', 'cuoo.thingy.web', 'cuoo.thingy.web.controllers',
              'cuoo.thingy.web.middleware'],
    install_requires=[
        'aiohttp',
        'redis'
    ]
)

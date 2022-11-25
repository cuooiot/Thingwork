from setuptools import setup

setup(
    name='cuoo.thingwork',
    version='0.5.0',
    description='Make anything an IoT thingy',
    author='Bugbird Co.',
    author_email='hey@cuoo.io',
    url='https://l.cuoo.io/thingwork',
    packages=['cuoo.thingy.core', 'cuoo.thingy.component', 'cuoo.thingy.web', 'cuoo.thingy.web.controllers',
              'cuoo.thingy.web.middleware'],
    install_requires=[
        'aiohttp',
        'redis'
    ]
)

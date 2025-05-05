from setuptools import setup, find_packages

setup(
    name='plugin.video.animesphere',
    version='1.0.0',
    packages=find_packages(),
    package_data={'': ['*.py']},
    install_requires=[
        'requests',
        'unittest.mock'
    ]
)

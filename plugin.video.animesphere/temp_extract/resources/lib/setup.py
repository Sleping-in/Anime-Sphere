from setuptools import setup, find_packages

setup(
    name="animesphere",
    version="0.0.1",
    description="Kodi plugin for MyAnimeList integration",
    packages=find_packages(),
    package_dir={'': '.'},
    install_requires=[
        'requests>=2.25.1',
        'python-dateutil>=2.8.2',
        'six>=1.16.0'
    ],
    include_package_data=True
)

from setuptools import (
    find_packages,
    setup
)

INSTALL_REQUIRES = [
    'requests-http-signature==v0.1.0'
]

setup(
    name='remoteit-ssh',
    description='Opens an SSH connection to a remoteit device by name.',
    version='0.1.0',
    url='https://github.com/conor-f/remoteit-ssh',
    python_requires='>=3.6',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'remoteit-ssh = remoteit_ssh.client:main'
        ]
    }
)

import os

from setuptools import (
    find_packages,
    setup
)

from setuptools.command.install import install


class CustomInstallCommand(install):
    """
    Using this as a post-install hook to alias the output of the internal
    script to an interactive script run in ZSH.
    """

    def run(self):
        os.system("sh resources/post_install_script.sh")

        install.run(self)


INSTALL_REQUIRES = [
    'requests-http-signature==v0.1.0'
]

setup(
    name='remoteit-ssh',
    description='Opens an SSH connection to a remoteit device by name.',
    version='0.2.0',
    url='https://github.com/conor-f/remoteit-ssh',
    python_requires='>=3.6',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            '_remoteit-ssh = remoteit_ssh.client:main'
        ]
    },
    data_files=([
        "resources/post_install_script.sh",
    ]),
    cmdclass={
        'install': CustomInstallCommand,
    },
)

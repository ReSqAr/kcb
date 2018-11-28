from setuptools import setup

setup(
    name="kcb",
    packages=["kcb", "kcb.lib"],
    version="1.0",
    description="KDE Connect bash helper",
    author="Yasin Zaehringer",
    author_email="yasin.zaehringer-kcb@yhjz.de",
    url="https://github.com/ReSqAr/kcb",
    keywords=["kdeconnect"],
    entry_points={
        'console_scripts': [
            'kcb = kcb.__main__:main'
        ]},
    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    long_description="""\
Execute bash scripts on your smart phone's memory from your computer

Execute bash scripts on sshfs mounts of smart phones using KDE Connect 
-------------------------------------

This version requires Python 3 or later.
"""
)

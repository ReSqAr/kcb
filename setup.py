from setuptools import setup

setup(
    name="kcb",
    packages=["kcb", "kcb.lib"],
    version="0.2",
    description="KDE Connect bash helper",
    author="Yasin Zaehringer",
    author_email="yasin-kcb@yhjz.de",
    url="https://github.com/ReSqAr/kcb",
    keywords=["kdeconnect"],
    entry_points={
        'console_scripts': [
            'kcb = kcb.__main__:main'
        ]},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
    ],
    long_description="""\
Execute bash scripts on your smart phone from your computer

Execute bash scripts on sshfs mounts of smart phones using KDE Connect 
-------------------------------------

This version requires Python 3 or later.
"""
)

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="kcb",
    packages=["kcb", "kcb.lib"],
    version="0.9.2.1",
    description="Execute bash scripts on top of KDEConnect's sftp mount",
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
    install_requires=[
        "pydbus",
    ],
    # https://packaging.python.org/tutorials/packaging-projects/
    long_description=long_description,
    long_description_content_type="text/markdown",
)

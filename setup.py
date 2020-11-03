from setuptools import setup

with open("README.rst", encoding='utf-8') as README:
    readme = str(README.read())

with open("requirements.txt") as reqs:
    lines = reqs.read().split("\n")
    install_requires = [line for line in lines if line]

setup(
    name="swc_api",
    version="0.1.8",
    description="A library for interacting with the Small World Community REST API",
    long_description=readme,
    long_description_content_type='text/x-rst',
    url="https://github.com/citizensclimateeducation/community_api",
    author="Bryan Hermsen",
    author_email="b_hermse@hotmail.com",
    install_requires=install_requires,
    packages=["swc_api"],
    include_package_data=True,
    keywords="rest, requests",
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

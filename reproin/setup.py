from setuptools import setup, find_packages

setup(
    name="reproin",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "datalad",
        "datalad-container",
        "python-dateutil",
        "pyyaml",
    ],
    entry_points="""
        [console_scripts]
        reproin=reproin.cli:main
    """,
    python_requires=">=3.7",
    author="ReproNim Center",
    author_email="info@repronim.org",
    description="A tool for automatic generation of shareable BIDS datasets from MR scanners",
    url="https://github.com/ReproNim/reproin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyguime-hbilar", # Replace with your own username
    version="0.0.1",
    author="Henrik Bilar",
    author_email="henrik@bilar.co.uk",
    description="Simple GUI functions for pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hbilar/pyguime",
    packages=setuptools.find_packages(include=['pyguime']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2.1",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
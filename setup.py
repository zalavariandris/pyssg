import setuptools

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyssg-zalavariandris", # Replace with your own username
    version="0.0.1",
    author="András Zalavári",
    author_email="zalavariandris@gmail.com",
    description="a simple static site generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zalavariandris/pyssg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
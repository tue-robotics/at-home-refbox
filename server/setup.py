import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="at-home-refbox-server",
    version="0.0.1",
    author="Janno Lunenburg",
    author_email="jannolunenburg@gmail.com",
    description="Server of the RoboCup @Home refbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tue-robotics/at-home-refbox/tree/master/server",
    packages=setuptools.find_packages(),
    scripts=['server']
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

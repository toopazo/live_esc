import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="live_esc",    # Replace with your own username
    version="0.0.8",
    author="toopazo",
    author_email="toopazo@protonmail.com",
    description="Python package to communicate with an ESC and log, parse and plot data in real time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toopazo/live_esc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

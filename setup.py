import setuptools

with open("README.md", "r", encoding="utf-8") as fh_readme:
    long_description = fh_readme.read()

setuptools.setup(
    name = "iot_web_app",
    version = "0.0.dev4",
    author = "Walter Pachlinger",
    author_email = "walter.pachlinger@gmail.com",
    description = "Web applications for the Raspberry Pi based IOT system.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent"
    ],
    python_requires = ">= 3.7"
)


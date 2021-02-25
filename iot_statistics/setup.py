import setuptools

with open("README.md", "r", encoding="utf-8") as fh_readme:
    long_description = fh_readme.read()

setuptools.setup(
    name = "iot_statistics",
    version = "0.0.dev5",
    author = "Walter Pachlinger",
    author_email = "walter.pachlinger@gmail.com",
    description = "Inspect the contents of a statistics database (created by an IOT Recorder).",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "",
    packages = setuptools.find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent"
    ],
    install_requires = [
        'flask',
    ],
    python_requires = ">= 3.7"
)


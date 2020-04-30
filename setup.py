import setuptools

long_description = "awsbrainsworks"

description = "Accelerate machine learning experimentation"
distname = "awsbrainsworks"
license = "MIT"
maintainer = "Tyler Peterson"
maintainer_email = "petersontylerd@gmail.com"
project_urls = {
    "bug tracker": "https://github.com/petersontylerd/awsbrainsworks/issues",
    "source code": "https://github.com/petersontylerd/awsbrainsworks",
}
url = "https://github.com/petersontylerd/awsbrainsworks"
version = "0.1.4"


def setup_package():
    metadata = dict(
        name=distname,
        packages=[
            "awsbrainsworks",
            "awsbrainsworks.compute",
            "awsbrainsworks.compute.ec2",
            "awsbrainsworks.compute.emr",
            "awsbrainsworks.compute.setup",
        ],
        maintainer=maintainer,
        maintainer_email=maintainer_email,
        description=description,
        keywords=["machine learning", "data science"],
        license=license,
        url=url,
        project_urls=project_urls,
        version=version,
        long_description=long_description,
        include_package_data=True,
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Visualization",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.6.1",
        install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    )

    setuptools.setup(**metadata)


if __name__ == "__main__":
    setup_package()

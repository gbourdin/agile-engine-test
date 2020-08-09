from setuptools import find_packages, setup


setup(
    name="image_search_api",
    version="0.0.1",
    description="image_search_ Web API",
    url="https://github.com/gbourdin/agile-engine-test",
    author="German Bourdin",
    author_email="german.bourdin@gmail.com",
    packages=find_packages(),
    install_requires=[
        "flask>=1.1.2",
        "flask-restx>=0.2.0",
        "requests>=2.24.0",
        "tqdm>=4.48.2",
        "uWSGI>=2.0.19",
    ],
    setup_requires=["pytest-runner>=2.11.0"],
    tests_require=["pytest>=3.2.0", "pytest-flask>=0.10.0"],
    extras_require={"dev": ["pycodestyle>=2.3.0", "flake8>=3.5.0"]},
    entry_points={
        "console_scripts": ["image_search_api = image_search_api.__main__:cli"]
    },
)

from setuptools import setup

def get_requires(filename):
    requirements = []
    with open(filename, "rt") as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                requirements.append(line)
    return requirements

setup(
    name = "youtube_feed_dl",
    version = "0.0.1",
    author = "Yousef/Sammy Al Hashemi",
    author_email = "",
    description = ("Downloads your youtube feed."),
    license = "BSD",
    keywords = "youtube,python,ytdl",
    url = "http://packages.python.org/youtube_feed_dl",
    packages=['youtube_feed_dl', 'tests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=get_requires("requirements.txt"),
    entry_points={
        "console_scripts": [
                "youtube_feed_dl=youtube_feed_dl.youtube_feed_dl:main"
            ]
        }
)

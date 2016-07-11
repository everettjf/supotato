from setuptools import setup

setup(
        name="supotato",
        version="2.0.1",
        description="Classify the header (.h) files in to a txt report.",
        url="http://github.com/everettjf/supotato",
        author="everettjf",
        author_email="everettjf@live.com",
        license='MIT',
        packages=["supotato"],
        entry_points="""
             [console_scripts]
             supotato = supotato.supotato:main
        """,
        install_requires=[
            'six>=1.10.0',
        ],
        zip_safe=False
)

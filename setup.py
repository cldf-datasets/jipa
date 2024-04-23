from setuptools import setup


setup(
    name='cldfbench_jipa',
    py_modules=['cldfbench_jipa'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'jipa=cldfbench_jipa:Dataset',
        ]
    },
    install_requires=[
        'clld',
        'pyglottolog',
        'pyclts',
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

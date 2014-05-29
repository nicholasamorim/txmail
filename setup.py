from setuptools import setup

long_description = '''
Use Twisted to send emails via SMTP asynchronously. Receive emails
using POP3 and IMAP and pass a callback that will deal with the email
or save it all to a specified folder.
'''

setup(
    name='txmail',
    version='0.1',
    description='Defer your emails.',
    long_description=long_description,
    url='http://github.com/nicholasamorim/txmail',
    license='MIT',
    author='Nicholas Amorim',
    author_email='nicholas@alienretro.com',
    packages=['txmail'],
    test_suite='tests',
    install_requires=['Twisted >= 12.1.0'],
    include_package_data = True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
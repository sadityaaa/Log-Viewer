from setuptools import setup

APP = ['log_viewer.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Log Viewer',
        'CFBundleDisplayName': 'High-Performance Log Viewer',
        'CFBundleIdentifier': 'com.logviewer.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

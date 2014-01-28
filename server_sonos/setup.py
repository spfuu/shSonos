from distutils.core import setup

setup(
    name='sonos_broker',
    version='0.1',
    packages=['server_sonos'],
    #package_dir={'': 'server_sonos'},
    url='https://github.com/pfischi/shSonos',
    license='',
    author='pfischi',
    author_email='pfischi@gmx.de',
    description='sonos htp/udp broker',
    requires=['requests']
)

from distutils.core import setup

setup(
    name='sonos_broker',
    version='0.1.9',
    packages=['lib_sonos', 'soco'],
    scripts=['sonos_broker', 'sonos_broker.sh'],
    url='https://github.com/pfischi/shSonos',
    license='',
    author='pfischi',
    author_email='pfischi@gmx.de',
    description='sonos htp/udp broker',
    requires=['requests']
)

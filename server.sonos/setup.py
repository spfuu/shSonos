from distutils.core import setup
from lib_sonos import definitions

setup(
    name='sonos_broker',
    version='{version}'.format(version=definitions.VERSION_BUILDSTRING),
    packages=['lib_sonos', 'soco', 'soco.music_services'],
    scripts=['sonos_broker', 'sonos_broker.cfg', 'sonos_cmd'],
    url='https://github.com/pfischi/shSonos',
    license='',
    author='pfischi',
    author_email='pfischi@gmx.de',
    description='sonos broker',
    requires=['requests']
)

import os
import subprocess
from setuptools import setup
from lib_sonos import definitions
from setuptools.command.install import install
from pkg_resources import resource_filename, Requirement
import shutil


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class PostInstallCommand(install):
    def run(self):
        install.run(self)

        try:
            conf_default_path = "/etc/default/"
            if not os.path.exists(conf_default_path):
                os.makedirs(conf_default_path)

            config_filename = resource_filename(Requirement.parse("sonos-broker"), "config/sonos-broker")
            shutil.copy(config_filename, conf_default_path)
            self.set_autostart()
        except:
            pass

    def set_autostart(self):

        upstart_filename = resource_filename(Requirement.parse("sonos-broker"), "scripts/upstart/sonos-broker.conf")
        systemd_filename = resource_filename(Requirement.parse("sonos-broker"), "scripts/systemd/sonos-broker.service")

        print("\nChecking systems start method ... ", end="")

        strings_process = subprocess.Popen(["strings", "/sbin/init"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        s_out, s_err = strings_process.communicate()

        awk_process = subprocess.Popen(
            ["awk", "match($0, /(upstart|systemd|sysvinit)/) { print toupper(substr($0, RSTART, RLENGTH));exit; }"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = awk_process.communicate(input=s_out)
        start_method = out.decode().strip('\n')
        valid_methods = ['UPSTART', 'SYSTEMD', 'SYSVINIT']

        if start_method not in valid_methods:
            print(bcolors.FAIL + 'not ok')
            print("Unable to detect the systems start method.")
            print(
                "Choose a suitable script from /usr/share/sonos for your system and install it manually.\n" + bcolors.ENDC)
            exit()

        print(bcolors.OKGREEN + 'ok ' + bcolors.OKBLUE + '[{method}]'.format(method=start_method) + bcolors.ENDC)

        src_file = ""
        dest_dir = ""
        user_hint = ""
        additional_command = []
        autostart_hint = ""

        if start_method == "UPSTART":
            src_file = upstart_filename
            dest_dir = "/etc/init"
            user_hint = "sudo service {file} [start|stop|restart]"
            autostart_hint = "For auto-start edit " + bcolors.OKBLUE + os.path.join(dest_dir,
                                                                                    os.path.basename(src_file)) \
                             + bcolors.ENDC + " and uncomment line " + bcolors.OKBLUE + "'start on runlevel [2345]'\n" \
                             + bcolors.ENDC

        elif start_method == "SYSTEMD":
            src_file = systemd_filename
            dest_dir = "/etc/systemd/system"
            user_hint = "sudo systemctl [start|stop|restart|status] {file}"

            reload_systemctl = subprocess.Popen(["systemctl", "daemon-reload"], stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE)

            autostart_hint = "For auto-start execute " + bcolors.OKBLUE + "sudo systemctl enable " \
                             + os.path.basename(src_file) + bcolors.ENDC + "\n"

            additional_command = [reload_systemctl]

        elif start_method == "SYSVINIT":
            print("SYSVINIT detected. No auto-start script defined. You have to create an appropriate script which fits"
                  " to your Linux distribution.\n")
            exit()
        else:
            exit()

        script_name = os.path.basename(src_file)
        user_hint = user_hint.format(file=script_name.split('.')[0])

        print("Checking permissions ... ", end="")

        if not os.access(dest_dir, os.W_OK):
            print(bcolors.FAIL + 'not ok')
            print("No 'write' permissions to '{dir}'. Please re-run the script with "
                  "root permissions.\n".format(dir=dest_dir) + bcolors.ENDC)
            exit()

        print(bcolors.OKGREEN + "ok" + bcolors.ENDC)
        print("Copying start script to {dir} ... ".format(dir=dest_dir), end="")

        try:
            shutil.copy(src_file, os.path.join(dest_dir, script_name))
        except IOError:
            print(bcolors.FAIL + "not ok")
            print("No 'write' permissions to '{dir}'. Please re-run the script with "
                  "root permissions.\n".format(dir=dest_dir) + bcolors.ENDC)

        print(bcolors.OKGREEN + "ok " + bcolors.OKBLUE + "[{file}]".format(
            file=os.path.join(dest_dir, script_name)) + bcolors.ENDC)

        for command in additional_command:
            command.communicate()

        print(bcolors.OKGREEN + "Sonos Broker service successfully installed." + bcolors.ENDC)
        print("Type " + bcolors.OKBLUE + "{hint}".format(hint=user_hint) + bcolors.ENDC + " to control the service.")
        print(autostart_hint)

setup(
    name='sonos-broker',
    version='{version}'.format(version=definitions.VERSION),
    packages=['lib_sonos', 'soco', 'soco.music_services'],
    scripts=['sonos-broker', 'sonos-cmd'],
    url='https://github.com/pfischi/shSonos',
    license='',
    author='pfischi',
    author_email='pfischi@gmx.de',
    description='sonos broker',
    install_requires=['requests', 'xmltodict'],
    cmdclass={'install': PostInstallCommand},
    include_package_data=True
)

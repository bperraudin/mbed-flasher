"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author:
Jussi Vatjus-Anttila <jussi.vatjus-anttila@arm.com>

Note:

These devices is not originally mbed -devices, but is also supported
"""

import os
import re
import subprocess
import logging
import tempfile

class FlasherAtprogram(object):
    name = "Atprogram"
    exe = None
    supported_targets=["SAM4E"]
    logger = logging

    def __init__(self, exe=None):
        FlasherAtprogram.set_atprogram_exe(exe)
        self.logger = logging.getLogger('mbed-flasher')

    @staticmethod
    def get_supported_targets():
        return {
            "SAM4E": {
                "yotta_targets": [],
                "properties": {
                    "binary_type": ".bin",
                    "copy_method": "atprogram",
                    "reset_method": "default",
                    "program_cycle_s": 0
                }
            }
        }

    @staticmethod
    def set_atprogram_exe(exe):
        if exe is None:
            alternatives = [
                "C:/Program Files (x86)/Atmel/Atmel Studio 6.2/atbackend/atprogram.exe"
            ]
            FlasherAtprogram.exe = FlasherAtprogram.lookupExe(alternatives)
            if FlasherAtprogram.exe is None:
                FlasherAtprogram.exe = "atprogram.exe" # assume that atprogram is in path
        else:
            FlasherAtprogram.exe = exe

        FlasherAtprogram.logger.debug("atprogram location: %s", FlasherAtprogram.exe)


    @staticmethod
    def get_available_devices():
        """list available devices
        """
        FlasherAtprogram.set_atprogram_exe(FlasherAtprogram.exe)
        cmd = FlasherAtprogram.exe + " list"
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr = proc.communicate()
        connected_devices = []
        if proc.returncode == 0 :
            lines = stdout.splitlines()
            for line in lines:
                ret = FlasherAtprogram.find(line, 'edbg\W+(.*)')
                if ret:
                    connected_devices.append({
                        "platform_name": "SAM4E",
                        "serial_port": None,
                        "mount_point": None,
                        "target_id": ret,
                        "baud_rate": 460800
                    })
        FlasherAtprogram.logger.debug("Connected atprogrammer supported devices: %s", connected_devices)
        return connected_devices

    # actual flash procedure
    def flash(self, source, target):
        """flash device
        :param sn: device serial number to be flashed
        :param binary: binary file to be flash
        :return: 0 when flashing success
        """
        with tempfile.TemporaryFile() as temp:
             temp.write(source)
             temp.close()
             temp.name
             # actual flash procedure

             cmd = self.exe+" -t edbg -i SWD -d atsam4e16e -s "+target['target_id']+" -v -cl 10mhz  program --verify -f "+temp.name
             proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
             stdout, stderr = proc.communicate()
             FlasherAtprogram.logger.debug(stdout)
             FlasherAtprogram.logger.debug(stderr)
             return proc.returncode

    @staticmethod
    def lookupExe(alternatives):
        """lookup existing exe
        :param alternatives: exes
        :return: founded exe
        """
        for exe in alternatives:
            if os.path.exists(exe):
                return exe
        return None

    @staticmethod
    def find(line, lookup):
        """find with regexp
        :param line:
        :param lookup:
        :return:
        """
        m = re.search(lookup, line)
        if m:
            if m.group(1):
                return m.group(1)
        return False
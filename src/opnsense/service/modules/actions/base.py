"""
    Copyright (c) 2023 Ad Schellevis <ad@opnsense.org>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
"""
from .. import syslog_notice


class BaseAction:
    """ Action base class
    """

    def __init__(self, config_environment: dict, action_parameters: dict):
        """ setup default properties
        :param config_environment: dict environment to use
        :param action_parameters: dict of parameters belonging to this action
        :return:
        """
        self.config_environment = config_environment
        self.command = action_parameters.get('command', None)
        self.parameters = action_parameters.get('parameters', None)
        self.message = action_parameters.get('message', None)

    def _cmd_builder(self, parameters):
        """ basic (shell) script command builder, uses action command, expected parameter phrase and given parameters
        :param parameters: user provided parameters
        :return: command (+parameters) string
        """
        script_command = self.command
        if self.parameters is not None and type(self.parameters) == str:
            script_arguments = self.parameters
            if script_arguments.find('%s') > -1:
                # use command execution parameters in action parameter template
                # use quotes on parameters to prevent code injection
                if script_arguments.count('%s') > len(parameters):
                    # script command accepts more parameters than given, fill with empty parameters
                    for i in range(script_arguments.count('%s') - len(parameters)):
                        parameters.append("")
                elif len(parameters) > script_arguments.count('%s'):
                    # more parameters than expected, fail execution
                    raise TypeError('Parameter mismatch')

                # use single quotes to prevent command injection
                for i in range(len(parameters)):
                    parameters[i] = "'" + parameters[i].replace("'", "'\"'\"'") + "'"

                # safely print the argument list now
                script_arguments = script_arguments % tuple(parameters)

            return script_command + " " + script_arguments

        return script_command

    def execute(self, parameters, message_uuid):
        """ execute an action
        :param parameters: list of parameters
        :param message_uuid: unique message id
        :return:
        """
        # send-out syslog message
        if self.message is not None:
            log_param = []
            # make sure message items match input
            if self.message.count('%s') > 0 and len(parameters) > 0:
                log_param = parameters[0:self.message.count('%s')]
            if len(log_param) < self.message.count('%s'):
                for i in range(self.message.count('%s') - len(log_param)):
                    log_param.append('')

            syslog_notice('[%s] %s' % (message_uuid, self.message % tuple(log_param)))

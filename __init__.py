# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


import aiml
from os import listdir
from os.path import dirname, isfile
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class AimlFallback(FallbackSkill):
    def __init__(self):
        super(AimlFallback, self).__init__(name='AimlSkill')
        self.kernel = aiml.Kernel()
        # TODO read from config maybe?
        self.aiml_path = dirname(__file__) + "/aiml"
        self.brain_path = dirname(__file__) + "/bot_brain.brn"
        #self.load_brain()

    def load_brain(self):
        aimls = listdir(self.aiml_path)
        for aiml in aimls:
            self.kernel.bootstrap(learnFiles=self.aiml_path + "/" + aiml)

    def initialize(self):
        #self.register_fallback(self.handle_fallback, 99)
        pass

    def ask_brain(self, utterance):
        response = self.kernel.respond(utterance)
        return response

    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        self.speak(self.ask_brain(utterance))
        return True

    def shutdown(self):
        self.kernel.resetBrain() # Manual remove
        self.remove_fallback(self.handle_fallback)
        super(AimlFallback, self).shutdown()

def create_skill():
    return AimlFallback()

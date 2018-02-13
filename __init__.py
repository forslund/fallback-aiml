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
import os
from os import listdir, remove as remove_file
from os.path import dirname, isfile

from mycroft.api import DeviceApi
from mycroft.skills.core import FallbackSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger

__author__ = 'jarbas, nielstron'

LOGGER = getLogger(__name__)

def strTobool(v):
    """ Converts String to boolean representation
        From https://stackoverflow.com/questions/715417/
        converting-from-a-string-to-boolean-in-python/715468#715468
    """
    return v.lower() in ("yes", "true", "t", "1")

class AimlFallback(FallbackSkill):
    def __init__(self):
        super(AimlFallback, self).__init__(name='AimlSkill')
        self.kernel = aiml.Kernel()
        self.aiml_path = os.path.join(dirname(__file__),"aiml")
        self.brain_path = os.path.join(dirname(__file__),"bot_brain.brn")
        self.load_brain()

    def load_brain(self):
        if isfile(self.brain_path):
            self.kernel.bootstrap(brainFile = self.brain_path)
        else:
            aimls = listdir(self.aiml_path)
            for aiml in aimls:
                self.kernel.learn(os.path.join(self.aiml_path, aiml))

            device = DeviceApi().get()
            self.kernel.setBotPredicate("name", device["name"])
            self.kernel.saveBrain(self.brain_path)

    def initialize(self):
        self.register_fallback(self.handle_fallback, 40)

    @intent_handler(IntentBuilder("ResetMemoryIntent").require("Reset").require("Memory"))
    def handle_reset_brain(self, message):
        # delete the brain file and reset memory
        self.speak_dialog("reset.memory")
        self.kernel.resetBrain()
        remove_file(self.brain_path)
        # also reload base knowledge
        self.load_brain()

    def ask_brain(self, utterance):
        response = self.kernel.respond(utterance)
        # make a security copy once in a while
        # TODO maybe every 10th time?
        self.kernel.saveBrain(self.brain_path)
        return response

    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        answer = self.ask_brain(utterance)
        if answer != "":
            asked_question = False
            if answer.endswith("?"):
                asked_question = True
            self.speak(answer, expect_response=asked_question)
            return True
        return False

    def shutdown(self):
        #self.kernel.saveBrain(self.brain_path)
        #self.kernel.resetBrain() # Manual remove
        self.remove_fallback(self.handle_fallback)
        super(AimlFallback, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return AimlFallback()

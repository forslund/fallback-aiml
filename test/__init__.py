from unittest.mock import MagicMock, patch
from test.integrationtests.skills.skill_tester import SkillTest

def test_runner(skill, example, emitter, loader):

    # Get the skill object from the skill path
    s = [s for s in loader.skills if s and s.root_dir == skill]
    class MockSettings(dict):
        def store(self):
            pass
        def stop_polling(self):
            pass

    settings = MockSettings()
    settings['enabled'] = True
    s[0].settings = settings
    with patch(s[0].__module__ + '.remove_file') as mock_remove:
        ret = SkillTest(skill, example, emitter).run(loader)
    settings['enabled'] = 'false'
    return ret

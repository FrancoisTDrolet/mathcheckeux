import unittest

import mathcheckeux
import instancefactory


class TestTeam(unittest.TestCase):
    def test_team_all_players(self):
        team = mathcheckeux.Team()
        team.attackers.append(instancefactory.player())
        team.defenders += instancefactory.players(2)
        team.goalers += instancefactory.players(3)
        for player in team.attackers:
            self.assertIn(player, team.all_players())
        for player in team.defenders:
            self.assertIn(player, team.all_players())
        for player in team.goalers:
            self.assertIn(player, team.all_players())


if __name__ == '__main__':
    unittest.main()
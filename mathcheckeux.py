import json
import math

ALPHA = 1/400*math.log(10)


class Team:
    def __init__(self):
        self.attackers = []
        self.defenders = []
        self.goalers = []

    def has_player(self, player):
        return player in self.all_players()

    def all_players(self):
        return self.attackers + self.defenders + self.goalers

    def get_elo(self):
        team_elo = 0
        for player in self.all_players():
            team_elo += player.elo
        return team_elo/len(self.all_players())


class Match:
    def __init__(self, team_1, team_2, result):
        self.team_1 = team_1
        self.team_2 = team_2
        self.result = result

    def get_winner(self):
        if self.result == 1:
            return self.team_1
        elif self.result == 0:
            return self.team_2
        else:
            return None

    def get_loser(self):
        if self.result == 0:
            return self.team_1
        elif self.result == 1:
            return self.team_2
        else:
            return None

    def get_probability(self):
        if self.result == 0.5:
            probability = 1/(1+math.e**(ALPHA*(self.team_1.get_elo()-self.team_2.get_elo()))) * 1/(1+math.e**(ALPHA*(self.team_2.get_elo()-self.team_1.get_elo())))
            probability = probability**0.5
        else:
            probability = 1 / (1 + math.e ** (ALPHA * (self.get_loser().get_elo() - self.get_winner().get_elo())))
        return probability


class Player:
    def __init__(self, prenom, nom, id):
        self.prenom = prenom
        self.nom = nom
        self.id = id
        self.elo = 0
        self.self_win_connected = True
        self.matches = []
        self.update_step = 0

    def update_elo(self):
        if self.self_win_connected:
            self.elo += self.update_step

    def update_update_step(self, speed):
        self.update_step = 0
        for match in self.matches:
            if match.get_loser() is None:
                continue
            loser_elo = match.get_loser().get_elo()
            winner_elo = match.get_winner().get_elo()
            if self in match.get_loser().all_players():
                result = 0
                self_team_size = len(match.get_loser().all_players())
            elif self in match.get_winner().all_players():
                result = 1
                self_team_size = len(match.get_winner().all_players())
            else:
                continue
            self.update_step += -(1/(1+10**((loser_elo-winner_elo)/400))*(-1)**result*10**((loser_elo-winner_elo)/400)/self_team_size)*speed


class Connection_crawler:
    def __init__(self):
        self.computed_matches = set()

    def win_connection_crawl(self, present_player, target_player):
        for match in set(present_player.matches)-self.computed_matches:
            if match.get_winner() is None:
                self.computed_matches.add(match)
                continue
            if match.get_winner().has_player(present_player):
                self.computed_matches.add(match)
                if match.get_loser().has_player(target_player):
                    return True
                else:
                    for player in match.get_loser().all_players():
                        if self.win_connection_crawl(player, target_player):
                            return True
                        else:
                            continue
        return False

class Descent_runner:
    def __init__(self, league):
        self.league = league

    def _get_match_contribution_to_gradient_teamed(self, match):
        if match.get_winner() is None:
            ealpha1 = math.e ** (ALPHA * (match.team_1.get_elo() - match.team_2.get_elo()))
            ealpha2 = math.e ** (ALPHA * (match.team_2.get_elo() - match.team_1.get_elo()))
            contribution = ALPHA*(ealpha1/(1+ealpha1)-ealpha2/(1+ealpha2))/2
        else:
            ealpha = math.e**(ALPHA*(match.get_loser().get_elo()-match.get_winner().get_elo()))
            contribution = ALPHA*ealpha/(1+ealpha)
        return contribution

    def get_gradient(self):
        gradient = self.league.players.copy()
        p_factor = 1
        for key in gradient.keys():
            gradient[key] = 0

        for match in league.matches:
            match_contribution_to_gradient_teamed = self._get_match_contribution_to_gradient_teamed(match)
            p_factor *= match.get_probability()
            if match.get_winner() is None:
                for player in match.team_1.all_players():
                    gradient[player.id] -= match_contribution_to_gradient_teamed/len(match.team_1.all_players())
                for player in match.team_2.all_players():
                    gradient[player.id] += match_contribution_to_gradient_teamed/len(match.team_2.all_players())
            else:
                for player in match.get_winner().all_players():
                    gradient[player.id] += match_contribution_to_gradient_teamed/len(match.get_winner().all_players())
                for player in match.get_loser().all_players():
                    gradient[player.id] -= match_contribution_to_gradient_teamed/len(match.get_loser().all_players())

        for key in gradient.keys():
            gradient[key] = gradient[key]*p_factor

        return gradient

    def step(self):
        gradient = self.get_gradient()
        for key in gradient.keys():
            if gradient[key] > 0:
                self.league.players[key].elo += 1
            elif gradient[key] < 0:
                self.league.players[key].elo -= 1


class League:
    def __init__(self):
        self.players = {}
        self.matches = []

    def renorm(self):
        sum = 0
        n = 0
        for player in self.players:
            sum += player.elo
            n += 1
        mod = sum/n

        for player in self.players:
            player.elo -= mod

    def step(self, speed):
        for player in self.players.values():
            player.update_update_step(speed)
        for player in self.players.values():
            player.update_elo()
        self.renorm

    def update_connections(self):
        n = len(self.players.values())
        x = 0
        for player in self.players.values():
            x += 1
            print("{} sur {}".format(x, n))
            crawler = Connection_crawler()
            player.self_win_connected = crawler.win_connection_crawl(player, player)

    def update_elos(self, n, speed=1):
        for i in range(n):
            self.step(speed)

    def save_report(self, filename):
        with open(filename, "w") as file:
            for i in range(1000):
                if i in self.players.keys():
                    file.writelines(["{}:{}\n".format(str(i), str(self.players[i].elo))])

    def import_from_json(self, filepath):
        with open(filepath) as json_file:
            data = json.load(json_file)
            for season in data:
                for match_data in season:
                    team_1_score = match_data["foreCheckeuxScore"]
                    team_2_score = match_data["backCheckeuxScore"]
                    if team_1_score > team_2_score:
                        result = 1
                    elif team_2_score > team_1_score:
                        result = 0
                    else:
                        result = 0.5

                    team_1 = Team()
                    team_2 = Team()
                    match = Match(team_1, team_2, result)
                    self.matches.append(match)

                    for player_data in match_data["foreCheckeux"]:
                        player_id = player_data["id"]
                        player_position = player_data["position"]

                        if not(player_id in self.players):
                            player_prenom = player_data["prenom"]
                            player_nom = player_data["nom"]
                            player = Player(player_prenom, player_nom, player_id)
                            self.players[player_id] = player
                        else:
                            player = self.players[player_id]

                        player.matches.append(match)

                        if player_position == "A":
                            team_1.attackers.append(player)
                        elif player_position == "D":
                            team_1.defenders.append(player)
                        elif player_position == "G":
                            team_1.goalers.append(player)
                        else:
                            raise Exception("Player is assigned an undefined role")

                    for player_data in match_data["backCheckeux"]:
                        player_id = player_data["id"]
                        player_position = player_data["position"]

                        if not(player_id in self.players):
                            player_prenom = player_data["prenom"]
                            player_nom = player_data["nom"]
                            player = Player(player_prenom, player_nom, player_id)
                            self.players[player_id] = player
                        else:
                            player = self.players[player_id]

                        player.matches.append(match)

                        if player_position == "A":
                            team_2.attackers.append(player)
                        elif player_position == "D":
                            team_2.defenders.append(player)
                        elif player_position == "G":
                            team_2.goalers.append(player)
                        else:
                            raise Exception("Player is assigned an undefined role")


if __name__ == "__main__":
    league =League()
    league.import_from_json("./data/allstats.json")
    league.save_report("report{}.txt".format("init"))
    descent_runner = Descent_runner(league)
    for i in range(100):
        for j in range(1000):
            descent_runner.step()
        league.save_report("./results/report{}.txt".format(i))



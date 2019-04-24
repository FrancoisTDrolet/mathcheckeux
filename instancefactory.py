import mathcheckeux


last_player_id = 0


def new_player_id():
    global last_player_id
    last_player_id += 1
    return last_player_id


def player():
    id = new_player_id()
    return mathcheckeux.Player("prenom_of_player_{}".format(id), "nom_of_player_{}".format(id), id)


def players(n):
    r = []
    for i in range(n):
        r.append(player())
    return r
from mathcheckeux import League


def computeprior(league):
    n = 0
    sum = 0
    sum2 = 0
    for player in league.players.values():
        if abs(player.elo) != 100000 and len(player.matches) > 20:
            size = len(player.matches)
            n += size
            sum += player.elo*size
            sum2 += player.elo**2*size
    sigma_squared = sum2/n
    sample_variance = sigma_squared*n/(n-1)
    return sample_variance**0.5

if __name__ == "__main__":
    league = League()
    league.import_from_json("./data/allstats.json")
    league.apply_elo_from_file("./results/report24.txt")
    print(computeprior(league))
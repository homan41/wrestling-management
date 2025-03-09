class Wrestler:
    def __init__(self, name, seed, weight_class, score=0, all_american=False, medal=0, finalist=False, number_of_times_picked=0):
        self.name = name
        self.seed = seed
        self.weight_class = weight_class
        self.score = score
        self.all_american = all_american
        self.medal = medal
        self.finalist = finalist
        self.number_of_times_picked = number_of_times_picked

class Team:
    def __init__(self, name, score, tie_breaker_team, tie_breaker_score):
        self.name = name
        self.score = score
        self.tie_breaker_team = tie_breaker_team
        self.tie_breaker_score = tie_breaker_score
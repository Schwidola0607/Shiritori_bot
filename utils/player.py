class Player:
    """
    A class to represent a shiritori player.
    """
    def __init__(self, user, lives, time_left):
        self.id = user.id
        self.name = user.name
        self.score = 0
        self.lives = lives
        self.time_left = time_left
        self.inventory = []
        self.card_queue = []

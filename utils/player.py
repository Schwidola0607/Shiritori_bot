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
<<<<<<< HEAD
        self.inventory = []
        self.card_queue = []
=======
>>>>>>> e4d80e090b45cb3c5cdb0996a4e0f20e92b21f09

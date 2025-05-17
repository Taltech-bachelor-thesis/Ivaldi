import constants as const


class Corner:
    def __init__(self, location, canvas, r=5):
        self.canvas = canvas
        self.location = location
        self.r = r

        self.circle = self.canvas.create_oval(location[0] - self.r, location[1] - self.r, location[0] + self.r,
                                              location[1] + self.r, fill=const.WHITE, outline=const.WHITE)

    def move_to(self, location):
        self.canvas.coords(self.circle, location[0] - self.r, location[1] - self.r, location[0] + self.r,
                           location[1] + self.r)
        self.location = location

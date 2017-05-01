class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    __repr__ = __str__

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, num):
        return Vector2(num*self.x, num*self.y)

    def __divmod__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def get_length(self):
        from math import sqrt
        return sqrt(self.x**2 + self.y**2)

    def normolize(self):
        length = self.get_length()
        return Vector2(self.x/length, self.y/length)

    @classmethod
    def from_points(cls, P1, P2):
        return cls(P2[0] - P1[0], P2[1] - P1[1])

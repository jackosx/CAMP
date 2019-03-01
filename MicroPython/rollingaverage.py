# A fast rolling average class
#
# Get the average by using the .avg property
# Add a new value with the .update method

class RollingAverage(object):
    """docstring for RollingAverage."""
    def __init__(self, n, init_val=0):
        self.vals = [init_val for i in range(n)]
        self.n    = n
        self.i    = 0
        self.avg  = init_val

    def update(self, new_val):
        self.avg = max(self.avg - self.vals[self.i]/self.n, 0)
        self.avg = self.avg + new_val/self.n
        self.vals[self.i] = new_val
        self.i = (self.i + 1) % self.n


class RollingStats(RollingAverage):
        def __init__(self, n, init_val=0):
            RollingAverage.__init__(self, n, init_val)
            self.devs_sq = RollingAverage(n)

        def update(self, new_val):
            RollingAverage.update(self, new_val)
            dev = new_val - self.avg
            self.devs_sq.update(dev * dev)

        def pseudo_std_dev(self):
            return self.devs_sq.avg ** .5

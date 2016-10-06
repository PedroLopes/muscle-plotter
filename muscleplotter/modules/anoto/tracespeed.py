import time

def calculate_distance(point_one, point_two):
    x1, y1 = point_one
    x2, y2 = point_two
    horizontal_distance = x1 - x2
    vertical_distance = y1 - y2
    distance = (horizontal_distance**2 + vertical_distance**2) ** 0.5
    return (distance, horizontal_distance, vertical_distance)


class TraceSpeed(object):

    def __init__(self):
        self.x = []
        self.y = []
        self.time = []
        self.speed = []
        self.speed_x = []
        self.speed_y = []

        self.time_last_update = 0

    def get_speed_vector(self):
        speed = self.get_vector()
        return {'x': speed[0], 'y': speed[1]}

    def get_vector(self):
        weights = [2, 1, 1]
        data_x = self.speed_x[-len(weights) - 1:]
        data_y = self.speed_y[-len(weights) - 1:]
        if len(data_x) > len(weights):
            data_x = sum(w * data_x[-i] / sum(weights)
                         for i, w in enumerate(weights, start=1))
            data_y = sum(w * data_y[-i] / sum(weights)
                         for i, w in enumerate(weights, start=1))
            if self._sample_fresh():
                return (data_x, data_y)
        else:
            return (0, 0)

    def feed_data(self, x, y, time_stamp):
        self.time_last_update = time.time()
        self.x.append(x)
        self.y.append(y)
        self.time.append(time_stamp)
        self._calculate_speed()

    def reset_measure(self):
        self.__init__()

    def _sample_fresh(self):
        if time.time() - self.time_last_update > 300:
            return False
        else:
            return True

    def _calculate_speed(self):

        try:
            i = 1
            while self.time[-1] == self.time[-1 - i]:
                i += 1
            point_one = (self.x[-1], self.y[-1])
            point_two = (self.x[-1 - i], self.y[-1 - i])
            distance, distance_x, distance_y = \
                calculate_distance(point_one, point_two)
            time = float(self.time[-1] - self.time[-1 - i])
            if time < 0:
                time += 1000
            self.speed.append(distance / time)
            self.speed_x.append(distance_x / time)
            self.speed_y.append(distance_y / time)

        except:
            pass

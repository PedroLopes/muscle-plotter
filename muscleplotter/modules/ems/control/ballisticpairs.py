import sys
if (sys.version_info < (3, 0)):
        import ConfigParser
else:
        import configparser


class BallisticPairs(object):
    """Determines appropriate ballistic pairs based on calibration results
    """

    def __init__(self, user='doga'):
        super(BallisticPairs, self).__init__()
        self.params = self.read_params_from_configs(user)

    def get_amp(self, channel):
        if channel == 1:
            return self.params['left_amp']
        elif channel == 2:
            return self.params['right_amp']
        elif channel == 3:
            return self.params['penup_amp']
        elif channel == 4:
            return self.params['brake_amp']

    def get_duty(self, channel):
        if channel == 3:
            return self.params['penup_duty']
        if channel == 4:
            return self.params['brake_duty']

    def get_pair(self, slope):
        """ Map slope to pair determined pair
        """
        if slope == 'b':
            code = 'b'
        elif slope > 2:
            code = 3
        elif slope > 0.5:
            code = 2
        elif slope > 0.15:
            code = 1
        elif slope > -0.15:
            code = 0
        elif slope > -0.5:
            code = -1
        elif slope > -2:
            code = -2
        else:
            code = -3
        pair = self.params[code]
        return [code, pair]

    def read_params_from_configs(self, user):

        if (sys.version_info < (3, 0)):
                config_user = ConfigParser.ConfigParser()
        else:
                config_user = confiparser.ConfigParser()
        user_ems_file = 'configuration/user_parameters/' + str(user) + '.ems'
        config_user.read(user_ems_file)
        params = {}

        params['left_amp'] = config_user.getint('Left', 'amp')
        params['right_amp'] = config_user.getint('Right', 'amp')
        params['penup_amp'] = config_user.getint('Up', 'amp')
        params['penup_duty'] = config_user.getint('Up', 'duty')
        params['brake_amp'] = config_user.getint('Brake', 'amp')
        params['brake_duty'] = config_user.getint('Brake', 'duty')

        params[3] = (config_user.getint('Right', 'high_left'),
                     config_user.getint('Right', 'high_right'))
        params[2] = (config_user.getint('Right', 'mid_left'),
                     config_user.getint('Right', 'mid_right'))
        params[1] = (config_user.getint('Right', 'low_left'),
                     config_user.getint('Right', 'low_right'))

        params[-3] = (config_user.getint('Left', 'high_left'),
                      config_user.getint('Left', 'high_right'))
        params[-2] = (config_user.getint('Left', 'mid_left'),
                      config_user.getint('Left', 'mid_right'))
        params[-1] = (config_user.getint('Left', 'low_left'),
                      config_user.getint('Left', 'low_right'))

        params[0] = (config_user.getint('Brake', 'low_left'),
                     config_user.getint('Brake', 'low_right'))
        params['b'] = (config_user.getint('Brake', 'high_left'),
                       config_user.getint('Brake', 'high_right'))

        return params

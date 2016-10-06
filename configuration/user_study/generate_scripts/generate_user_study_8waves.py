from __future__ import division
import random
import ConfigParser
import sys
import argparse
import time
import datetime

parser = argparse.ArgumentParser(description='Generate data/functions for plotting')

parser.add_argument("-o", '--output', action="store", default="userstudy8.config", dest='filename', help="Provide output filename [fallback is userstudy8.config]")

#(299.3 / 10) (anoto pixels to cms)
centimeter = 299 

arguments = parser.parse_args()
size_of_array = 8
period = [0] * size_of_array
amplitude= [0] * size_of_array
a = [0] * size_of_array
b = [0] * size_of_array
c = [0] * size_of_array
d = [0] * size_of_array
phase_offset1 = [0] * size_of_array
phase_offset2 = [0] * size_of_array

def make_function(level,i):
    if level == "triangle":
        period[i] = -1 #-1 means triangle wave
        return
    if level == "horizontal":
        period[i] = -2 #-2 means wave with horizontal features
        return
    if level == "easy1":
        period_in_cms = 24
        period[i] = random.randint(int(centimeter * period_in_cms) - int(centimeter * (1/3)), centimeter * period_in_cms + int(centimeter * (1/3)))
        amplitude[i] = random.randint(400,500)
    if level == "easy2":
        period_in_cms = 18
        period[i] = random.randint(int(centimeter * period_in_cms) - int(centimeter * (1/3)), centimeter * period_in_cms + int(centimeter * (1/3)))
        amplitude[i] = random.randint(400,500)
    if level == "medium1":
        period_in_cms = 12 
        period[i] = random.randint(int(centimeter * period_in_cms) - int(centimeter * (1/3)), centimeter * period_in_cms + int(centimeter * (1/3)))
        phase_offset1[i] = random.randint(int(period[i]/3), int(period[i]/2))
        amplitude[i] = random.randint(300,400)
        a[i] = random.randrange(-2, 2) #modulates amplitude of 1st partial
        b[i] = random.randrange(4, 8) 
    if level == "medium2" or level == "hard1" or level == "hard2":
        period_in_cms = 9 
        period[i] = random.randint(int(centimeter * period_in_cms) - int(centimeter * (1/3)), centimeter * period_in_cms + int(centimeter * (1/3)))
        phase_offset1[i] = random.randint(int(period[i]/3), int(period[i]/2))
        amplitude[i] = random.randint(300,400)
        a[i] = random.randrange(-2, 2) #modulates amplitude of 1st partial
        b[i] = random.randrange(4, 8) 
    if level == "hard1" or level == "hard2":
        amplitude[i] = random.randint(200,300)
        a[i] = random.randrange(-2, 2) #modulates amplitude of 1st partial
        b[i] = random.randrange(4, 8) 
    if level == "hard1": 
        period_in_cms = 4 
        period[i] = random.randint(int(centimeter * period_in_cms), centimeter * period_in_cms + int(centimeter * (1/3)))
        c[i] = random.randrange(-2, 2) #modulates amplitude of 2nd partial
        d[i] = random.randrange(4, 8) 
    if level == "hard2": 
        period_in_cms = 2 
        period[i] = random.randint(int(centimeter * period_in_cms), centimeter * period_in_cms + int(centimeter * (1/3)))
        phase_offset2[i] = random.randint(int(period[i]/3), int(period[i]/2))
        c[i] = random.randrange(-2, 2) #modulates amplitude of 2nd partial
        d[i] = random.randrange(4, 8) 

make_function("easy1",0)
make_function("easy2",1)
make_function("medium1",2)
make_function("medium2",3)
make_function("hard1",4)
make_function("hard2",5)
make_function("triangle",6)
make_function("horizontal",7)

#write to file
Config = ConfigParser.ConfigParser()
functions = open(arguments.filename,'w')
Config.add_section('sinewaves')
Config.set('sinewaves','period', period)
Config.set('sinewaves','amplitude', amplitude)
Config.set('sinewaves','a',a)
Config.set('sinewaves','b',b)
Config.set('sinewaves','c',c)
Config.set('sinewaves','d',d)
Config.set('sinewaves','phase_offset1',phase_offset1)
Config.set('sinewaves','phase_offset2',phase_offset2)
Config.set('sinewaves','level',"user_study")
Config.add_section('features')
Config.set('features','feature_width',1500)
Config.add_section('metadata')
Config.set('metadata','timestamp',str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
Config.write(functions)
functions.close()


#from target
            #period = random.randint(1600, 2400)
            #amplitude = random.randint(200, 400)
            #a = random.randrange(-3, 3)
            #b = random.randrange(2, 4)
            #c = random.randrange(3, 6)
            #d = random.randrange(2, 4)

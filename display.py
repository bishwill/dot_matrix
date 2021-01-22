from luma.core.render import canvas
from PIL import Image, ImageDraw
from PIL.ImageFont import truetype
from time import strftime, localtime, sleep
from luma.oled.device import ssd1322
from luma.core.interface.serial import spi
from requests import get
from os import path
from json import load

config = open(path.dirname(path.realpath(__file__)) + '/config.txt', 'r')
settings = load(config)
config.close() 

x = 270
data = []
points = ''
calling_points_scroll_speed = settings['calling_points_scroll_speed']
card_time = settings['card_switching_speed']
time_font = path.dirname(path.realpath(__file__)) + '/time.ttf'
text_font = path.dirname(path.realpath(__file__)) + '/text.ttf'

if settings['station_filter'] == 'none':
    url = 'https://huxley2.azurewebsites.net/departures/' + settings['station_crs'] + '/?accessToken=' + settings['api_key'] + '&numServices=3'
else:
    url = 'https://huxley2.azurewebsites.net/departures/' + settings['station_crs'] + '/?accessToken=' + settings['api_key'] + '&numServices=3&filterStation=' + settings['station_filter']

class cards():
    def __init__(self, sch, plat, dest, exp, call, op):
        self.sch = sch
        self.plat = plat
        self.dest = dest
        self.exp = exp
        self.call = call
        self.op = op
        self.colour = 'yellow'
        self.font = truetype(path.dirname(path.realpath(__file__)) + '/text.ttf', 14)

    def generate_card(self):
        if len(self.plat + ' ' + self.dest) <= 14:
            return (self.sch + ' ' + self.plat + ' ' + self.dest + (' ' * int(15 - len(self.plat + ' ' + self.dest))) + self.exp)
        else:
            return (self.sch + ' ' + (self.plat + ' ' + self.dest)[0:14] + ' ' + self.exp)

def get_data():
    r = get(url)
    trains = r.json()['trainServices']
    data.clear()
    if trains != None:
        for i in trains:
            if i['platform'] != None:
                data.append(cards(i['std'], i['platform'], i['destination'][0]['locationName'], i['etd'], '', i['operator']))
            else:
                data.append(cards(i['std'], ' ', i['destination'][0]['locationName'], i['etd'], '', i['operator']))
        points = ''
        for i in trains[0]['subsequentCallingPointsList'][0]['subsequentCallingPoints']:
            points += i['locationName']
            points += ' ('
            if i['et'] == 'On time' or i['et'] == None:
                points += i['st']
            else:
                points += i['et']
            points += '), '
        points = points[:-2] + '   (' + data[0].op + ')'
        data[0].call = points

def scroller():
    global x
    if abs(x) < (truetype(text_font, 14).getsize(data[0].call)[0]):
        x -= calling_points_scroll_speed
    else:
        x = 270

def image_1():
    scroller()
    current_time = strftime("%H:%M:%S", localtime())
    im = Image.new('RGB', (256, 64))
    draw =ImageDraw.Draw(im)
    draw.text((0, 0), '1st', fill = 'yellow', font = data[0].font)
    draw.text((0, 30), '2nd', fill = 'yellow', font = data[0].font)
    draw.text((30, 0), data[0].generate_card(), fill = 'yellow', font = data[0].font)
    draw.text((x, 15), data[0].call, fill = 'yellow', font = data[0].font)
    draw.text((30, 30), data[1].generate_card(), fill = 'yellow', font = data[1].font)
    draw.text((92, 48), current_time, fill = 'yellow', font = truetype(time_font, 17))
    with canvas(device, background = im) as draw:
        pass

def image_2():
    scroller()
    current_time = strftime("%H:%M:%S", localtime())
    im = Image.new('RGB', (256, 64))
    draw =ImageDraw.Draw(im)
    draw.text((0, 0), '1st', fill = 'yellow', font = data[0].font)
    draw.text((0, 30), '3rd', fill = 'yellow', font = data[0].font)
    draw.text((30, 0), data[0].generate_card(), fill = 'yellow', font = data[0].font)
    draw.text((x, 15), data[0].call, fill = 'yellow', font = data[0].font)
    draw.text((30, 30), data[2].generate_card(), fill = 'yellow', font = data[2].font)
    draw.text((92, 48), current_time, fill = 'yellow', font = truetype(time_font, 17))
    with canvas(device, background = im) as draw:
        pass

def image_3():
    scroller()
    current_time = strftime("%H:%M:%S", localtime())
    im = Image.new('RGB', (256, 64))
    draw =ImageDraw.Draw(im)
    draw.text((0, 0), '1st', fill = 'yellow', font = data[0].font)
    draw.text((30, 0), data[0].generate_card(), fill = 'yellow', font = data[0].font)
    draw.text((x, 15), data[0].call, fill = 'yellow', font = data[0].font)
    draw.text((92, 48), current_time, fill = 'yellow', font = truetype(time_font, 17))
    with canvas(device, background = im) as draw:
        pass

def image_4():
    current_time = strftime("%H:%M:%S", localtime())
    im = Image.new('RGB', (256, 64))
    draw =ImageDraw.Draw(im)
    draw.text((13, 14), current_time, fill = 'yellow', font = truetype(time_font, 50))
    with canvas(device, background = im) as draw:
        pass

get_data()
serial = spi(port=0, device=0)
device = ssd1322(serial, rotate = 2)

while True:
    if len(data) == 3:
        for i in range(card_time):
            image_1()
        for i in range(card_time):
            image_2()
    elif len(data) == 2:
        for i in range(2 * card_time):
            image_1()
    elif len(data) == 1:
        for i in range(2 * card_time):
            image_3()
    elif len(data) == 0:
        for i in range(2 * card_time):
            image_4()
    try:
        get_data()
    except:
        pass

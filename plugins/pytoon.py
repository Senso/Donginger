from wand.image import Image
from wand.drawing import Drawing
from wand.display import display
from wand.color import Color
from os import listdir, stat
from random import choice, randrange, shuffle
import textwrap
import time
import re
from collections import OrderedDict

from plugin import Plugin

draw = Drawing()

talk_pat = re.compile("(.+) (says|asks|exclaims), \"(.+)\"")
talk_to_pat = re.compile("(.+) \[to (.+)\]\:(.+)")
irc_pat = re.compile("\<(.+)\> (.+)")
net_pat = re.compile("\[.+\] (.+) (says|asks|exclaims), \"(.+)\"")

class Panel:
    def __init__(self, background=None, chars=None, scene=None, doublewide=False):
        if background is None:
            background = randomize_background()
        self.background = Image(filename=background)

        self.doublewide = doublewide
        if self.doublewide is True:
            self.background.crop(0, 0, self.background.height, self.background.height)
            self.background.transform(resize='1000x500^')
            self.background.transform('1000x500')
        else:
            self.background.crop(0, 0, self.background.height, self.background.height)
            self.background.transform(resize='500')
            self.background.transform(resize='500x500')

        self.chars = chars
        self.scene = scene
        draw.font = 'plugins/py_toon/fonts/DejaVuSansMono.ttf'
        draw.font_size = 15
        draw.text_kerning = 1
        draw.text_alignment = 'left'

    def setup(self):
        self.add_characters()
        self.speech_bubbles()
        self.background = self.render()
        return self.background
        
    def speech_bubbles(self):
        curx = 15
        cury = 15

        for action in self.scene[1]:

            actor = action[0]
            line = action[1]
            if not line:
                continue
            line = textwrap.fill(line, 20)

            metrics = draw.get_font_metrics(self.background, line, True)

            ctext = int(metrics.text_width / 2.0)
            draw.fill_color = Color('white')
            draw.stroke_color = Color('black')
            draw.stroke_width = 1.0

            char_center = actor.img.x + int(actor.img.width / 2.0)
            text_center = int(metrics.text_width / 2.0)

            if len(self.scene[1]) == 1:
                cury = randrange(50, 125 + 20)
            else:
                max_y = cury + 20
                if max_y < 1: max_y = 245
                cury = randrange(cury, max_y)
            curx = char_center - text_center
            if curx < 25: curx = 25
            if curx > self.background.width - int(metrics.text_width):
                curx = self.background.width - int(metrics.text_width) - 15

            curx = int(curx)
            cury = int(cury)

            if line.strip() != '':
                draw.round_rectangle(curx - 10, cury, curx + metrics.text_width + 10, cury + metrics.text_height + 5, 5, 5)

                draw.fill_color = Color('black')

                draw.text(curx, cury + 15, line)
                curx += metrics.text_width + 10
                cury += int(metrics.text_height + 10)

    def add_characters(self):
        parts = self.background.width / len(self.chars.keys())

        curx = 0
        cury = 0

        char_count = 0
        for i in self.chars.items():
            char = i[1]

            if self.doublewide is True:
                #char.img.resize(175, 175)
                char.img.transform(resize='x150')
            else:
                char.img.resize(125, 125)

            ### contain the character in this "box"
            char_pos = curx + parts - char.img.width
            print 'char_pos:', char_pos
            if char_pos < 1:
                return 'Not enough space to fit everybody.'
            curx = randrange(curx, char_pos)

            cury = self.background.height - char.img.height

            char.img.x = curx
            char.img.y = cury

            char_count += 1

            curx = parts * char_count

            if char_count == 2:
                char.flip()
            self.background.composite(char.img, char.img.x, char.img.y)
            draw(self.background)
            if char_count == 2:
                ### unflip
                char.flip()

    def render(self):
        if self.doublewide is False:
            self.background.border(Color('white'), 5, 5)
        else:
            self.background.border(Color('white'), 10, 10)
        draw(self.background)
        draw.clear()
        return self.background

    
class Character:
    def __init__(self, name, text):
        self.avatar = None
        self.name = name
        self.text = [text]
        self.x = 0
        self.y = 0

    def set_avatar(self, file):
        self.avatar = file
        self.img = Image(filename='/home/donginger/donginger/development/plugins/py_toon/characters/' + self.avatar)

    def place(self):
        self.img.x = self.x
        self.img.y = self.y

    def flip(self):
        self.img.flop()


def dialogue_parser(diag):
    dialogue = diag
    scenes = OrderedDict()
    actors = OrderedDict()

    cur_scene = 1
    prev_actor = None
    talk_to = None

    for line in dialogue:
        ee = re.search(net_pat, line)
        ff = re.search(talk_pat, line)
        gg = re.search(talk_to_pat, line)
        hh = re.search(irc_pat, line)
        if ee:
            actor = ee.group(1)
            text = ee.group(3)
        elif ff:
            actor = ff.group(1)
            text = ff.group(3)
        elif gg:
            actor = gg.group(1)
            talk_to = gg.group(2)
            text = gg.group(3)
        elif hh:
            actor = hh.group(1)
            text = hh.group(2)
        else:
            continue
        
        text = text.strip()

        if actor not in actors.keys():
            actors[actor] = Character(actor, text)
        else:
            actors[actor].text.append(text)

        if talk_to is not None:
            if talk_to not in actors.keys():
                actors[talk_to] = Character(talk_to, '')
    
        if prev_actor == actor:
            # NEW SCENE
            cur_scene += 1
            scenes[cur_scene] = [[actors[actor], text]]
        elif cur_scene not in scenes.keys():
            # Create new scene, add actor
            scenes[cur_scene] = [[actors[actor], text]]
        elif actor in (a[0].name for a in scenes[cur_scene]):
            # Already appearing in the scene -> new scene
            cur_scene += 1
            scenes[cur_scene] = [[actors[actor], text]]
        else:
            # Add to current scene
            scenes[cur_scene].append([actors[actor], text])

        prev_actor = actor

    if len(scenes.keys()) % 2 == 0 and len(scenes.keys()) != 0:
        ### 40% chance of adding an extra panel with no dialogue
        ### If that doesn't happen, the last panel will be doublewide
        if randrange(1,100) < 40:
            scenes[cur_scene + 1] = [[actors[i], ''] for i in actors.keys()]

    return scenes, actors

def randomize_background():
    files = listdir('/home/donginger/donginger/development/plugins/py_toon/backgrounds/')
    return '/home/donginger/donginger/development/plugins/py_toon/backgrounds/' + choice(files)

def randomize_avatards(x):
    files = listdir('/home/donginger/donginger/development/plugins/py_toon/characters')
    avatards = []
    for x in range(0, x):
        avatards.append(choice(files))
    return avatards

def make_filename(doge=None):
    today = time.strftime("%Y%m%d", time.gmtime(time.time()))
    counter = 1
    while True:
        if doge is True:
            ff = "/home/donginger/webroot/blab/static/doge/%s_%s.png" % (today, counter)
        else:
            ff = "/home/donginger/webroot/blab/static/%s_%s.png" % (today, counter)
        try:
            stat(ff)
            counter += 1
        except OSError:
            break
        
    return "%s_%s.png" % (today, counter)

def build_strip(all_panels, title):
    ### Merge all panels into a trip
    total_width = 0
    total_height = 0

    pc = 0
    for x in all_panels:
        pc += 1
        if pc == 1:
            total_width = x.width
            total_height = x.height
        elif pc % 2 == 0:
            total_width += x.width
        else:
            total_height += x.height

    with Image(width=total_width, height=total_height, background=Color('white')) as main_img:
        curx = 0
        cury = 0

        panel_count = 0
        for pan in all_panels:
            panel_count += 1
            if panel_count == 1:
                curx = 0
                cury = 0
            elif panel_count % 2 == 0:
                curx = pan.width
            else:
                curx = 0
                cury += pan.height

            main_img.composite(pan, curx, cury)

            draw(main_img)
        main_img.format = 'png'
        url = make_filename()
        main_img.save(filename="/home/donginger/webroot/blab/static/%s" % url)
        draw.clear()
        return url

def make_doge(dialogue):
    p = Panel(background='/home/donginger/webroot/blab/doge.jpg')
    p.background.resize(500, 500)
    draw.font_size = 18
    draw.font = '/home/donginger/ComicRelief.ttf'
    draw.stroke_color = Color('black')
    draw.stroke_width = 0.5
    cols = ('red', 'blue', 'magenta', 'green', 'yellow', 'crimson', 'deeppink', 'dodgerblue', 'springgreen',
            'lime', 'darkorange', 'orangered')
    y_used = []
    for i in dialogue:
        i = i.strip()
        if not i:
            continue
        draw.fill_color = Color(choice(cols))
        draw.stroke_color = Color('black')
        draw.stroke_width = 0.5
        mets = draw.get_font_metrics(p.background, i, True)
        randx = randrange(0, int(p.background.width) - int(mets.text_width))

        # so that text doesn't go out of the pic
#        if randx > p.background.width - int(mets.text_width):
#            randx -= p.background.width - int(mets.text_width) - randrange(30, 60)

        # to avoid text overlapping
        checking = True
        while checking is True:
            reroll = False
            max_h = p.background.height - 40
            if max_h < 1: max_h = 40
            randy = randrange(0, p.background.height - 40)
            for yy in y_used:
                if randy > yy - 10 and randy < yy + 10:
                    reroll = True
            if reroll is False:
                checking = False
                y_used.append(randy)
                break

        draw.text(randx, randy, i)
        draw(p.background)
    url = make_filename(True)
    p.background.format = 'png'
    p.background.save(filename="/home/donginger/webroot/blab/static/doge/%s" % url)
    draw.clear()
    return url


class Pytoon(Plugin):
    def __init__(self, dong, conf):
        super(Pytoon, self).__init__(dong, conf)

    def main(self, caller, dialogue):
        try:
            return self.alt_main(caller, dialogue)
        except Exception as e:
            print 'Error:', e
            return 'You fucked that up, champ!'

    def alt_main(self, caller, dialogue):
	    #pick one background for the whole strip
        bg = randomize_background()

		# First line is the @paste-to start marker
        dialogue = dialogue[1:]
        title = None
        if dialogue[0].find('title:') > -1:
            title = dialogue[0].replace('title:', '')
            dialogue = dialogue[1:]

        scenes, actors = dialogue_parser(dialogue)

        ### DOGE
        # scenes and actors are both empty
        if scenes == OrderedDict() and actors == OrderedDict():
            shibe = make_doge(dialogue)
            return "http://dejablabspace.com/static/doge/%s" % shibe

        # Assign a random avatar to each character
        tards = listdir('/home/donginger/donginger/development/plugins/py_toon/characters/')
        shuffle(tards)
        for a in actors.values():
            # These 3 lines will standardize the aliases vs real chillmin names
            for x in self.conf["aliases"].items():
                if a.name.lower() in x[1]:
                    a.name = x[0].capitalize()

            if 'r_' + a.name.lower() + '.png' in tards:
                a.set_avatar(tards.pop(tards.index('r_' + a.name.lower() + '.png')))
            else:
                nt = []
                for t in tards:
                    if t[:2] != 'r_':
                        nt.append(t)
                shuffle(nt)
                a.set_avatar(nt.pop())
            a.place()

        # SETUP A SCENE
       	all_panels = []

        firstb = Image(width=500, height=500, background=Color('white'))
        draw.font = 'plugins/py_toon/fonts/BalsamiqSansBold.ttf'
        draw.font_size = 18
        draw.text_alignment = 'left'
        draw.fill_color = Color('black')

        texty = 50
        if title is None:
            #generate a random title from a dialogue line
            while True:
                s = choice(scenes.keys())
                st = scenes[s]
                rline = st[0][1]
                words = rline.split(' ')
                if words != [''] and len(words) >= 1:
                    break
            title_tup = words[:randrange(4,5)]
            title = ' '.join(title_tup)
            if title[-1] in (',',':','-'):
                title = title[:-1]

        tmet = draw.get_font_metrics(firstb, title, True)

        tx = 250 - int(tmet.text_width / 2)

        draw.text(tx, texty, textwrap.fill(title, 40))

        texty += 40
        draw.font_size = 16
        draw.text(30, texty, "With:")
        texty += 35
        draw.font = 'plugins/py_toon/fonts/DejaVuSansMono.ttf'
        draw.font_size = 15

        for peep in actors.values():
            with peep.img.clone() as av:
                av.resize(60, 60)
                av.x = 10
                av.y = texty
                firstb.composite(av, av.x, av.y)
                draw.text(av.width + 25, texty + 32, peep.name)
                texty += 65
       
        firstb.border(Color('white'), 10, 10) 
        draw(firstb)
        all_panels = [firstb]
        draw.clear()
        for scene in scenes.items():
            ### Decide if we need a double-wide bottom panel
            last_scene_id = scenes.keys()[-1:]
            if scene[0] == last_scene_id[0] and scene[0] > 1 and len(scenes) % 2 == 0:
                panel = Panel(background=bg, chars=actors, scene=scene, doublewide=True)
            else:
                panel = Panel(background=bg, chars=actors, scene=scene)
            all_panels.append(panel.setup())
        part = build_strip(all_panels, title)
        url = "http://dejablabspace.com/static/%s" % part
        return url

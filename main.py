import os
import pickle
import time
import sys
import pygame as pg
from pygame._sdl2.video import Window
from random import *
from C_librarianthefirstsecondandlast import *
from copy import *

pg.init()

# loading options
options = open("options.txt", "r")
key_bindings = {}
window_name = "Placeholder"

for line in options.readlines():
    if ":" in line:
        line = line.replace("\n", "").split(":")
    
        if line[0] == "fullscreen":
            global fullscreen
            fullscreen = bool(int(line[1]))
            
        elif line[0] == "framerate":
            global framerate_text
            global framerate
            temp = line[1]
            if temp == "VSync":
                framerate = pg.display.get_desktop_refresh_rates()[0]
                framerate_text = "Vsync"
            elif temp == "Unlimited":
                framerate = pg.display.get_desktop_refresh_rates()[0]*3
                framerate_text = "Unlimited"
            else:
                framerate = int(line[1])
                framerate_text = str(framerate)
        
        elif line[0] == "master_volume":
            global master_volume
            master_volume = float(line[1])/10
            
        elif line[0] == "music_volume":
            global music_volume
            music_volume = float(line[1])/10
        
        elif line[0] == "sfx_volume":
            global sfx_volume
            sfx_volume = float(line[1])/10
            
        elif line[0] == "resolution":
            resolution = line[1]
            screen_width, screen_height = int(line[1].split("X")[0]),int(line[1].split("X")[1])
            
        else:
            if "mouse_button" in line[1]:
                key_bindings[line[0]] = "mouse_button-"+line[1][-1]
            else:
                key_bindings[line[0]] = pg.key.key_code(line[1])

options.close()

# loading images
player_images = {}
platform_images = {}
power_images = {}
other_images = {}
for image in os.walk("assets\\images"):
    
    if image[0] == "assets\\images\\player":
        for frame in image[2]:
            player_images[frame.removesuffix(".png")] = pg.image.load("assets\\images\\player\\"+frame)
    
    elif image[0] == "assets\\images\\platforms":
        for platform in image[2]:
            if len(platform.split("_")) > 1:
                root = platform.split("_")[0]
                frame = platform.removesuffix(".png").split("_")[1]
                
                try:
                    platform_images[root][frame] = pg.image.load("assets\\images\\platforms\\"+platform)
                except KeyError:
                    platform_images[root] = {}
                    platform_images[root][frame] = pg.image.load("assets\\images\\platforms\\"+platform)
            else:
                platform_images[platform.removesuffix(".png")] = pg.image.load("assets\\images\\platforms\\"+platform)
    
    elif image[0] == "assets\\images\\power_ups":        
        for power in image[2]:
            if len(power.split("_")) > 1:
                root = power.split("_")[0]
                frame = power.removesuffix(".png").split("_")[1]
                
                try:
                    power_images[root][frame] = pg.image.load("assets\\images\\power_ups\\"+power)
                except KeyError:
                    power_images[root] = {}
                    power_images[root][frame] = pg.image.load("assets\\images\\power_ups\\"+power)
            else:
                power_images[power.removesuffix(".png")] = pg.image.load("assets\\images\\power_ups\\"+power)
         
        
        for root in image[1]:
            for frames in os.walk("assets\\images\\power_ups\\"+root):
                frames = frames[2]
                for frame in frames:
                    try:
                        power_images[root][frame.removesuffix(".png")] = pg.image.load("assets\\images\\power_ups\\"+root+"\\"+frame)
                    except KeyError:
                        power_images[root] = {}
                        power_images[root][frame.removesuffix(".png")] = pg.image.load("assets\\images\\power_ups\\"+root+"\\"+frame)
    else:
        if image[0].count("\\") >= 2:
            pass
        else:
            for o_i in image[2]:
                other_images[o_i.removesuffix(".png")] = pg.image.load("assets\\images\\"+o_i)
            
other_sounds = {}
player_sounds = {}
platform_sounds = {}
music = {}
for sound in os.walk("assets\\sounds"):
    
    if sound[0] == "assets\\sounds\\player":
        for audio in sound[2]:
            player_sounds[audio.removesuffix(".mp3")] = pg.mixer.Sound("assets\\sounds\\player\\"+audio)
    
    elif sound[0] == "assets\\sounds\\platforms":
        for audio in sound[2]:
            player_sounds[audio.removesuffix(".mp3")] = pg.mixer.Sound("assets\\sounds\\platforms\\"+audio)
    
    elif sound[0] == "assets\\sounds\\music":
        for audio in sound[2]:
            if len(audio.split("_")) > 1:
                root = audio.split("_")[0]
                frame = audio.removesuffix(".mp3").split("_")[1]
                
                try:
                    music[root][frame] = pg.mixer.Sound("assets\\sounds\\music\\"+audio)
                except KeyError:
                    music[root] = {}
                    music[root][frame] = pg.mixer.Sound("assets\\sounds\\music\\"+audio)
            else:
                music[power.removesuffix(".png")] = pg.mixer.Sound("assets\\sounds\\music\\"+audio)
        
    else:
        for o_s in sound[2]:
            
            other_sounds[o_s.removesuffix(".mp3")] = pg.mixer.Sound("assets\\sounds\\"+o_s)
 
# Defining screen size
if fullscreen == False:
    screen_width, screen_height = screen_width/1.5, screen_height/1.5
else: 
    temp = pg.display.Info()
    screen_width, screen_height = temp.current_w, temp.current_h
    
# Finding size in case of fullscreen
screen = Window(window_name, [screen_width, screen_height])

d_time = 1/60

clock = pg.time.Clock()

#1920 offset_ratio 1080, 360 offset_ratio 800, 1366 offset_ratio 768, 1536 offset_ratio 864, 390 offset_ratio 844, 393 offset_ratio 873
resolution_presets = ["1920X1080", "1360X770", "1540X860", "700X700", "1080X1080"]

cont = False
key_names = {}

for key in key_bindings:
    if isinstance(key_bindings[key], str):
        mouse_button = int(key_bindings[key][-1])
        if mouse_button == 0:
            key_names[key] = "Left Click"
        elif mouse_button == 1:
            key_names[key] = "Middle Click"
        elif mouse_button == 2:
            key_names[key] = "Right Click"
        else:
            key_names[key] = "mouse button "+str(mouse_button)
    
    else:
        key_names[key] = pg.key.name(key_bindings[key])
  
def load(save):
    global stars
    global level_number
    global max_level
    global level_stars
    
    data = pickle.load(save)
    
    try:
       stars = data[0]
       level_number = data[1]
       max_level = data[2]
       level_stars = data[3]
    except IndexError:
        pass
    
def load_level(save):
    global platforms
    global powerups
    global player
    global allowed_objects
    
    data = pickle.load(save)
    
    try:
       platforms = data[0]
       powerups = data[1]
       player = data[2]
       allowed_objects = data[3]
    except IndexError:
        pass
        
def menu(saveable = False):
    global cont
    global fullscreen
    global screen
    global screen_width
    global screen_height
    global framerate
    global framerate_text
    global resolution
    global platforms
    global powerups
    global player
    global allowed_objects
    global level_text
    global level_number
    global max_level
    global level_stars
    
    global master_volume
    global music_volume
    global sfx_volume
    global music_channel
    
    global animation
    
    title = "PlaceHolder"
    font = pg.font.SysFont("Comic Sans", 50)
    title = font.render(title, True, (180, 200, 180))
    
    outer = (50, 100, 50)
    inner = (50, 50, 100)
    
    star_outer = (150, 120, 0)
    star_inner = (240, 240, 100)
    
    if saveable == True:
        if animation == False:
            if cont == True:
                title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.15], outer, inner, "Continue"),
                            "levels":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "  Levels  "),
                            "save":button(screen, 0.25, 0.1, [0.5, 0.45], outer, inner, "  Save  "),
                            "load":button(screen, 0.25, 0.1, [0.5, 0.6], outer, inner, "  Load  "),
                            "options":button(screen, 0.25, 0.1, [0.5, 0.75], outer, inner, "Options"),
                            "quit":button(screen, 0.25, 0.1, [0.5, 0.9], outer, inner, "  Quit  ")}
            else:
                title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "New Game"),
                            "load":button(screen, 0.25, 0.1, [0.5, 0.45], outer, inner, "  Load  "),
                            "options":button(screen, 0.25, 0.1, [0.5, 0.6], outer, inner, "Options"),
                            "quit":button(screen, 0.25, 0.1, [0.5, 0.75], outer, inner, "  Quit  ")}
        else:
            title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.15], outer, inner, "Continue"),
                          "stop_anim":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Skip Animation"),
                          "options":button(screen, 0.25, 0.1, [0.5, 0.45], outer, inner, "Options"),
                          "quit":button(screen, 0.25, 0.1, [0.5, 0.6], outer, inner, "  Quit  ")}
          
                
    else:
        if cont == True:
            title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Continue"),
                        "options":button(screen, 0.25, 0.1, [0.5, 0.5], outer, inner, "Options"),
                        "quit":button(screen, 0.25, 0.1, [0.5, 0.7], outer, inner, "  Quit  ")}
        else:
            title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "New Game"),
                        "options":button(screen, 0.25, 0.1, [0.5, 0.5], outer, inner, "Options"),
                        "quit":button(screen, 0.25, 0.1, [0.5, 0.7], outer, inner, "  Quit  ")}
        
    options_menu = {"display_settings": button(screen, 0.25, 0.1, [0.5, 0.25], outer, inner, "Display Settings"),
                    "audio_settings":button(screen, 0.25, 0.1, [0.5, 0.45], outer, inner, "Audio Settings"),
                    "controls":button(screen, 0.25, 0.1, [0.5, 0.65], outer, inner, "Controls"),
                    "back_tm":button(screen, 0.25, 0.1, [0.5, 0.85], outer, inner, "Title Menu")}
    
    key_menu = {"back_om": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  ")}
    key_count = 0
    for key in key_bindings:
        key_menu[key] = button(screen, 0.25, 0.1, [0.5, 0.3 + key_count*0.15], outer, inner, " "+key.title()+": "+key_names[key].title()+" ")
        key_count += 1
    
    
    save_count = 0
    saves = []
    for file in os.listdir("saves"):
        if file.endswith(".sav"):
            save_count += 1
            saves.append(file)
            
    level_count = 0
    levels = []
    for file in os.listdir("levels"):
        if file.endswith(".lvl"):
            if int(file.split("-")[0]) <= max_level:
                level_count += 1
                levels.append(file)
    
    load_menu = {"back_tm": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  ")}
    for i in range(save_count):
        load_menu[saves[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], outer, inner, saves[i].removesuffix(".sav"))
        
    level_menu = {"back_tm": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  ")}
    for i in range(level_count):
        temp = int(levels[i].removesuffix(".lvl").split("-")[0])
        if temp in stars:
            if stars[temp]:
                level_menu[levels[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], star_outer, star_inner, levels[i].removesuffix(".lvl"))
            else:
                level_menu[levels[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], outer, inner, levels[i].removesuffix(".lvl"))
        else:
            level_menu[levels[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], outer, inner, levels[i].removesuffix(".lvl"))
        
    
    display_menu = {"back_om": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  "),
                    "fullscreen": button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Fullscreen: " + str(fullscreen)),
                    "framerate": button(screen, 0.25, 0.2, [0.5, 0.50], outer, inner, "Framerate: " + framerate_text, slider=True, slider_max = 145, slider_min = 0, slider_value = framerate, slider_colour = (147, 107, 15)),
                    "resolution": button(screen, 0.25, 0.1, [0.5, 0.70], outer, inner, "Resolution: " + str(int(round(screen_width*1.5, 0))) + "X" + str(int(round(screen_height*1.5, 0)))),
    }
    
    audio_menu = {"back_om": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  "),
                  "master_volume": button(screen, 0.25, 0.2, [0.5, 0.30], outer, inner, "Master: " + str(master_volume*10), slider=True, slider_max = 100, slider_min = 0, slider_value = master_volume*10, slider_colour = (147, 107, 15)),
                  "music_volume": button(screen, 0.25, 0.2, [0.5, 0.50], outer, inner, "Music: " + str(music_volume*10), slider=True, slider_max = 100, slider_min = 0, slider_value = music_volume*10, slider_colour = (147, 107, 15)),
                  "sfx_volume": button(screen, 0.25, 0.2, [0.5, 0.70], outer, inner, "SFX: " + str(sfx_volume*10), slider=True, slider_max = 100, slider_min = 0, slider_value = sfx_volume*10, slider_colour = (147, 107, 15)),
    }
    
    if framerate_text == "Unlimited":
        display_menu["framerate"].slider_value = 145
    if framerate_text == "Vsync":
        display_menu["framerate"].slider_value = 0
    
    
    current_menu = title_menu
    
    end = False
    game_start = False
    while not end:
        events = pg.event.get(pg.MOUSEBUTTONDOWN)
        background = pg.transform.scale(other_images["background"],[screen_width, screen_height])
        screen.get_surface().blit(background, [0, 0])
        screen.get_surface().blit(title, ((0.5*screen_width)-(title.get_width()/2),(0.1*screen_height)-(title.get_height()/2)))
        changed_menu = False
        
        # allows scrolling for certain menus
        for event in pg.event.get(pg.MOUSEWHEEL):
            if current_menu == key_menu:
                if event.y == -1:
                    for it in current_menu:
                        current_menu[it].center[1] -= 0.025
                    current_menu["back_om"].center[1] += 0.025
                elif event.y == 1:
                    for it in current_menu:
                        current_menu[it].center[1] += 0.025
                    current_menu["back_om"].center[1] -= 0.025
            
            elif current_menu == load_menu:
                if event.y == -1:
                    for it in current_menu:
                        current_menu[it].center[1] -= 0.025
                    current_menu["back_tm"].center[1] += 0.025
                elif event.y == 1:
                    for it in current_menu:
                        current_menu[it].center[1] += 0.025
                    current_menu["back_tm"].center[1] -= 0.025
            elif current_menu == level_menu:
                if event.y == -1:
                    for it in current_menu:
                        current_menu[it].center[1] -= 0.025
                    current_menu["back_tm"].center[1] += 0.025
                elif event.y == 1:
                    for it in current_menu:
                        current_menu[it].center[1] += 0.025
                    current_menu["back_tm"].center[1] -= 0.025
                
        
        for item in current_menu:
            mouse_pos = pg.mouse.get_pos()
            if changed_menu == True:
                break
            
            current_menu[item].draw()
            
            
            
            for event in pg.event.get(pg.QUIT):
                sys.exit(0)
                
            if pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]:
                for event in events:
                    
                    if current_menu[item].get_focused(mouse_pos):
                        sound = choice(["", "1", "2"])
                        other_sounds["click" + sound].set_volume(master_volume*sfx_volume/100)
                        other_sounds["click" + sound].play()
                        
                        if item == "new_game":
                            if cont == False:
                                game_start = True
                                end = True
                            else:
                                end = True

                        elif item == "quit":
                            sys.exit(0)
                            
                        elif item == "options":
                            current_menu = options_menu
                            changed_menu = True
                          
                        elif item == "load":
                            changed_menu = True
                            current_menu = load_menu
                            
                        elif item == "levels":
                            changed_menu = True
                            current_menu = level_menu
                            
                        elif item == "back_tm":
                            current_menu = title_menu
                            changed_menu = True
                            
                        elif item == "controls":
                            current_menu = key_menu
                            changed_menu = True
                            
                        elif item == "stop_anim":
                            animation = False
                            end = True
                        
                        elif item in key_menu and not item == "back_om" and not item == "slider":
                            
                            text = "choose new key: "
                            text = font.render(text, True, (0, 0, 0))
                            pg.draw.rect(screen.get_surface(), outer, ((0.49*screen_width)-(text.get_width()/2),(0.49*screen_height)-(text.get_height()/2), text.get_width()*1.2, text.get_height()*1.2), border_radius=50)
                            pg.draw.rect(screen.get_surface(), inner, ((0.5*screen_width)-(text.get_width()/2),(0.5*screen_height)-(text.get_height()/2), text.get_width()*1.15, text.get_height()*1.05), border_radius=50)
                            screen.get_surface().blit(text, ((0.51*screen_width)-(text.get_width()/2),(0.5*screen_height)-(text.get_height()/2)))
                            screen.flip()
                            
                            constants = dir(pg.constants)
                            key = None
                            mouse_button = None
                            while key == None and mouse_button == None:
                                for event in pg.event.get(pg.MOUSEBUTTONDOWN) + pg.event.get(pg.KEYDOWN):
                                
                                    keys = pg.key.get_pressed()
                                    for constant in constants:
                                        potential_key = getattr(pg.constants, constant)
                                        if isinstance(potential_key, int):
                                            if keys[potential_key] == True:
                                                key = potential_key

                                    for i in range(len(pg.mouse.get_pressed(5))):
                                        if pg.mouse.get_pressed(5)[i] == True:
                                            mouse_button = i
                            
                            if mouse_button != None:
                                key_bindings[item] = "mouse_button-"+str(mouse_button)
                                if mouse_button == 0:
                                    current_menu[item].text = " " + item.title() + ": " + "Left Click" + " "
                                elif mouse_button == 1:
                                    current_menu[item].text = " " + item.title() + ": " + "Middle Click" + " "
                                elif mouse_button == 2:
                                    current_menu[item].text = " " + item.title() + ": " + "Right Click" + " "
                                else:
                                    current_menu[item].text = " " + item.title() + ": " + "mouse button "+str(mouse_button) + " "
                            else:
                                key_bindings[item] = key
                                current_menu[item].text = " " + item.title() + ": " + pg.key.name(key).title() + " "
                            
                            options = open("options.txt", "r")
                            prev_options = options.readlines()
                            options.close()
                            
                            line_number = 0
                            new_line = ""
                            for line in prev_options:
                                if ":" in line:
                                    line = line.replace("\n", "").split(":")
                                    
                                    
                                    if line[0] == item:
                                        if mouse_button != None:
                                            new_line = item + ":" + "mouse_button-"+str(mouse_button) + "\n"
                                        else:
                                            new_line = item + ":" + pg.key.name(key)+"\n"
                                        break

                                line_number += 1
                            
                            prev_options[line_number] = new_line
                            options = open("options.txt", "w")
                            options.writelines(prev_options)
                            options.close()                                                                                               
                        
                        elif item in load_menu and not item == "back_tm":
                            save = open("saves\\"+item, "rb")
                            load(save)
                            main()
                            
                        elif item in level_menu and not item == "back_tm":
                            save = open("levels\\"+item, "rb")
                            load_level(save)
                            
                            if level_number in stars:
                                if stars[level_number]:
                                    for entity in powerups:
                                        if entity.type == 5:
                                            powerups.remove(entity)
                                            break
                                    to_remove = None
                                    for entity in allowed_objects:
                                        if isinstance(entity, PowerUp):
                                            if entity.type == 5:
                                                to_remove = entity
                                    if to_remove != None:
                                        allowed_objects.pop(to_remove)
                            
                            if player != []:
                                player = player[0]
                            
                            level_number, level_name = level_menu[item].text.split("-")
                            level_number = int(level_number)
                            
                            font = pg.font.SysFont("Comic Sans", 50)
                            temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
                            level_text = {}
                            level_text[temp] = [5, 5]
                            main()
                              
                        elif item == "save":
                            done = False
                            save_name = time.ctime().replace(":", "_").replace(" ", "_")
                            
                            font = pg.font.SysFont("calibri", int(0.1*screen_height))
                            
                            info = "Choose Save Name"
                            info = font.render(info, True, (50, 20, 20))
                            
                            held_keys = {}
                            while not done:
                                clock.tick(framerate)
                                text = font.render(save_name, True, (10, 10, 10))
                                
                                # scaling text if it becomes too big
                                if not len(save_name) == 0:
                                    old_width = text.get_width()
                                    if old_width > (0.7*screen_width) :
                                        text = pg.transform.scale(text, ((0.8*screen_width) - 20, text.get_height()))
                                        
                                    scaling_ratio = text.get_width()/old_width
                                    new_height = scaling_ratio * text.get_height()
                                    
                                    text = pg.transform.scale(text, (text.get_width(), new_height))
                                            
                                # Drawing save menu                        
                                pg.draw.rect(screen.get_surface(), outer,
                                             ((0.5*screen_width) - (0.4*screen_width),
                                              (0.5*screen_height) - (0.1*screen_height),
                                              0.8*screen_width, 0.2*screen_height))
                                pg.draw.rect(screen.get_surface(), inner,
                                             ((0.5*screen_width) - (0.4*screen_width) + 10,
                                              (0.5*screen_height) - (0.1*screen_height) + 10,
                                              (0.8*screen_width) - 20, (0.2*screen_height) - 20))
                                screen.get_surface().blit(text, ((0.5*screen_width) - (0.5*text.get_width()),
                                                   (0.5*screen_height) - (0.5*text.get_height())))
                                pg.draw.rect(screen.get_surface(), outer, ((0.46*screen_width)-(info.get_width()/2),(0.64*screen_height)-(info.get_height()/2), info.get_width()*1.2, info.get_height()*1.2), border_radius=50)
                                pg.draw.rect(screen.get_surface(), inner, ((0.47*screen_width)-(info.get_width()/2),(0.65*screen_height)-(info.get_height()/2), info.get_width()*1.15, info.get_height()*1.05), border_radius=50)
                            
                                screen.get_surface().blit(info, ((0.5*screen_width) - (0.5*info.get_width()),
                                                   (0.6*screen_height) ))
                                screen.flip() 
                                
                                for event in pg.event.get(pg.QUIT):
                                    sys.exit(0)
                                
                                # Handling keyboard input
                                
                                # Handling held keys
                                keys = pg.key.get_pressed()
                                for i in range(len(keys)):
                                    if keys[i]:
                                        try:
                                            held_keys[pg.key.name(i)] += 1
                                        except KeyError:
                                            held_keys[pg.key.name(i)] = 1
                                        
                                        if held_keys[pg.key.name(i)] >= framerate and held_keys[pg.key.name(i)] % (framerate/15) == 0:
                                            mods = pg.key.get_mods()
                                    
                                            character = pg.key.name(i)
                                        
                                            if len(character) == 1:
                                            
                                                if mods == 1 or mods == 2 or mods == 8192:
                                                    character = character.upper()
                                                    if character == "-":
                                                        character = "_"
                                                    elif character == "1":
                                                        character = "!"
                                                    elif character == "2":
                                                        character = "@"
                                                    elif character == "3":
                                                        character = "#"
                                                    elif character == "4":
                                                        character = "$"
                                                    elif character == "5":
                                                        character = "%"
                                                    elif character == "6":
                                                        character = "^"
                                                    elif character == "7":
                                                        character = "&"
                                                    elif character == "8":
                                                        character = "*"
                                                    elif character == "9":
                                                        character = "()"
                                                    elif character == "0":
                                                        character = ")"
                                                save_name += character
                                                
                                            else:
                                                if character == "space":
                                                    save_name += " "
                                                    
                                            if event.key == pg.K_BACKSPACE:
                                                s = list(save_name)
                                                if len(s) > 0:
                                                    s.pop()
                                                save_name = ""
                                                for i in range(len(s)):
                                                    save_name += s[i]
                                    
                                    else:
                                        held_keys[pg.key.name(i)] = 0
                                         
                                # Handling single press keys
                                for event in pg.event.get(pg.KEYDOWN):
                                    mods = pg.key.get_mods()
                                    
                                    character = pg.key.name(event.key)
                                
                                    if len(character) == 1:
                                    
                                        if mods == 1 or mods == 2 or mods == 8192:
                                            character = character.upper()
                                            
                                            if mods == 1 or mods == 2 or mods == 8192:
                                                    character = character.upper()
                                                    if character == "-":
                                                        character = "_"
                                                    elif character == "1":
                                                        character = "!"
                                                    elif character == "2":
                                                        character = "@"
                                                    elif character == "3":
                                                        character = "#"
                                                    elif character == "4":
                                                        character = "$"
                                                    elif character == "5":
                                                        character = "%"
                                                    elif character == "6":
                                                        character = "^"
                                                    elif character == "7":
                                                        character = "&"
                                                    elif character == "8":
                                                        character = "*"
                                                    elif character == "9":
                                                        character = "()"
                                                    elif character == "0":
                                                        character = ")"
                                                        
                                        save_name += character
                                        
                                    else:
                                        if character == "space":
                                            save_name += " "
                                            
                                    if event.key == pg.K_BACKSPACE:
                                        s = list(save_name)
                                        if len(s) > 0:
                                            s.pop()
                                        save_name = ""
                                        for i in range(len(s)):
                                            save_name += s[i]
                                        
                                    if event.key == pg.K_RETURN:
                                        
                                        if len(save_name) >=1:
                                            save = open("saves\\"+save_name+".sav", "wb")
                                            
                                            data = [stars, level_number, max_level, level_stars]
                                            
                                            pickle.dump(data, save)
                                            
                                            save.close()
                                                                                        
                                            done = True
                                            
                                    if event.key == key_bindings["menu"]:
                                        done = True
                                        
                                                                                        
                        elif item == "back_om":
                            changed_menu = True
                            current_menu = options_menu

                        elif item == "display_settings":
                            current_menu = display_menu
                            changed_menu = True
                        
                        elif item == "audio_settings":
                            current_menu = audio_menu
                            changed_menu = True
                            
                        elif item == "fullscreen":
                            options = open("options.txt", "r")
                            prev_options = options.readlines()
                            options.close()
                            
                            line_number = 0
                            new_line = ""
                            
                            if fullscreen == True:
                                fullscreen = False
                                text = "0"
                            else:
                                fullscreen = True
                                text = "1"
                                
                            current_menu[item] =button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Fullscreen: " + str(fullscreen))
                                
                           
                            if fullscreen == False:
                                temp = pg.display.Info()
                            
                                moniter_width, moniter_height = temp.current_w, temp.current_h
                                
                                screen_width, screen_height = int(resolution.split("X")[0]),int(resolution.split("X")[1])
                                screen_width /= 1.5
                                screen_height /= 1.5
                                                                
                                screen.size = [screen_width, screen_height]
                                screen.position = ((moniter_width/2) - (screen_width/2), (moniter_height/2) - (screen_height/2))
                            else: 
                                temp = pg.display.Info()
                            
                                moniter_width, moniter_height = temp.current_w, temp.current_h
                                
                                screen.size = [moniter_width, moniter_height]
                                screen.position = (0, 0)
                                screen_height = moniter_height
                                screen_width = moniter_width
                                new_resolution = str(int(screen_width*1.5)) + "X" + str(int(screen_height*1.5))
                                resolution = new_resolution
                                
                                current_menu["resolution"] = button(screen, 0.25, 0.1, [0.5, 0.70], outer, inner, "Resolution: " + resolution)
                                
                            for line in prev_options:
                                if ":" in line:
                                    line = line.replace("\n", "").split(":")
                                    
                                    
                                    if line[0] == item:
                                        new_line = item + ":" + text+"\n"
                                        break

                                line_number += 1
                            
                            prev_options[line_number] = new_line
                            options = open("options.txt", "w")
                            options.writelines(prev_options)
                            options.close()
                            
                        elif item == "resolution":
                            options = open("options.txt", "r")
                            prev_options = options.readlines()
                            options.close()
                            
                            fullscreen = False
                            current_menu["fullscreen"] =button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Fullscreen: " + str(fullscreen))
                            
                            line_number = 0
                            new_line = ""
                            
                            current_resolution = resolution_presets.index(resolution)
                            if current_resolution + 1 >= len(resolution_presets):
                                new_resolution = resolution_presets[0] 
                            else:
                                new_resolution = resolution_presets[current_resolution + 1] 
                                
                            temp = pg.display.Info()
                            
                            moniter_width, moniter_height = temp.current_w, temp.current_h
                                
                            text = new_resolution
                            resolution = new_resolution
                            screen_width, screen_height = int(text.split("X")[0]),int(text.split("X")[1])
                            
                            
                            screen_width, screen_height = screen_width/1.5, screen_height/1.5
                            
                            screen.size = [screen_width, screen_height]
                            screen.position = ((moniter_width/2) - (screen_width/2), (moniter_height/2) - (screen_height/2))
                            
                            
                            current_menu[item] = button(screen, 0.25, 0.1, [0.5, 0.70], outer, inner, "Resolution: " + text)
                                
                            for line in prev_options:
                                if ":" in line:
                                    line = line.replace("\n", "").split(":")
                                    
                                    
                                    if line[0] == item:
                                        new_line = item + ":" + text+"\n"
                                        break

                                line_number += 1
                            
                            prev_options[line_number] = new_line
                            options = open("options.txt", "w")
                            options.writelines(prev_options)
                            options.close()
                
            if changed_menu == True:
                break
                        
            if item == "framerate":
                temp = current_menu[item].get_focused(mouse_pos)
                
                if temp[0]:
                    current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                    current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                        
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                
                if temp[0] and (pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]):
                    framerate = temp[1]
                    current_menu[item].slider_value = framerate
                    if int(round(framerate, 0)) == 0:
                        framerate = pg.display.get_desktop_refresh_rates()[0]
                        framerate_text = "VSync"
                    elif int(round(framerate, 0)) == 145:
                        framerate = 1_000_000_000
                        framerate_text = "Unlimited"
                    else:
                        framerate_text = str(int(round(framerate, 0)))
                    current_menu[item].text = "Framerate: " + framerate_text
                    
                    options = open("options.txt", "r")
                    prev_options = options.readlines()
                    options.close()
                    
                    line_number = 0
                    new_line = ""
                    
                    for line in prev_options:
                        if ":" in line:
                            line = line.replace("\n", "").split(":")
                            
                            
                            if line[0] == item:
                                new_line = item + ":" + framerate_text+"\n"
                                break

                        line_number += 1
                    
                    prev_options[line_number] = new_line
                    options = open("options.txt", "w")
                    options.writelines(prev_options)
                    options.close()
            
            elif item == "master_volume":
                temp = current_menu[item].get_focused(mouse_pos)
                
                if temp[0]:
                    current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                    current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                        
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                
                if temp[0] and (pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]):
                    master_volume = int(temp[1])/10
                    current_menu[item].slider_value = master_volume*10
                    
                    current_menu[item].text = "Master: " + str(master_volume*10)
                    
                    options = open("options.txt", "r")
                    prev_options = options.readlines()
                    options.close()
                    
                    line_number = 0
                    new_line = ""
                    
                    for line in prev_options:
                        if ":" in line:
                            line = line.replace("\n", "").split(":")
                            
                            
                            if line[0] == item:
                                new_line = item + ":" + str(master_volume*10)+"\n"
                                break

                        line_number += 1
                    
                    prev_options[line_number] = new_line
                    options = open("options.txt", "w")
                    options.writelines(prev_options)
                    options.close()
                    
                    music_channel.set_volume(master_volume*music_volume/100)
            
            elif item == "music_volume":
                temp = current_menu[item].get_focused(mouse_pos)
                
                if temp[0]:
                    current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                    current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                        
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                
                if temp[0] and (pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]):
                    music_volume = int(temp[1])/10
                    current_menu[item].slider_value = music_volume*10
                    
                    current_menu[item].text = "Music: " + str(music_volume*10)
                    
                    options = open("options.txt", "r")
                    prev_options = options.readlines()
                    options.close()
                    
                    line_number = 0
                    new_line = ""
                    
                    for line in prev_options:
                        if ":" in line:
                            line = line.replace("\n", "").split(":")
                            
                            
                            if line[0] == item:
                                new_line = item + ":" + str(music_volume*10)+"\n"
                                break

                        line_number += 1
                    
                    prev_options[line_number] = new_line
                    options = open("options.txt", "w")
                    options.writelines(prev_options)
                    options.close()
                    
                    music_channel.set_volume(master_volume*music_volume/100)
            
            elif item == "sfx_volume":
                temp = current_menu[item].get_focused(mouse_pos)
                
                if temp[0]:
                    current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                    current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                        
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                
                if temp[0] and (pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]):
                    sfx_volume = int(temp[1])/10
                    current_menu[item].slider_value = sfx_volume*10
                    
                    current_menu[item].text = "SFX: " + str(sfx_volume*10)
                    
                    options = open("options.txt", "r")
                    prev_options = options.readlines()
                    options.close()
                    
                    line_number = 0
                    new_line = ""
                    
                    for line in prev_options:
                        if ":" in line:
                            line = line.replace("\n", "").split(":")
                            
                            
                            if line[0] == item:
                                new_line = item + ":" + str(sfx_volume*10)+"\n"
                                break

                        line_number += 1
                    
                    prev_options[line_number] = new_line
                    options = open("options.txt", "w")
                    options.writelines(prev_options)
                    options.close()
            
            
            else:
                temp = current_menu[item].text
                try:
                    temp = int(temp.split("-")[0])
                except ValueError:
                    pass
                if  not item in level_menu:
                    if current_menu[item].get_focused(mouse_pos):
                        current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                        current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                            
                    else:
                        current_menu[item].outer_colour = outer
                        current_menu[item].inner_colour = inner
                elif temp in stars:
                    if stars[temp]:
                        if current_menu[item].get_focused(mouse_pos):
                            current_menu[item].outer_colour = min(star_outer[0]*1.1, 255), min(star_outer[1]*1.1, 255), min(star_outer[2]*1.1, 255)
                            current_menu[item].inner_colour = min(star_inner[0]*1.1, 255), min(star_inner[1]*1.1, 255), min(star_inner[2]*1.1, 255)
                        
                        else:
                            current_menu[item].outer_colour = star_outer
                            current_menu[item].inner_colour = star_inner
                                
                    else:
                        current_menu[item].outer_colour = star_outer
                        current_menu[item].inner_colour = star_inner
                            
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                    
            for event in pg.event.get(pg.KEYDOWN):
                                       
                if event.key == key_bindings["menu"]:
                    if cont == True:
                        end = True
                                                                                 
                
        screen.flip()
        
        if music_channel.get_busy() == False:
            global current_track
            current_track = choice(list(music.keys()))
            segment = choice(list(music[current_track].keys()))

            music_channel.set_volume(master_volume*music_volume/100)
            music_channel.play(music[current_track][segment])
        
    if game_start == True:
        main()
        
class Platform:
    def __init__(self, location, width, height, type = 0):
        self.location = location
        self.width = width
        self.height = height
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        self.type = type
        self.start = [self.location[0], self.location[1]]
        self.offset = [0, 0]
        
        self.passengers = []
        
        self.tags = ""
        self.id = (randint(1, 12_090_070)/ randint(1, 1350)) * randint(1, 1091)
        
        self.frame = 0
        
    def draw(self, surface = screen.get_surface()):
        global d_time
        self.frame += d_time*60
        if self.type == 0:
            pg.draw.rect(surface, (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 1:
            pg.draw.rect(surface, (240, 50, 240), (self.location, (self.width, self.height)))
        elif self.type == 2:
            pg.draw.rect(surface, (150, 0, 0), (self.location, (self.width, self.height)))
        elif self.type == 3:
            pg.draw.rect(surface, (50, 50, 50), (self.location, (self.width, self.height)))
        elif self.type == 4:
            pg.draw.rect(surface, (50, 240, 50), (self.location, (self.width, self.height)))
        elif self.type == 5:
            image = platform_images["end"]
            image = pg.transform.scale(image, [self.width, self.height])
            surface.blit(image, (self.location))
        
    def update(self):
        global d_time
        if self.type == 1 and "-moving_end-" in self.tags:
            
            destination = [self.start[0] + self.offset[0], self.start[1] + self.offset[1]]
            
            x_diff = destination[0] - self.start[0]
            y_diff = destination[1] - self.start[1]
            
            self.location[0] += x_diff*d_time/10
            self.location[1] += y_diff*d_time/10
            
            for passenger in self.passengers:
                passenger.location[0] += x_diff*d_time/10
                passenger.location[1] += y_diff*d_time/10
            
            self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
            
            if destination[0] > self.start[0]:
                if self.location[0] > destination[0]:
                    self.location[0] = destination[0]
            elif destination[0] < self.start[0]:
                if self.location[0] < destination[0]:
                    self.location[0] = destination[0]
            
            if destination[1] > self.start[1]:
                if self.location[1] > destination[1]:
                    self.location[1] = destination[1]
            elif destination[1] < self.start[1]:
                if self.location[1] < destination[1]:
                    self.location[1] = destination[1]
                    
            if self.location == destination:
                self.tags = self.tags.replace("-moving_end-", "-moving_start-")
            
        if self.type == 1 and "-moving_start-" in self.tags:
            destination = [self.start[0] + self.offset[0], self.start[1] + self.offset[1]]
            
            x_diff = self.start[0] - destination[0]
            y_diff = self.start[1] - destination[1]
            
            self.location[0] += x_diff*d_time/10
            self.location[1] += y_diff*d_time/10
            
            for passenger in self.passengers:
                passenger.location[0] += x_diff*d_time/10
                passenger.location[1] += y_diff*d_time/10
                passenger.centre = [passenger.location[0] + passenger.width/2, passenger.location[1] + passenger.height/2]
                if isinstance(passenger, Platform) or isinstance(passenger, Player):
                    passenger.start = [passenger.location[0], passenger.location[1]]
            
            self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
            
            if self.start[0] > destination[0]:
                if self.location[0] > self.start[0]:
                    self.location[0] = self.start[0]
            elif self.start[0] < destination[0]:
                if self.location[0] < self.start[0]:
                    self.location[0] = self.start[0]
            
            if self.start[1] > destination[1]:
                if self.location[1] > self.start[1]:
                    self.location[1] = self.start[1]
            elif self.start[1] < destination[1]:
                if self.location[1] < self.start[1]:
                    self.location[1] = self.start[1]
                    
            if self.location == self.start:
                self.tags = self.tags.replace("-moving_start-", "-moving_end-")
                 
class Player:
    def __init__(self, location):
        self.location = location
        self.width = 40
        self.height = 55
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        self.jump_enabled = False
        self.jump_allowed = False
        self.dashes = 0
        self.max_dashes = 0
        self.dash_speed = [0, 0]
        self.dash_timer = -1
        self.flow_mult = 1
        self.speed = [0, 0]
        self.on_ground = False
        self.cayote_timer = 0
        self.crouched = False
        self.dead = False
        self.tags = ""
        self.id = -1
        self.offset = [0, 0]
        self.start = [self.location[0], self.location[1]]
        self.frame = 0
        
    def draw(self, surface = screen.get_surface()):
        pg.draw.rect(surface, (220, 255, 220), (self.location, (self.width, self.height)))
    
    def collide(self, entity):
        entity_rect = pg.Rect(entity.location[0], entity.location[1], entity.width, entity.height)
        self_rect = pg.Rect(self.location, [self.width, self.height])
        
        if entity_rect.colliderect(self_rect):
            return True
            
        return False
    
    def update(self, entity_list, d_time):
        global platforms
        global powerups
        global player
        global allowed_objects
        global level_number
        global level_name
        global level_text
        global stars
        global max_level
        global level_stars
        
        global previous_time
        global music_channel
        
        self.cayote_timer += d_time
        self.frame += d_time*60
        
        if self.dash_timer >= 0:
            self.crouched = True
            self.dash_timer += d_time
        else:
            if not "-no_collide-" in self.tags:
                self.speed[1] += 0.1*d_time*60
            
        if self.dash_timer >= 0.17:
            self.crouched = True
            
            if not "-no_collide-" in self.tags:
                self.speed[1] += 0.1*d_time*60
            
            self.dash_speed[0] *= 0.8
            self.dash_speed[1] *= 0.8
            self.dash_speed[0] = truncate(self.dash_speed[0], 1)
            self.dash_speed[1] = truncate(self.dash_speed[1], 1)
            
            if vector_magnitude(self.dash_speed) == 0:
                self.dash_timer = -1
                
        flow_speed = [self.speed[0] + self.dash_speed[0], min(self.speed[1], 0) + self.dash_speed[1]]
        
        if vector_magnitude(flow_speed) > 0:
            self.flow_mult += self.flow_mult*0.035*d_time
        else:
            self.flow_mult = 1
            
        if self.speed[1] >= 14.5:
            self.speed[1] = 14.5
                
        self.location[0] += self.speed[0]*self.flow_mult*d_time*60
        self.location[1] += self.speed[1]*self.flow_mult*d_time*60
        self.location[0] += self.dash_speed[0]*self.flow_mult*d_time*60
        self.location[1] += self.dash_speed[1]*self.flow_mult*d_time*60
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        
        if self.cayote_timer >= 0.204:
            self.on_ground = False
            self.cayote_timer = 0
            
        
        Top_collide = False
        Bottom_collide = False
        for entity in entity_list:
            try:
                if self in entity.passengers:
                        entity.passengers.remove(self)
            except:
                pass
            
            if self.collide(entity) and not "-no_collide-" in entity.tags and not "-no_collide-" in self.tags:
                if isinstance(entity, Platform):
                    
                    if not "moving" in entity.tags:
                        entity.tags += "-moving_end-"
                        
                                    
                    x_diff = self.centre[0] - entity.centre[0]
                    y_diff = self.centre[1] - entity.centre[1]
                    
                    if (entity.width/2 + self.width/2 + 1) - abs(x_diff) < (entity.height/2 + self.height/2 + 1) - abs(y_diff):
                        if x_diff < 0:
                            self.location[0] -= (entity.width/2 + self.width/2) - abs(x_diff)
                        else:
                            self.location[0] += (entity.width/2 + self.width/2 ) - abs(x_diff)

                    else:
                        if y_diff < 0:
                            
                            if entity.type == 5:
                                level_number += 1
                                max_level = max(level_number, max_level)
                                
                                temp = deepcopy(screen.get_surface())
                                temp = pg.transform.scale(temp, [1280, 720])
                                stage_transition_animation(temp)
                                            
                                font = pg.font.SysFont("Comic Sans", 50)
                                temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
                                level_text = {}
                                level_text[temp] = [5, 5]                        
                            
                            self.on_ground = True
                            Bottom_collide = True
                            if not self in entity.passengers:
                                entity.passengers.append(self)
                            self.cayote_timer = 0
                            self.speed[1] = 0
                            
                            if Bottom_collide == Top_collide == True:
                                self.dead = True
                            self.location[1] -= (entity.height/2 + self.height/2 - 1) - abs(y_diff)
                            
                            
                        else:
                            Top_collide = True
                            if Bottom_collide == Top_collide == True:
                                self.dead = True
                                
                            self.location[1] += (entity.height/2 + self.height/2) - abs(y_diff)
                    
                    if entity.type == 2:
                        self.dead = True
                        self.speed[0] *= 0.1
                        self.speed[1] *= 0.1
                        
                    
                            
                elif isinstance(entity, PowerUp):
                    if entity.type == 0: #Jump Crystal
                        self.jump_enabled = True
                        self.jump_allowed = True
                        self.on_ground = True
                        self.cayote_timer = 0
                        powerups.remove(entity)
                    elif entity.type == 1: #Dash Crystal
                        self.max_dashes += 1
                        self.dashes = self.max_dashes  
                        powerups.remove(entity)   
                    elif entity.type == 5: # Stars
                        stars[level_number] = True  
                        powerups.remove(entity) 
                        other_sounds["star_collect"].set_volume(master_volume*music_volume/100)
                        other_sounds["star_collect"].play()
                        # of the form: location, size, rotation 
                        star_data = {"location":[randint(60, 1250), randint(60, 690)],
                                                     "size":randint(10, 20), 
                                                     "angle":randint(0, 359),
                                                     "direction": randint(0, 1),
                                                     "speed": randint(1, 10)/100,
                                                     "growth_phase": randint(0, 1),
                                                     "layer":randint(1, 3)}
                        
                        music_channel.pause()
                        star_collect_animation(entity, star_data)
                        music_channel.unpause()
                        level_stars[level_number] = star_data
                        previous_time = time.time()
                        
                        
                    elif entity.type == 4: # Cam Trigger
                        if self.offset == [0, 0]:
                            self.offset[0], self.offset[1] = [entity.offset[0], entity.offset[1]]
                            entity.offset[0] *= -1
                            entity.offset[1] *= -1
                            
                    elif entity.type == 2: #Fog
                        if not "-triggered-" in entity.tags:
                            entity.tags += "-triggered"
                        
        if self.offset != [0, 0]:
            destination = [self.start[0] + self.offset[0], self.start[1] + self.offset[1]]
            
            x_diff = destination[0] - self.start[0]
            y_diff = destination[1] - self.start[1]
            
            self.location[0] -= x_diff*d_time*10
            self.location[1] -= y_diff*d_time*10
            self.offset[0] -= x_diff*d_time*10
            self.offset[1] -= y_diff*d_time*10
            self.start[0] -= x_diff*d_time*10
            self.start[1] -= y_diff*d_time*10
            
            self.offset[0] = truncate(self.offset[0], 2)
            self.offset[1] = truncate(self.offset[1], 2)
            
            for entity in entity_list:
                entity.location[0] -= x_diff*d_time*10
                entity.location[1] -= y_diff*d_time*10
                entity.centre = [entity.location[0] + entity.width/2, entity.location[1] + entity.height/2]
                if isinstance(entity, Platform):
                    entity.start[0] -= x_diff*d_time*10
                    entity.start[1] -= y_diff*d_time*10
            
            self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
            
            
          
        else:
            self.start = [self.location[0], self.location[1]]
                    
        if self.on_ground:
            if self.dash_timer == -1:
                self.dashes = self.max_dashes
            self.jump_allowed = True
        else:
            self.jump_allowed = False
        
        if self.crouched == True:
            if self.height == 55:
                if self.on_ground or self.dash_timer != -1:
                    self.location[1] += 15
                
                else:
                    self.location[1] += 7.5
                
                self.height = 40
        else:
            self.height = 55
            
        if self.dead:
            self.height = 30
            self.width = 55
 
class PowerUp:
    def __init__(self, location, type):
        self.location = location
        self.type = type
        self.width = 50
        self.height = 50
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        self.tags = ""
        self.id = (randint(1, 12_090_070)/ randint(1, 1350)) * randint(1, 1091)
        
        self.offset = [0, 0]
        
        self.frame = 0
        
        
    def draw(self, surface = screen.get_surface()):
        global d_time
        if not "-fog-" in self.tags:
            self.frame += d_time*60
            frame = str(int(self.frame))
        if self.type == 0:
            pg.draw.rect(surface, (255, 200, 200), (self.location, (self.width, self.height)))
        elif self.type == 1:
            pg.draw.rect(surface, (255, 100, 255), (self.location, (self.width, self.height)))
        elif self.type == 2: # Fog
            if "-triggered-" in self.tags:
                self.frame += d_time*60
            
            temp = deepcopy(power_images["fog"])
            temp = pg.transform.scale(temp, [self.width, self.height])
            temp.set_alpha(min(max(255 - int(2*self.frame), 0), 255))
            surface.blit(temp, self.location)
            
            
        elif self.type == 3: # Refusal Zone
            temp = pg.Surface([self.width, self.height], pg.SRCALPHA)
            pg.draw.rect(temp, (240, 150, 150, 100), ([0, 0], (self.width, self.height)))
            surface.blit(temp, self.location)
            
            
        elif self.type == 4: # Cam Trigger
            pass
        
        
        elif self.type == 5: # Star
            try:
                temp = deepcopy(power_images["star_idle"][frame])
                temp = pg.transform.scale(temp, [self.width, self.height])
                surface.blit(temp, self.location)
            except KeyError:
                self.frame = 1
                frame = "1"
                temp = deepcopy(power_images["star_idle"][frame])
                temp = pg.transform.scale(temp, [self.width, self.height])
                surface.blit(temp, self.location)
        
   
       
global level_number
global stars
global max_level
global level_stars

level_number = 1
max_level = level_number
stars = {}
level_stars = {}

global platforms
global powerups
global player
global allowed_objects

platforms = []
powerups = []
player = []
allowed_objects = {}

global current_track
current_track = "MomentsBetween"
segment = str(1)

global music_channel
music_channel = pg.mixer.Channel(1)

music_channel.set_volume(master_volume*music_volume/100)
music_channel.play(music[current_track][segment])

global animation
animation = False

def star_collect_animation(star:PowerUp, star_data):
    global animation
    global power_images
    global d_time
    global previous_time
    
    animation = True
    fade_alpha = 1
    destination = [0, 0]
    time_taken = 0
    trail = False
    frame = 0
    ap = False
    oob = False
    explode = False
    
    
    while animation:
        temp_surface = pg.Surface([1280, 720], pg.SRCALPHA)
        fade = pg.Surface([1280, 720], pg.SRCALPHA)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)
                
            try:
                if pg.key.get_just_pressed()[key_bindings["menu"]]:
                    menu(True)
                    current_time = time.time()
                    d_time = 1/framerate
                    previous_time = current_time                
                        
            except TypeError:
                if isinstance(key_bindings["menu"], str):
                    if pg.mouse.get_just_pressed()[int(key_bindings["menu"][-1])]:
                        menu(True)
                        current_time = time.time()
                        d_time = 1/framerate
                        previous_time = current_time
      
        
        temp_surface.fill((25, 25, 75, 255))
        
        for sky_star in level_stars:
            temp_star = deepcopy(power_images["star_idle"]["1"])
            temp_star = pg.transform.scale(temp_star, [level_stars[sky_star]["size"], level_stars[sky_star]["size"]])
            temp = pg.Surface([level_stars[sky_star]["size"], level_stars[sky_star]["size"]], pg.SRCALPHA)
            temp.blit(temp_star)
            temp = pg.transform.rotate(temp, level_stars[sky_star]["angle"])
            
            
                    
            draw_location = [level_stars[sky_star]["location"][0] - temp.get_width()/2, level_stars[sky_star]["location"][1] - temp.get_height()/2]
                               
                
            temp_surface.blit(temp, draw_location)
        
        
        for platform in platforms:
            platform.draw(temp_surface)
        
        for power in powerups:
            power.draw(temp_surface)
            
        
            
        
        fade.fill((0, 0, 0, fade_alpha))
        fade_alpha += (4/framerate)*60
        fade_alpha = min(fade_alpha, 100)
        temp_surface.blit(fade)
        
        if player != []:
            player.draw(temp_surface)  
        
        if destination == [0, 0]: # Start of animation
            destination = [truncate(player.location[0]+(0.5*player.width)-(star.width/2)), truncate(player.location[1]-star.height)]
            x_diff = truncate(star.location[0] - destination[0], 3)
            y_diff = truncate(star.location[1] - destination[1], 3)
            time_taken = 1
            
        elif [round(star.location[0]), round(star.location[1])] == destination and time_taken >= framerate*2 and ap == False:
            # If star is above head
            destination[1] -= 720
            x_diff = star.location[0] - destination[0]
            y_diff = star.location[1] - destination[1]
            trail = True
            ap = True
            other_sounds["star_beam"].set_volume(master_volume*music_volume/100)
            other_sounds["star_beam"].play()
            
        elif [round(star.location[0]), round(star.location[1])] == destination and  not time_taken >= framerate*2:
            #making it pause above head
            x_diff = 0
            y_diff = 0   
            
        elif [round(star.location[0]), round(star.location[1])] == destination and time_taken >= framerate*2 and ap == True and explode == False and oob == False:
            destination = star_data["location"]   
            x_diff = truncate(star.location[0] - destination[0], 3)
            y_diff = truncate(star.location[1] - destination[1], 3)
            star.height = star.width
            oob = True
            
        elif [round(star.location[0]), round(star.location[1])] == destination and oob == True and explode == False:
            destination = star_data["location"]   
            x_diff = 0
            y_diff = 0
            star.height = star.width
            size_diff = star_data["size"] - star.height
            explode = True
            frame = 1
            
            other_sounds["star_burst"].set_volume(master_volume*music_volume/100)
            other_sounds["star_burst"].play()
            
        elif [round(star.location[0]), round(star.location[1])] == destination and explode == True:
            #making it stop at destination
            x_diff = 0
            y_diff = 0   
        
        
        
        star.location[0] -= x_diff/framerate
        star.location[1] -= y_diff/framerate
        
        star.draw(temp_surface)
        
        if time_taken >= 1:
            time_taken += 1
            
        if trail == True and ap == True and oob != True:
            frame += (1/framerate) *60
            frame = max(1, frame)
            frame = int(frame)
            if frame % 5 == 0:
                star.width = max(4, star.width - 4)
            try:
                image = power_images["star_beam"][str(frame)]
                image = pg.transform.scale(image, [star.width, image.height])
                
            except KeyError:
                frame = 100
                image = power_images["star_beam"][str(frame)]
                image = pg.transform.scale(image, [star.width, image.height])
            
            temp_surface.blit(image, [star.location[0] , star.location[1] + star.height])
            
        if explode == True:
            frame += (1/framerate) *60
            frame = max(1, frame)
            frame = int(frame)
            
            try:
                image = power_images["star_burst"][str(frame)]
                temp_surface.blit(image, [star.location[0] + (star.width/2)-(image.width/2), star.location[1] + (star.height/2) - (image.height/2)])
                
                star.width += size_diff/111
                star.height += size_diff/111
                
            except KeyError:
                animation = False
                
            
            
        
        ratio = min(screen_width/1280, screen_height/720)
        
        scaled_width = int(1280 * ratio)
        scaled_height = int(720 * ratio)
        
        temp_surface = pg.transform.scale(temp_surface, [scaled_width, scaled_height])
        center = [screen_width//2, screen_height//2]
        
        screen.get_surface().blit(temp_surface, [center[0] - scaled_width/2, center[1] - scaled_height/2])
            
        screen.flip()
        clock.tick(framerate)
        
          
    previous_time = time.time()        
    animation = False
 
def stage_transition_animation(pre_trans_surface: pg.Surface):
    global animation
    global power_images
    global d_time
    global previous_time
    global time_taken
    
    global player
    global level_number
    global level_name
    
    animation = True
    time_taken = 0
    size = 1280
    
    shrink = True
    grow = False
    
    while animation:
        temp_surface = pg.Surface([1280, 720], pg.SRCALPHA)
        iris_surface = pg.Surface([1280, 720], pg.SRCALPHA)
        location = [640, 360]
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)
                
            try:
                if pg.key.get_just_pressed()[key_bindings["menu"]]:
                    for levels in os.walk("levels"):
                        for level in levels[2]:
                            if level.split("-")[0] == str(level_number):
                                
                                level_name = level.split("-")[1].removesuffix(".lvl")
                                save = open("levels\\"+ level, "rb")
                                load_level(save)
                                if level_number in stars:
                                    if stars[level_number]:
                                        for entity in powerups:
                                            if entity.type == 5:
                                                powerups.remove(entity)
                                                break
                                        to_remove = None
                                        for entity in allowed_objects:
                                            if isinstance(entity, PowerUp):
                                                if entity.type == 5:
                                                    to_remove = entity
                                        if to_remove != None:
                                            allowed_objects.pop(to_remove)
                                            
                                if len(player) == 1:
                                    player = player[0]
                                break

                    menu(True)
                    current_time = time.time()
                    d_time = 1/framerate
                    previous_time = current_time                
                        
            except TypeError:
                if isinstance(key_bindings["menu"], str):
                    if pg.mouse.get_just_pressed()[int(key_bindings["menu"][-1])]:
                        for level in levels[2]:
                            if level.split("-")[0] == str(level_number):
                                
                                level_name = level.split("-")[1].removesuffix(".lvl")
                                save = open("levels\\"+ level, "rb")
                                load_level(save)
                                if level_number in stars:
                                    if stars[level_number]:
                                        for entity in powerups:
                                            if entity.type == 5:
                                                powerups.remove(entity)
                                                break
                                        to_remove = None
                                        for entity in allowed_objects:
                                            if isinstance(entity, PowerUp):
                                                if entity.type == 5:
                                                    to_remove = entity
                                        if to_remove != None:
                                            allowed_objects.pop(to_remove)
                                            
                                if len(player) == 1:
                                    player = player[0]
                                break
                        menu(True)
                        current_time = time.time()
                        d_time = 1/framerate
                        previous_time = current_time

        temp_surface.fill((25, 25, 75, 255))
        iris_surface.fill((0, 0, 0, 255))
            
        if shrink == True:
            if player != []:  
                location = [player.location[0] + (0.5*player.width), player.location[1] + (0.5*player.height)]
            temp_surface.blit(pre_trans_surface)
            pg.draw.circle(iris_surface, (0, 0, 0, 0), location, size)
            size -= 21*60/framerate
            size = max(size, 0)
            
        if grow == True:
            for platform in platforms:
                platform.draw(temp_surface)
                
            allowed_images = {}
            for thing in allowed_objects:
                temp_surface = pg.Surface([thing.width, thing.height])
                thing.location = [0, 0]
                if allowed_objects[thing] == 0:
                    temp_surface.fill((70, 70, 70))
                else:
                    thing.draw(temp_surface)
                ratio = 80 / max(thing.width, thing.height) 
                temp_surface = pg.transform.scale_by(temp_surface, ratio)
                allowed_images[temp_surface] = thing
            
            start_x = 20
            i = 0
            for image in allowed_images:
                    
                center = image.get_height()/2
                temp_surface.blit(image, [start_x + (100 * i), 50 - center])
                font = pg.font.SysFont("Comic Sans", 20)
                number = allowed_objects[allowed_images[image]]
                number = font.render(str(number), True, (180, 200, 180))
                temp_surface.blit(number, [start_x + (100 * i) + (80 - number.get_width()), (50 - center) + image.get_height()])
                i += 1
            
        
            for power in powerups:
                power.draw(temp_surface)
            
            if player != []:
                player.draw(temp_surface)  
                location = [player.location[0] + (0.5*player.width), player.location[1] + (0.5*player.height)]
                
            pg.draw.circle(iris_surface, (0, 0, 0, 0), location, size)
            size += 21*60/framerate
            size = min(size, 1280)
            
        temp_surface.blit(iris_surface)
        
        if shrink == True and size == 0 and time_taken == 0:
            time_taken = 1
        
        elif shrink == True and size == 0 and time_taken >= framerate:
            shrink = False
            grow  = True
            
            for levels in os.walk("levels"):
                for level in levels[2]:
                    if level.split("-")[0] == str(level_number):
                        
                        level_name = level.split("-")[1].removesuffix(".lvl")
                        save = open("levels\\"+ level, "rb")
                        load_level(save)
                        if level_number in stars:
                            if stars[level_number]:
                                for entity in powerups:
                                    if entity.type == 5:
                                        powerups.remove(entity)
                                        break
                                to_remove = None
                                for entity in allowed_objects:
                                    if isinstance(entity, PowerUp):
                                        if entity.type == 5:
                                            to_remove = entity
                                if to_remove != None:
                                    allowed_objects.pop(to_remove)
                                    
                        if len(player) == 1:
                            player = player[0]
                        break

        if grow == True and size == 1280:
            animation = False
            
        if time_taken >= 1:
            time_taken += 1
            
        ratio = min(screen_width/1280, screen_height/720)
        
        scaled_width = int(1280 * ratio)
        scaled_height = int(720 * ratio)
        
        temp_surface = pg.transform.scale(temp_surface, [scaled_width, scaled_height])
        center = [screen_width//2, screen_height//2]
        
        screen.get_surface().blit(temp_surface, [center[0] - scaled_width/2, center[1] - scaled_height/2])
            
        screen.flip()
        clock.tick(framerate)
    
    previous_time = time.time()
    animation = False
 
def main(): 
    
    global platforms
    global powerups
    global player
    global allowed_objects
    global level_text
    
    global music_channel
    
    global animation
    global previous_time
    
    global music_offset
    global level_number
    
    music_offset = 0
    
    animation = False         
    
    temp = deepcopy(screen.get_surface())
    temp = pg.transform.scale(temp, [1280, 720])
    stage_transition_animation(temp)
    
    global cont
    cont = True
    
    held_keys = {}
    frame = 0
    previous_time = time.time()
    current_time = time.time()
    global d_time
    d_time = 0.018
    
    selected_offset = [0, 0]
    selected_object = None
    
    font = pg.font.SysFont("Comic Sans", 50)
    temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
    
    level_text = {}
    level_text[temp] = [5, 5]
    
    cutout_size = [1280, 720]
    vignette_strength = 250
    vignette_alpha = 0
        
    while True:  
        direction = [0, 0]
        pre_scaled = pg.Surface([1280, 720])  
        vignette = pg.Surface([1280, 720], pg.SRCALPHA) 
        
           
        mouse_position = list(pg.mouse.get_pos())
        # # mouse_position[0] *= 1.5
        # # mouse_position[1] *= 1.5
        
        # # Scaling mouse position
        center = [(screen_width)//2, (screen_height)//2]
        ratio = min(screen_width/1280, screen_height/720)
        scaled_width = int(1280 * ratio)
        scaled_height = int(720 * ratio)
        
        mouse_position[0] -= center[0] - scaled_width/2
        mouse_position[1] -= center[1] - scaled_height/2
                
        
        
        mouse_position[0] /= truncate(ratio, 5)
        mouse_position[1] /= truncate(ratio, 5)
        
        
        direction = [0, 0]
        frame += 1
        pre_scaled.fill((25, 25, 75))
        
        
            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)
            if event.type == pg.MOUSEBUTTONDOWN:
                entity_list = platforms + powerups
                if player != []:
                    entity_list += [player]
                for thing in entity_list:
                    temp_rect = pg.Rect(thing.location, [thing.width, thing.height])
                    
                    if temp_rect.collidepoint(mouse_position):
                        for item in allowed_objects:
                            if item.id == thing.id:
                                
                                selected_object = thing
                                selected_object.tags += "-no_collide-"
                                selected_offset = [mouse_position[0] - selected_object.location[0], mouse_position[1] - selected_object.location[1]]
                            
                                break
                
                if selected_object == None:
                    start_x = 20
                    i = 0
                    for image in allowed_images:
                        center = image.get_height()/2
                        image_rect = pg.Rect([start_x + (100 * i), 50 - center], [80, 80])
                        
                        if image_rect.collidepoint(mouse_position) and allowed_objects[allowed_images[image]] > 0:
                            selected_object = deepcopy(allowed_images[image])
                            allowed_objects[allowed_images[image]] -= 1
                            selected_object.tags += "-no_collide-"
                            if isinstance(allowed_images[image], Player) and player == []:
                                player.append(selected_object)
                                player = player[0]
                            
                            elif isinstance(allowed_images[image], Platform):
                                platforms.append(selected_object)
                            
                            elif isinstance(allowed_images[image], PowerUp):
                                powerups.append(selected_object)
                                
                        
                        i += 1
                
                  
            if event.type == pg.MOUSEBUTTONUP:
                if pg.mouse.get_just_released()[0]:
                    start_x = 20
                    i = 0
                    for image in allowed_images:
                        center = image.get_height()/2
                        image_rect = pg.Rect([start_x + (100 * i), 50 - center], [80, 80])
                        
                        if image_rect.collidepoint(mouse_position) and selected_object != None:
                            if allowed_images[image].id == selected_object.id:
                                allowed_objects[allowed_images[image]] += 1
                                
                                if isinstance(selected_object, Player):
                                    player = []
                                elif isinstance(selected_object, Platform):
                                    platforms.remove(selected_object)
                                elif isinstance(selected_object, PowerUp):
                                    powerups.remove(selected_object)
                
                        i += 1
                    
                    for power_up in powerups:
                        if power_up.type == 3 and selected_object != None:
                            selected_rect = pg.Rect(selected_object.location, [selected_object.width, selected_object.height])
                            illegal_rect = pg.Rect(power_up.location, [power_up.width, power_up.height])
                            
                            if selected_rect.colliderect(illegal_rect):
                                for image in allowed_images:
                                    
                                    if allowed_images[image].id == selected_object.id:
                                        allowed_objects[allowed_images[image]] += 1
                                        
                                        if isinstance(selected_object, Player):
                                            player = []
                                        elif isinstance(selected_object, Platform):
                                            platforms.remove(selected_object)
                                        elif isinstance(selected_object, PowerUp):
                                            powerups.remove(selected_object)
                
                if selected_object != None:
                    selected_object.tags = selected_object.tags.replace("-no_collide-", "")
                selected_object = None
        if  player != []:       
            if player.dead == False and not player == selected_object:
                try:
                    if pg.key.get_pressed()[key_bindings["left"]]:
                        if direction[0] == 1:
                            direction[0] -=2
                            player.flow_mult = 1
                        else:
                            direction[0] -=1
                        try:
                            if held_keys[key_bindings["left"]] == frame - 1:
                                player.speed[0] *= 1.0001
                            else:
                                player.speed[0] = -3
                                
                        except KeyError:
                            player.speed[0] = -3
                        
                        held_keys[key_bindings["left"]] = frame
                except TypeError:
                    if pg.mouse.get_pressed()[int(key_bindings["left"][-1])]:
                        if direction[0] == 1:
                            direction[0] -=2
                            player.flow_mult = 1
                        else:
                            direction[0] -=1
                        try:
                            if held_keys[key_bindings["left"]] == frame - 1:
                                player.speed[0] *= 1.0001
                            else:
                                player.speed[0] = -3
                                
                        except KeyError:
                            player.speed[0] = -3
                        
                        held_keys[key_bindings["left"]] = frame
                                            
                
                try:    
                    if pg.key.get_pressed()[key_bindings["right"]]:
                        if direction[0] == -1:
                            direction[0] +=2
                            player.flow_mult = 1
                        else:
                            direction[0] +=1
                        direction[0] += 1
                        try:
                            if held_keys[key_bindings["right"]] == frame - 1:
                                player.speed[0] *= 1.0001
                            else:
                                player.speed[0] = 3
                                
                        except KeyError:
                            player.speed[0] = 3
                        
                        held_keys[key_bindings["right"]] = frame
                except TypeError:
                    if pg.mouse.get_pressed()[int(key_bindings["right"][-1])]:
                        if direction[0] == -1:
                            direction[0] +=2
                            player.flow_mult = 1
                        else:
                            direction[0] +=1
                        try:
                            if held_keys[key_bindings["right"]] == frame - 1:
                                player.speed[0] *= 1.0001
                            else:
                                player.speed[0] = 3
                                
                        except KeyError:
                            player.speed[0] = 3
                        
                        held_keys[key_bindings["right"]] = frame
                if direction == [0, 0]:
                    player.speed[0] = 0
                
                try:
                    
                    if pg.key.get_pressed()[key_bindings["jump"]]:
                        direction[1] -= 1
                    if pg.key.get_just_pressed()[key_bindings["jump"]]:
                        if player.jump_enabled and player.jump_allowed:
                            player.speed[1] = min(player.speed[1], 0)
                            player.speed[1] -= 4
                            player.jump_allowed = False
                            player.on_ground = False
                            player.cayote_timer = 0
                except TypeError:
                    if pg.mouse.get_pressed()[int(key_bindings["jump"][-1])]:
                        direction[1] -= 1
                    if pg.mouse.get_just_pressed()[int(key_bindings["jump"][-1])]:
                        if player.jump_enabled and player.jump_allowed:
                            player.speed[1] = min(player.speed[1], 0)
                            player.speed[1] -= 4
                            player.jump_allowed = False
                            player.on_ground = False
                            player.cayote_timer = 0
                try:
                    
                    if pg.key.get_pressed()[key_bindings["crouch"]]:
                        direction[1] += 1
                        player.crouched = True
                    else:
                        player.crouched = False
                
                except TypeError:
                    if pg.mouse.get_pressed()[int(key_bindings["crouch"][-1])]:
                        direction[1] += 1
                        player.crouched = True
                    else:
                        player.crouched = False
                
                    
                try:
                    if pg.key.get_pressed()[key_bindings["dash"]]:
                        if player.dashes > 0 and player.dash_timer == -1 and vector_magnitude(direction):
                            player.dashes -= 1
                            player.dash_timer = 0
                            player.speed[1] = 0
                            
                            direction = normalise(direction)
                            
                            player.dash_speed[0] += 10*direction[0]
                            player.dash_speed[1] += 10*direction[1]
                except TypeError:
                    if pg.mouse.get_pressed()[int(key_bindings["dash"][-1])]:
                        if player.dashes > 0 and vector_magnitude(direction) > 0 and player.dash_timer == -1:
                            player.dashes -= 1
                            player.dash_timer = 0
                            player.speed[1] = 0
                            
                            direction = normalise(direction)
                            
                            player.dash_speed[0] += 10*direction[0]
                            player.dash_speed[1] += 10*direction[1]
            
            if player.dead == True:
                level_text = {}
                font = pg.font.SysFont("Comic Sans", 50)
                
                temp = font.render("Press " + key_names["reset"].title() + " to Reset", True, (180, 200, 180))
                    
                level_text[temp] = [40000, 99999]
            
        try:
            if pg.key.get_pressed()[key_bindings["reset"]]:
                temp = deepcopy(screen.get_surface())
                temp = pg.transform.scale(temp, [1280, 720])
                stage_transition_animation(temp)
                level_text = {}
                font = pg.font.SysFont("Comic Sans", 50)
                temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
                level_text[temp] = [5, 5]
                    
        except TypeError:
            if isinstance(key_bindings["reset"], str):
                if pg.mouse.get_pressed()[int(key_bindings["reset"][-1])]:
                    temp = deepcopy(screen.get_surface())
                    temp = pg.transform.scale(temp, [1280, 720])
                    stage_transition_animation(temp)
                    level_text = {}
                    font = pg.font.SysFont("Comic Sans", 50)
                    temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
                    level_text[temp] = [5, 5]                    
                    
        try:
            if pg.key.get_just_pressed()[key_bindings["menu"]]:
                menu(True)
                current_time = time.time()
                d_time = 1/framerate
                previous_time = current_time                
                    
        except TypeError:
            if isinstance(key_bindings["menu"], str):
                if pg.mouse.get_just_pressed()[int(key_bindings["menu"][-1])]:
                    menu(True)
                    current_time = time.time()
                    d_time = 1/framerate
                    previous_time = current_time
                
        for star in level_stars:
            temp_star = deepcopy(power_images["star_idle"]["1"])
            temp_star = pg.transform.scale(temp_star, [level_stars[star]["size"], level_stars[star]["size"]])
            temp = pg.Surface([level_stars[star]["size"], level_stars[star]["size"]], pg.SRCALPHA)
            temp.blit(temp_star)
            temp = pg.transform.rotate(temp, level_stars[star]["angle"])
            
            if level_stars[star]["direction"] == 0: # Counter Clockwise
                level_stars[star]["angle"] -= level_stars[star]["speed"] * d_time * 60
                
            elif level_stars[star]["direction"] == 1: # Clockwise
                level_stars[star]["angle"] += level_stars[star]["speed"] * d_time * 60
                    
            if level_stars[star]["growth_phase"] == 0: # Shrinking
                level_stars[star]["size"] -= level_stars[star]["speed"] * d_time / 7.5 * 10
                
                if level_stars[star]["size"] <= 10:
                    level_stars[star]["size"] = 10
                    level_stars[star]["growth_phase"] = 1
                
            elif level_stars[star]["growth_phase"] == 1: # Growing
                level_stars[star]["size"] += level_stars[star]["speed"] * d_time / 7.5 * 10
                
                if level_stars[star]["size"] >= 20:
                    level_stars[star]["size"] = 20
                    level_stars[star]["growth_phase"] = 0
                    
            draw_location = [level_stars[star]["location"][0] - temp.get_width()/2, level_stars[star]["location"][1] - temp.get_height()/2]
            
            if player != []:
                if not "-no_collide-" in player.tags:
                    if level_stars[star]["layer"] == 3:
                        level_stars[star]["location"][0] += -(player.speed[0] + player.dash_speed[0])*d_time*12
                        level_stars[star]["location"][1] += -(player.speed[1] + player.dash_speed[1])*d_time*12
                    elif level_stars[star]["layer"] == 2:
                        level_stars[star]["location"][0] += -(player.speed[0] + player.dash_speed[0])*d_time*6
                        level_stars[star]["location"][1] += -(player.speed[1] + player.dash_speed[1])*d_time*6
                    elif level_stars[star]["layer"] == 1:
                        level_stars[star]["location"][0] += -(player.speed[0] + player.dash_speed[0])*d_time*3
                        level_stars[star]["location"][1] += -(player.speed[1] + player.dash_speed[1])*d_time*3
                        
                if level_stars[star]["location"][0] < 0:
                    level_stars[star]["location"][0] = pre_scaled.width
                elif level_stars[star]["location"][0] > pre_scaled.width:
                    level_stars[star]["location"][0] = 0
                    
                if level_stars[star]["location"][1] < 0:
                    level_stars[star]["location"][1] = pre_scaled.height
                elif level_stars[star]["location"][1] > pre_scaled.height:
                    level_stars[star]["location"][1] = 0
                
            
            pre_scaled.blit(temp, draw_location)
        
                            
        if selected_object != None:
            selected_object.location = [mouse_position[0], mouse_position[1]]
            selected_object.location[0] -= selected_offset[0]
            selected_object.location[1] -= selected_offset[1]
            selected_object.centre = [selected_object.location[0] + selected_object.width/2, selected_object.location[1] + selected_object.height/2]
            if isinstance(selected_object, Platform) or isinstance(selected_object, Player):
                selected_object.start = [selected_object.location[0], selected_object.location[1]]
              
        if player != []:
            player.draw(pre_scaled)
            player.update(platforms+powerups, d_time)
            
            if player.flow_mult > 0:
                flow_ratio = ((player.flow_mult-1)/5)*100
                
                music_offset = -flow_ratio
                music_channel.set_volume(((master_volume*music_volume)+music_offset)/100)
                vignette_alpha =  min(0.9*vignette_alpha + 0.1*max(min(50*flow_ratio, 255), 0), 200)
                cutout_size[0] = max(0.1*(1280*(1-flow_ratio/40) ) + (0.9*cutout_size[0]), 0.75*1280)
                cutout_size[1] = max(0.1*(720*(1-flow_ratio/40)) + (0.9*cutout_size[1]), 0.75*720)
                # print(flow_ratio, vignette_alpha)
        
        vignette.fill((100, 255, 100, vignette_alpha))
        pg.draw.ellipse(vignette, (0, 0, 0, 0), [[640 - (cutout_size[0]/2), 360 - (cutout_size[1]/2)], cutout_size])
        vignette = smooth_blur(vignette, vignette_strength/5)
        vignette = smooth_blur(vignette, vignette_strength/5)
        vignette = smooth_blur(vignette, vignette_strength/5)
        vignette = smooth_blur(vignette, vignette_strength/5)
        vignette = smooth_blur(vignette, vignette_strength/5)
                    
        for platform in platforms:
            platform.draw(pre_scaled)
            platform.update()
        
        allowed_images = {}
        for thing in allowed_objects:
            temp_surface = pg.Surface([thing.width, thing.height])
            thing.location = [0, 0]
            if allowed_objects[thing] == 0:
                temp_surface.fill((70, 70, 70))
            else:
                thing.draw(temp_surface)
            ratio = 80 / max(thing.width, thing.height) 
            temp_surface = pg.transform.scale_by(temp_surface, ratio)
            allowed_images[temp_surface] = thing
        
        start_x = 20
        i = 0
        for image in allowed_images:
                
            center = image.get_height()/2
            pre_scaled.blit(image, [start_x + (100 * i), 50 - center])
            font = pg.font.SysFont("Comic Sans", 20)
            number = allowed_objects[allowed_images[image]]
            number = font.render(str(number), True, (180, 200, 180))
            pre_scaled.blit(number, [start_x + (100 * i) + (80 - number.get_width()), (50 - center) + image.get_height()])
            i += 1
        
        
        for power in powerups:
            power.draw(pre_scaled)
            
        
        pre_scaled.blit(vignette)
        
        to_remove = []
        for name in level_text:
            if level_text[name][0] > 0:
                
                if level_text[name][0] > 0.4*level_text[name][1]:
                    name.set_alpha((1-(level_text[name][0]/level_text[name][1]))*425)
                else:
                    name.set_alpha(((level_text[name][0]/level_text[name][1]))*628)
                
                pre_scaled.blit(name, [(0.5*1280) - (name.get_width()/2), (0.5*720) - (name.get_height()/2)])
                level_text[name][0] -= d_time
            
            else:
                to_remove.append(name)
                
        for i in to_remove:
            level_text.pop(i)
            
        
        # Scaling to actual display
        ratio = min(screen_width/1280, screen_height/720)
        
        scaled_width = int(1280 * ratio)
        scaled_height = int(720 * ratio)
        
        pre_scaled = pg.transform.scale(pre_scaled, [scaled_width, scaled_height])
        center = [screen_width//2, screen_height//2]
        
        screen.get_surface().blit(pre_scaled, [center[0] - scaled_width/2, center[1] - scaled_height/2])
            
        screen.flip()
        clock.tick(framerate)
        
        current_time = time.time()
        d_time = current_time - previous_time
        previous_time = current_time
        
        # Handling Music replay
        
        if music_channel.get_busy() == False:
            global current_track
            current_track = choice(list(music.keys()))
            segment = str(randint(1, 5))
            music_channel.set_volume(master_volume*music_volume/100)
            music_channel.play(music[current_track][segment])
        

menu(True)
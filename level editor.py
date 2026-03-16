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
    
    title = "PlaceHolder Level Editor"
    font = pg.font.SysFont("Comic Sans", 50)
    title = font.render(title, True, (180, 200, 180))
    
    outer = (50, 100, 50)
    inner = (50, 50, 100)
    
    if saveable == True:
        if cont == True:
            title_menu = {"new_game":button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Continue"),
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
        key_menu[key] = button(screen, 0.25, 0.1, [0.5, 0.3 + key_count*0.15], outer, inner, " "+key.capitalize()+": "+key_names[key].capitalize()+" ")
        key_count += 1
    
    
    save_count = 0
    saves = []
    for file in os.listdir("levels"):
        if file.endswith(".lvl"):
            save_count += 1
            saves.append(file)
    
    
    load_menu = {"back_tm": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  ")}
    for i in range(save_count):
        load_menu[saves[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], outer, inner, saves[i].removesuffix(".lvl"))
        
    
    display_menu = {"back_om": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  "),
                    "fullscreen": button(screen, 0.25, 0.1, [0.5, 0.3], outer, inner, "Fullscreen: " + str(fullscreen)),
                    "framerate": button(screen, 0.25, 0.2, [0.5, 0.50], outer, inner, "Framerate: " + framerate_text, slider=True, slider_max = 145, slider_min = 0, slider_value = framerate, slider_colour = (147, 107, 15)),
                    "resolution": button(screen, 0.25, 0.1, [0.5, 0.70], outer, inner, "Resolution: " + str(int(round(screen_width*1.5, 0))) + "X" + str(int(round(screen_height*1.5, 0)))),
    }
    if framerate_text == "Unlimited":
        display_menu["framerate"].slider_value = 145
    if framerate_text == "Vsync":
        display_menu["framerate"].slider_value = 0
    
    
    current_menu = title_menu
    
    end = False
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
                    
            if current_menu == load_menu:
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
                quit()
                
            if pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]:
                for event in events:
                    
                    if current_menu[item].get_focused(mouse_pos):
                        sound = choice(["", "1", "2"])
                        other_sounds["click" + sound].play()
                        
                        if item == "new_game":
                            if cont == False:
                                main()
                            else:
                                end = True

                        elif item == "quit":
                            quit()
                            
                        elif item == "options":
                            current_menu = options_menu
                            changed_menu = True
                          
                        elif item == "load":
                            changed_menu = True
                            current_menu = load_menu
                            
                        elif item == "back_tm":
                            current_menu = title_menu
                            changed_menu = True
                            
                        elif item == "controls":
                            current_menu = key_menu
                            changed_menu = True
                        
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
                                    current_menu[item].text = " " + item.capitalize() + ": " + "Left Click" + " "
                                elif mouse_button == 1:
                                    current_menu[item].text = " " + item.capitalize() + ": " + "Middle Click" + " "
                                elif mouse_button == 2:
                                    current_menu[item].text = " " + item.capitalize() + ": " + "Right Click" + " "
                                else:
                                    current_menu[item].text = " " + item.capitalize() + ": " + "mouse button "+str(mouse_button) + " "
                            else:
                                key_bindings[item] = key
                                current_menu[item].text = " " + item.capitalize() + ": " + pg.key.name(key).capitalize() + " "
                            
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
                            save = open("levels\\"+item, "rb")
                            load(save)
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
                                    quit()
                                
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
                                            save = open("levels\\"+save_name+".lvl", "wb")
                                            
                                            to_remove = []
                                            for thing in allowed_objects.keys():
                                                
                                                if allowed_objects[thing] == 0:
                                                    to_remove.append(thing)
                                            
                                            for thing in to_remove:
                                                allowed_objects.pop(thing)
                                            
                                            data = [platforms, powerups, player, allowed_objects]
                                            
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
                                
                                screen_width, screen_height = screen_width/1.5, screen_height/1.5
                                
                                screen.size = [screen_width, screen_height]
                                screen.position = ((moniter_width/2) - (screen_width/2), (moniter_height/2) - (screen_height/2))
                            else: 
                                temp = pg.display.Info()
                            
                                moniter_width, moniter_height = temp.current_w, temp.current_h
                                
                                screen.size = [moniter_width, moniter_height]
                                screen.position = (0, 0)
                                screen_height = screen_height
                                screen_width = screen_width
                                
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
            
            else:
                if current_menu[item].get_focused(mouse_pos):
                    current_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                    current_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                        
                else:
                    current_menu[item].outer_colour = outer
                    current_menu[item].inner_colour = inner
                            
            for event in pg.event.get(pg.KEYDOWN):
                                       
                if event.key == key_bindings["menu"]:
                    if cont == True:
                        end = True
                                                                                 
                
        screen.flip()
        
class Platform:
    def __init__(self, location, width, height, type = 0):
        self.location = list(location)
        self.width = width
        self.height = height
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        self.type = type
        self.start = [self.location[0], self.location[1]]
        self.offset = [0, 0]
        
        self.passengers = []
        
        self.tags = ""
        self.id = (randint(1, 12_090_070)/ randint(1, 1350)) * randint(1, 1091)
        
        self.frame = 1
        
    def draw(self):
        if self.type == 0:
            pg.draw.rect(screen.get_surface(), (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 1:
            pg.draw.rect(screen.get_surface(), (240, 50, 240), (self.location, (self.width, self.height)))
        elif self.type == 2:
            pg.draw.rect(screen.get_surface(), (150, 0, 0), (self.location, (self.width, self.height)))
        elif self.type == 3:
            pg.draw.rect(screen.get_surface(), (50, 50, 50), (self.location, (self.width, self.height)))
        elif self.type == 4:
            pg.draw.rect(screen.get_surface(), (50, 240, 50), (self.location, (self.width, self.height)))
        elif self.type == 5:
            pg.draw.rect(screen.get_surface(), (255, 150, 150), (self.location, (self.width, self.height)))
        
    
class Player:
    def __init__(self, location):
        self.location = list(location)
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
        
        self.frame = 1
        
    def draw(self):
        pg.draw.rect(screen.get_surface(), (220, 255, 220), (self.location, (self.width, self.height)))
    
    def collide(self, entity):
        entity_rect = pg.Rect(entity.location[0], entity.location[1], entity.width, entity.height)
        points = [self.location, [self.location[0] + self.width, self. location[1]], [self.location[0] + self.width, self.location[1] + self.height], [self.location[0], self.location[1] + self.height]]
        
        for point in points:
            if entity_rect.collidepoint(point[0], point[1]):
                return True
            
        return False
    
    def update(self, entity_list, d_time):
        self.cayote_timer += d_time
        
        
        if self.dash_timer >= 0:
            self.dash_timer += d_time
        else:
            self.speed[1] += 0.1
            
        if self.dash_timer >= 0.17:
            self.speed[1] += 0.1
            self.dash_speed[0] *= 0.8
            self.dash_speed[1] *= 0.8
            self.dash_speed[0] = truncate(self.dash_speed[0], 1)
            self.dash_speed[1] = truncate(self.dash_speed[1], 1)
            
            if vector_magnitude(self.dash_speed) == 0:
                self.dash_timer = -1
                
        self.location[0] += self.speed[0]
        self.location[1] += self.speed[1]
        self.location[0] += self.dash_speed[0]
        self.location[1] += self.dash_speed[1]
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        
        if self.cayote_timer >= 0.204:
            self.on_ground = False
            self.cayote_timer = 0
            
        if self.crouched == True:
            if self.height == 55:
                if self.on_ground:
                    self.location[1] += 15
                
                self.height = 40
        else:
            self.height = 55
        
        for entity in entity_list:
            if self.collide(entity):
                x_diff = self.centre[0] - entity.centre[0]
                y_diff = self.centre[1] - entity.centre[1]
                
                if (entity.width/2 + self.width/2 + 1) - abs(x_diff) < (entity.height/2 + self.height/2 + 1) - abs(y_diff):
                    if x_diff < 0:
                        self.location[0] -= (entity.width/2 + self.width/2) - abs(x_diff)
                    else:
                        self.location[0] += (entity.width/2 + self.width/2 ) - abs(x_diff)

                else:
                    if y_diff < 0:
                        self.location[1] -= (entity.height/2 + self.height/2 + 1) - abs(y_diff)
                        self.on_ground = True
                        self.cayote_timer = 0
                        self.speed[1] = 0
                    else:
                        self.location[1] += (entity.height/2 + self.height/2 + 1) - abs(y_diff)
                        
                        
                        
        if self.on_ground:
            if self.dash_timer == -1:
                self.dashes = self.max_dashes
            self.jump_allowed = True
        else:
            self.jump_allowed = False
        
class PowerUp:
    def __init__(self, location, type):
        self.location = list(location)
        self.type = type
        self.width = 30
        self.height = 30
        self.centre = [self.location[0] + self.width/2, self.location[1] + self.height/2]
        self.tags = ""
        self.id = (randint(1, 12_090_070)/ randint(1, 1350)) * randint(1, 1091)
        
        self.offset = [0, 0]
        
        self.frame = 1
        
    def draw(self):
        if self.type == 0:
            pg.draw.rect(screen.get_surface(), (255, 200, 200), (self.location, (self.width, self.height)))
        elif self.type == 1:
            pg.draw.rect(screen.get_surface(), (255, 100, 255), (self.location, (self.width, self.height)))
        elif self.type == 2:
            pg.draw.rect(screen.get_surface(), (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 3:
            temp = pg.Surface([self.width, self.height], pg.SRCALPHA)
            pg.draw.rect(temp, (240, 150, 150, 100), ([0, 0], (self.width, self.height)))
            screen.get_surface().blit(temp, self.location)
        elif self.type == 4:
            temp = pg.Surface([self.width, self.height], pg.SRCALPHA)
            pg.draw.rect(temp, (240, 240, 240, 100), ([0, 0], (self.width, self.height)))
            screen.get_surface().blit(temp, self.location)
        elif self.type == 5:
            pg.draw.rect(screen.get_surface(), (255, 255, 200), (self.location, (self.width, self.height)))
      
platforms = []
powerups = []
player = []
allowed_objects = {}  
        
def main():
    global platforms
    global powerups
    global player
    global allowed_objects
    global cont
    
    cont = True
    
    selected_objects = []
    selected_object = None
    selected_offset = [0, 0]
    allow_amount = 1
    selected_width = 1
    selected_height = 1
    selected_type = 0
    
    target_x_offset = 0
    target_y_offset = 0
    
    
    outer = (50, 100, 50)
    inner = (50, 50, 100)
    
    place_menu = {"player": button(screen, 0.2, 0.1, [0.1, 0.05], outer, inner, "Player", radius=0),
                  "platform": button(screen, 0.2, 0.1, [0.3, 0.05], outer, inner, "Platform", radius=0),
                  "power_up": button(screen, 0.2, 0.1, [0.5, 0.05], outer, inner, "Power Up", radius=0),
                  "clear": button(screen, 0.2, 0.1, [0.7, 0.05], outer, inner, "Clear Allowed", radius=0),
                  "remove": button(screen, 0.1, 0.15, [0.9, 0.05], outer, inner, "[X]", radius=0)}
    
    open_menus = [place_menu]
    menu_position = [0, 0]
    
    while True:
        mouse_position = pg.mouse.get_pos()
        menu_position = mouse_position
    
        select_menu = {"allow": button(screen, 0.2, 0.1, [(menu_position[0]/screen_width) - 0.2, menu_position[1]/screen_height], outer, inner, "Allow Placement", radius=0),
                       "width": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.15], outer, inner, "Width: " + str(selected_width), slider = True, slider_max = 500, slider_min = 1, slider_value = selected_width, slider_colour = (147, 107, 15), radius=0),
                       "height": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.35], outer, inner, "Height: " + str(selected_height), slider = True, slider_max = 500, slider_min = 1, slider_value = selected_height, slider_colour = (147, 107, 15), radius=0),
                       "type": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.55], outer, inner, "Type: " + str(selected_type), slider = True, slider_max = 5, slider_min = 0, slider_value = selected_type, slider_colour = (147, 107, 15), radius=0),
                       "target": button(screen, 0.2, 0.1, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.65], outer, inner, "Change Target", radius=0)}
        
        target_menu = {"target_x": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)], outer, inner, "X Offset" + str(target_x_offset), slider = True, slider_max = 500, slider_min = -500, slider_value = target_x_offset, slider_colour = (147, 107, 15), radius=0),
                       "target_y": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.15], outer, inner, "Y Offset: " + str(target_y_offset), slider = True, slider_max = 500, slider_min = -500, slider_value = target_y_offset, slider_colour = (147, 107, 15), radius=0)}
        
        cam_menu = {"target_x": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)], outer, inner, "X Offset" + str(target_x_offset), slider = True, slider_max = 1, slider_min = -1, slider_value = target_x_offset, slider_colour = (147, 107, 15), radius=0),
                       "target_y": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width) - 0.2, (menu_position[1]/screen_height)+0.15], outer, inner, "Y Offset: " + str(target_y_offset), slider = True, slider_max = 1, slider_min = -1, slider_value = target_y_offset, slider_colour = (147, 107, 15), radius=0)}

        allow_menu = {"number": button(screen, 0.2, 0.2, [(menu_position[0]/screen_width), menu_position[1]/screen_height], outer, inner, "Number: " + str(allow_amount), slider = True, slider_max = 10, slider_min = 0, slider_value = allow_amount, slider_colour = (147, 107, 15), radius=0)}
    
        if selected_object != None:
            selected_object.location = [mouse_position[0], mouse_position[1]]
            selected_object.location[0] -= selected_offset[0]
            selected_object.location[1] -= selected_offset[1]
            selected_object.centre = [selected_object.location[0] + selected_object.width/2, selected_object.location[1] + selected_object.height/2]
            if isinstance(selected_object, Platform) or isinstance(selected_object, Player):
                selected_object.start = [selected_object.location[0], selected_object.location[1]]
        
        
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a and pg.key.get_mods() & pg.KMOD_CTRL:
                    selected_objects = platforms + powerups + player
                if event.key == pg.K_c and pg.key.get_mods() & pg.KMOD_CTRL:
                    new_objects = []
                    for entity in selected_objects:
                        if isinstance(entity, Player):
                            continue
                        temp = deepcopy(entity)
                        temp.id = (randint(1, 12_090_070)/ randint(1, 1350)) * randint(1, 1091)
                        new_objects.append(temp)
                        
                    for entity in new_objects:
                        if isinstance(entity, Platform):
                            platforms.append(entity)
                            
                        elif isinstance(entity, PowerUp):
                            powerups.append(entity)
                            
                    selected_objects = new_objects
                    
                if event.key == pg.K_DELETE:
                    for entity in selected_objects:
                        if isinstance(entity, Player):
                            player.remove(entity)
                        if isinstance(entity, Platform):
                            platforms.remove(entity)
                        if isinstance(entity, PowerUp):
                            powerups.remove(entity)
                        
            
            if event.type == pg.MOUSEBUTTONDOWN:
                
                if pg.mouse.get_pressed()[0]:
                   
                    for open_menu in open_menus:
                        for item in open_menu:
                            if open_menu[item].get_focused(mouse_position):
                                if item == "player" and player == []:
                                    selected_object = Player(mouse_position)
                                    player.append(selected_object)
                                
                                elif item == "platform":
                                    selected_object = Platform(mouse_position, 100, 50)
                                    platforms.append(selected_object)
                                
                                elif item == "power_up":
                                    selected_object = PowerUp(mouse_position, 0)
                                    powerups.append(selected_object)
                                
                                else:
                                    selected_object = None
                                    
                                    
                                   
                    for entity in platforms + powerups + player:
                        temp_rect = pg.Rect(entity.location[0], entity.location[1], entity.width, entity.height)
                        if temp_rect.collidepoint(mouse_position):
                            selected_object = entity
                            selected_offset = [mouse_position[0] - selected_object.location[0], mouse_position[1] - selected_object.location[1]]
                        
                if pg.mouse.get_just_pressed()[2]:
                    select_start = mouse_position
                    
            if event.type == pg.MOUSEMOTION:
                new_pos = pg.mouse.get_rel()
                if pg.mouse.get_pressed()[0] and len(selected_objects) > 1:
                    for entity in selected_objects:
                        entity.location[0] += new_pos[0]
                        entity.location[1] += new_pos[1]
                        entity.centre = [entity.location[0] + entity.width/2, entity.location[1] + entity.height/2]
                        if isinstance(entity, Platform) or isinstance(entity, Player):
                            entity.start = [entity.location[0], entity.location[1]]
                                
                for open_menu in open_menus:
                        for item in open_menu:
                            if open_menu[item].get_focused(mouse_position) and (pg.mouse.get_pressed(5)[0] or pg.mouse.get_pressed(5)[2]):
                                
                                if item == "width" and len(selected_objects) == 1 and selected_object == None:
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None:
                                        selected_width = int(temp[1])
                                        open_menu[item].slider_value = selected_width
                                        open_menu[item].text = "Width: " + str(int(selected_width))
                                        selected_objects[0].width = selected_width
                                        
                                if item == "height" and len(selected_objects) == 1 and selected_object == None:
                                    
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None:
                                        selected_height = int(temp[1])
                                        open_menu[item].slider_value = selected_height
                                        open_menu[item].text = "Height: " + str(int(selected_height))
                                        selected_objects[0].height = selected_height
                                        
                                if item == "type" and len(selected_objects) == 1 and selected_object == None:
                                    
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None:
                                        selected_type = int(temp[1])
                                        
                                        if isinstance(selected_objects[0], PowerUp):
                                            selected_objects[0].type = selected_type
                                            
                                        elif isinstance(selected_objects[0], Platform):
                                            selected_objects[0].type = selected_type
                                        
                                        else:
                                            selected_type = 0
                                            
                                        open_menu[item].slider_value = selected_type
                                        open_menu[item].text = "Type: " + str(int(selected_type))
                                        
                                if item == "number" and len(selected_objects) == 1 and selected_object == None:
                                    
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None:
                                        allow_amount = int(temp[1])
                                        open_menu[item].slider_value = allow_amount
                                        open_menu[item].text = "Number: " + str(int(allow_amount))
                                        allowed_objects[selected_objects[0]] = allow_amount
                                        
                                if item == "target_x" and len(selected_objects) == 1 and selected_object == None:
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None and isinstance(selected_objects[0], Platform):
                                        target_x_offset = int(temp[1])
                                        open_menu[item].slider_value = target_x_offset
                                        open_menu[item].text = "X Offset: " + str(int(target_x_offset))
                                        selected_objects[0].offset[0] = target_x_offset
                                        
                                    elif temp[1] != None and isinstance(selected_objects[0], PowerUp):
                                        target_x_offset = temp[1]
                                        open_menu[item].slider_value = target_x_offset
                                        open_menu[item].text = "X Offset: " + str(truncate(target_x_offset, 2))
                                        selected_objects[0].offset[0] = target_x_offset*screen_width
                                        
                                if item == "target_y" and len(selected_objects) == 1 and selected_object == None:
                                    temp = open_menu[item].get_focused(mouse_position)
                                    
                                    if temp[0]:
                                        open_menu[item].outer_colour = min(outer[0]*1.1, 255), min(outer[1]*1.1, 255), min(outer[2]*1.1, 255)
                                        open_menu[item].inner_colour = min(inner[0]*1.1, 255), min(inner[1]*1.1, 255), min(inner[2]*1.1, 255)
                                            
                                    else:
                                        open_menu[item].outer_colour = outer
                                        open_menu[item].inner_colour = inner
                                    
                                    if temp[1] != None and isinstance(selected_objects[0], Platform):
                                        target_y_offset = int(temp[1])
                                        open_menu[item].slider_value = target_y_offset
                                        open_menu[item].text = "Y Offset: " + str(int(target_y_offset))
                                        selected_objects[0].offset[1] = target_y_offset
                                    
                                    elif temp[1] != None and isinstance(selected_objects[0], PowerUp):
                                        target_y_offset = temp[1]
                                        open_menu[item].slider_value = target_y_offset
                                        open_menu[item].text = "Y Offset: " + str(truncate(target_y_offset, 2))
                                        selected_objects[0].offset[1] = target_y_offset*screen_height
                                        
                    
            if event.type == pg.MOUSEBUTTONUP:
                if pg.mouse.get_just_released()[0]:
                    for open_menu in open_menus:
                        for item in open_menu:
                            if open_menu[item].get_focused(mouse_position):
                                if item == "remove":
                                    if isinstance(selected_object, Player):
                                        player.remove(selected_object)
                                    elif isinstance(selected_object, Platform):
                                        platforms.remove(selected_object)
                                    elif isinstance(selected_object, PowerUp):
                                        powerups.remove(selected_object)
                                        
                                if item == "clear":
                                    allowed_objects = {}
                                    
                                if item == "allow":
                                    menu_to_remove = None
                                    for temp_menu in open_menus:
                                        if "number" in temp_menu:
                                            menu_to_remove = temp_menu
                                            break
                                    if menu_to_remove != None:
                                        open_menus.remove(menu_to_remove)
                                    allow_menu["number"].center[0] = open_menu[item].center[0]+0.2
                                    open_menus.append(allow_menu)
                                
                                    if selected_objects[0] in allowed_objects:
                                        allow_amount = allowed_objects[selected_objects[0]]
                                        
                                    allowed_objects[selected_objects[0]] = allow_amount
                                     
                                if item == "target" and isinstance(selected_objects[0], Platform):   
                                    menu_to_remove = None
                                    for temp_menu in open_menus:
                                        if "target_x" in temp_menu:
                                            menu_to_remove = temp_menu
                                            break
                                    if menu_to_remove != None:
                                        open_menus.remove(menu_to_remove)
                                    target_menu["target_x"].center[0] = open_menu[item].center[0]+0.2
                                    target_menu["target_x"].center[1] = open_menu["allow"].center[1]
                                    target_menu["target_y"].center[0] = open_menu[item].center[0]+0.2
                                    target_menu["target_y"].center[1] = open_menu["allow"].center[1]+0.2
                                    open_menus.append(target_menu)
                                    
                                if item == "target" and isinstance(selected_objects[0], PowerUp):   
                                    menu_to_remove = None
                                    for temp_menu in open_menus:
                                        if "target_x" in temp_menu:
                                            menu_to_remove = temp_menu
                                            break
                                    if menu_to_remove != None:
                                        open_menus.remove(menu_to_remove)
                                    cam_menu["target_x"].center[0] = open_menu[item].center[0]+0.2
                                    cam_menu["target_x"].center[1] = open_menu["allow"].center[1]
                                    cam_menu["target_y"].center[0] = open_menu[item].center[0]+0.2
                                    cam_menu["target_y"].center[1] = open_menu["allow"].center[1]+0.2
                                    open_menus.append(cam_menu)
                                                               
                            
                    selected_object = None
                
                if pg.mouse.get_just_released()[2]:
                    
                    for temp_menu in open_menus:
                        menu_to_remove = None
                        if "number" in temp_menu:
                            menu_to_remove = temp_menu
                            break
                        if menu_to_remove != None:
                            open_menus.remove(menu_to_remove)
                    
                    select_end = mouse_position
                    selected_objects = []
                    selected_rect = pg.Rect(min(select_start[0], select_end[0]), min(select_start[1], select_end[1]), abs(select_start[0] - select_end[0]), abs(select_start[1] - select_end[1]))
                    
                    
                    for entity in platforms + powerups + player:
                        temp_rect = pg.Rect(entity.location[0], entity.location[1], entity.width, entity.height)
                        if temp_rect.colliderect(selected_rect):
                            selected_objects.append(entity)
                            
                    if len(selected_objects) == 1:
                        menu_to_remove = None
                        for open_menu in open_menus:
                            if "allow" in open_menu:
                                menu_to_remove = open_menu
                                break
                            
                        if menu_to_remove != None:
                            open_menus.remove(menu_to_remove)
                        open_menus.append(select_menu)
                     
            if event.type == pg.KEYDOWN:
                if event.key == key_bindings["menu"]:
                    menu(True)       
                if event.key == key_bindings["reset"]:
                    open_menus = [place_menu]
                    
                            
        screen.get_surface().fill((25, 25, 75))
        
        for open_menu in open_menus:
            for item in open_menu:
                open_menu[item].draw()
        
        for powerup in powerups:
            powerup.draw()
            
        for platform in platforms:
            platform.draw()
            
        for play_er in player:
            play_er.draw()
            
        screen.flip()
        
        clock.tick(framerate)

menu(True)
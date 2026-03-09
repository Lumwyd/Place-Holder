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
lion_images = {}
builder_images = {}
tiles = {}
items = {}
weapons = {}
other_images = {}
for image in os.walk("assets\\images"):
    
    if image[0] == "assets\\images\\lion":
        for frame in image[2]:
            lion_images[frame.removesuffix(".png")] = pg.image.load("assets\\images\\lion\\"+frame)
               
    elif image[0] == "assets\\images\\builder":
        for frame in image[2]:
            builder_images[frame.removesuffix(".png")] = pg.image.load("assets\\images\\builder\\"+frame)
    
    elif image[0] == "assets\\images\\tiles":
        for tile in image[2]:
            if len(tile.split("_")) > 1:
                root = tile.split("_")[0]
                extension = tile.removesuffix(".png").split("_")[1]
                
                try:
                    tiles[root][extension] = pg.image.load("assets\\images\\tiles\\"+tile)
                except KeyError:
                    tiles[root] = {}
                    tiles[root][extension] = pg.image.load("assets\\images\\tiles\\"+tile)
            else:
                tiles[tile.removesuffix(".png")] = pg.image.load("assets\\images\\tiles\\"+tile)
    
    elif image[0] == "assets\\images\\items":
        for item in image[2]:
                items[item.removesuffix(".png")] = pg.image.load("assets\\images\\items\\"+item)
    
    elif image[0] == "assets\\images\\weapons":
        for weapon in image[2]:
            if len(weapon.split("_")) > 1:
                root = weapon.split("_")[0]
                extension = weapon.removesuffix(".png").split("_")[1]
                
                try:
                    weapons[root][extension] = pg.image.load("assets\\images\\weapons\\"+weapon)
                except KeyError:
                    weapons[root] = {}
                    weapons[root][extension] = pg.image.load("assets\\images\\weapons\\"+weapon)
                    
    else:
        for o_i in image[2]:
            other_images[o_i.removesuffix(".png")] = pg.image.load("assets\\images\\"+o_i)
            
other_sounds = {}
builder_sounds = {}
lion_sounds = {}
for sound in os.walk("assets\\sounds"):
    
    if sound[0] == "assets\\sounds\\lion":
        for audio in sound[2]:
            lion_sounds[audio.removesuffix(".mp3")] = pg.mixer.Sound("assets\\sounds\\lion\\"+audio)
               
    elif sound[0] == "assets\\sounds\\builder":
        for audio in sound[2]:
            builder_sounds[audio.removesuffix(".mp3")] = pg.mixer.Sound("assets\\sounds\\builder\\"+audio)
    
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
    
    data = pickle.load(save)
    
    try:
       stars = data[0]
       level_number = data[1]
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
    
    title = "PlaceHolder"
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
    for file in os.listdir("saves"):
        if file.endswith(".sav"):
            save_count += 1
            saves.append(file)
    
    
    load_menu = {"back_tm": button(screen, 0.25, 0.1, [0.875, 0.05], outer, inner, "  Back  ")}
    for i in range(save_count):
        load_menu[saves[i]] = button(screen, 0.25, 0.1, [0.5, 0.3 + (i*0.15)], outer, inner, saves[i])
        
    
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
                            save = open("saves\\"+item, "rb")
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
                                            
                                            data = [stars, level]
                                            
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
        
    def draw(self, surface = screen.get_surface()):
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
            pg.draw.rect(surface, (255, 150, 150), (self.location, (self.width, self.height)))
        
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
        global text
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
                            self.location[1] -= (entity.height/2 + self.height/2) - abs(y_diff)
                            self.on_ground = True
                            if not self in entity.passengers:
                                entity.passengers.append(self)
                                
                            self.cayote_timer = 0
                            self.speed[1] = 0
                        else:
                            self.location[1] += (entity.height/2 + self.height/2) - abs(y_diff)
                    
                    if entity.type == 2:
                        self.dead = True
                    if entity.type == 5:
                        level += 1
                        for levels in os.walk("levels"):
                            for level in levels[2]:
                                if level.split("-")[0] == str(level_number):
                                    
                                    level_name = level.split("-")[1].removesuffix(".lvl")
                                    save = open("levels\\"+ level, "rb")
                                    load_level(save)
                                    text[temp] = [5, 5]
                                    break
                            
                elif isinstance(entity, PowerUp):
                    if entity.type == 0:
                        self.jump_enabled = True
                        self.jump_allowed = True
                        powerups.remove(entity)
                    elif entity.type == 1:
                        self.max_dashes += 1
                        self.dashes = self.max_dashes  
                        powerups.remove(entity)   
                    elif entity.type == 5:
                        stars[level] = True  
                        powerups.remove(entity)    
                    
        if self.on_ground:
            if self.dash_timer == -1:
                self.dashes = self.max_dashes
            self.jump_allowed = True
        else:
            self.jump_allowed = False
            
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
        
    def draw(self, surface = screen.get_surface()):
        if self.type == 0:
            pg.draw.rect(surface, (255, 200, 200), (self.location, (self.width, self.height)))
        elif self.type == 1:
            pg.draw.rect(surface, (255, 100, 255), (self.location, (self.width, self.height)))
        elif self.type == 2:
            pg.draw.rect(surface, (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 3:
            pg.draw.rect(surface, (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 4:
            pg.draw.rect(surface, (240, 240, 240), (self.location, (self.width, self.height)))
        elif self.type == 5:
            pg.draw.rect(surface, (255, 255, 200), (self.location, (self.width, self.height)))
        
       
global level_number
global stars

level_number = 2
stars = {}

global platforms
global powerups
global player
global allowed_objects

platforms = []
powerups = []
player = []
allowed_objects = {}
 
def main():
    
    global platforms
    global powerups
    global player
    global allowed_objects
    global text
    
    for levels in os.walk("levels"):
        for level in levels[2]:
            if level.split("-")[0] == str(level_number):
                
                level_name = level.split("-")[1].removesuffix(".lvl")
                save = open("levels\\"+ level, "rb")
                load_level(save)
                break
    
    
    if len(player) == 1:
        player = player[0]
    
    global cont
    cont = True
    
    held_keys = {}
    frame = 0
    previous_time = time.time()
    current_time = time.time()
    global d_time
    d_time = 0.018
    direction = [0, 0]
    
    selected_offset = [0, 0]
    selected_object = None
    
    font = pg.font.SysFont("Comic Sans", 50)
    temp = font.render(str(level_number) + "-" + level_name, True, (180, 200, 180))
    
    text = {}
    text[temp] = [5, 5]
    
    while True:       
        mouse_position = pg.mouse.get_pos()
        direction = [0, 0]
        frame += 1
        screen.get_surface().fill((25, 25, 75))
        
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
        start_y = 20
        i = 0
        for image in allowed_images:
                
            center = image.get_height()/2
            screen.get_surface().blit(image, [start_x + (100 * i), 50 - center])
            font = pg.font.SysFont("Comic Sans", 20)
            number = allowed_objects[allowed_images[image]]
            number = font.render(str(number), True, (180, 200, 180))
            screen.get_surface().blit(number, [start_x + (100 * i) + (80 - number.get_width()), (50 - center) + image.get_height()])
            i += 1
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                for thing in platforms + powerups + [player]:
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
                        
                        if image_rect.collidepoint(mouse_position):
                            if allowed_images[image].id == selected_object.id:
                                allowed_objects[allowed_images[image]] += 1
                                
                                if isinstance(selected_object, Player):
                                    player.remove(selected_object)
                                elif isinstance(selected_object, Platform):
                                    platforms.remove(selected_object)
                                elif isinstance(selected_object, PowerUp):
                                    powerups.remove(selected_object)
                
                        i += 1
                if selected_object != None:
                    selected_object.tags = selected_object.tags.replace("-no_collide-", "")
                selected_object = None
                        
        if player.dead == False and player != [] and not player == selected_object:
            try:
                if pg.key.get_pressed()[key_bindings["left"]]:
                    direction[0] -=1
                    try:
                        if held_keys[key_bindings["left"]] == frame - 1:
                            player.speed[0] *= 1.0001
                        else:
                            player.speed[0] = -3*d_time*60
                            
                    except KeyError:
                        player.speed[0] = -3*d_time*60
                    
                    held_keys[key_bindings["left"]] = frame
            except:
                if pg.mouse.get_pressed()[int(key_bindings["left"][-1])]:
                    direction[0] -=1
                    try:
                        if held_keys[key_bindings["left"]] == frame - 1:
                            player.speed[0] *= 1.0001
                        else:
                            player.speed[0] = -3*d_time*60
                            
                    except KeyError:
                        player.speed[0] = -3*d_time*60
                    
                    held_keys[key_bindings["left"]] = frame
                                        
            
            try:    
                if pg.key.get_pressed()[key_bindings["right"]]:
                    direction[0] += 1
                    try:
                        if held_keys[key_bindings["right"]] == frame - 1:
                            player.speed[0] *= 1.0001
                        else:
                            player.speed[0] = 3*d_time*60
                            
                    except KeyError:
                        player.speed[0] = 3*d_time*60
                    
                    held_keys[key_bindings["right"]] = frame
            except:
                if pg.mouse.get_pressed()[int(key_bindings["right"][-1])]:
                    direction[0] += 1
                    try:
                        if held_keys[key_bindings["right"]] == frame - 1:
                            player.speed[0] *= 1.0001
                        else:
                            player.speed[0] = 3*d_time*60
                            
                    except KeyError:
                        player.speed[0] = 3*d_time*60
                    
                    held_keys[key_bindings["right"]] = frame
            if direction[0] == 0:
                player.speed[0] = 0
            
            try:
                
                if pg.key.get_pressed()[key_bindings["jump"]]:
                    direction[1] -= 1
                    if player.jump_enabled and player.jump_allowed:
                        player.speed[1] -= 4*d_time*60
                        player.jump_allowed = False
                        player.on_ground = False
                        player.cayote_timer = 0
            except:
                if pg.mouse.get_pressed()[int(key_bindings["jump"][-1])]:
                    direction[1] -= 1
                    if player.jump_enabled and player.jump_allowed:
                        player.speed[1] -= 4*d_time*60
                        player.jump_allowed = False
                        player.on_ground = False
                        player.cayote_timer = 0
            try:
                
                if pg.key.get_pressed()[key_bindings["crouch"]]:
                    direction[1] += 1
                    player.crouched = True
                else:
                    player.crouched = False
            
            except:
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
                        
                        player.dash_speed[0] += 10*direction[0]*d_time*60
                        player.dash_speed[1] += 10*direction[1]*d_time*60
            except:
                if pg.mouse.get_pressed()[int(key_bindings["dash"][-1])]:
                    if player.dashes > 0 and vector_magnitude(direction) > 0 and player.dash_timer == -1:
                        player.dashes -= 1
                        player.dash_timer = 0
                        player.speed[1] = 0
                        
                        direction = normalise(direction)
                        
                        player.dash_speed[0] += 10*direction[0]*d_time*60
                        player.dash_speed[1] += 10*direction[1]*d_time*60
            
        try:
            if pg.key.get_pressed()[key_bindings["reset"]]:
                for levels in os.walk("levels"):
                    for level in levels[2]:
                        if level.split("-")[0] == str(level_number):
                            
                            level_name = level.split("-")[1] 
                            save = open("levels\\"+ level, "rb")
                            load_level(save)
                            text[temp] = [5, 5]
                            break
                
                if len(player) == 1:
                    player = player[0]
                    
        except:
            if pg.mouse.get_pressed()[int(key_bindings["reset"][-1])]:
                for levels in os.walk("levels"):
                    for level in levels[2]:
                        if level.split("-")[0] == str(level_number):
                            
                            level_name = level.split("-")[1] 
                            save = open("levels\\"+ level, "rb")
                            load_level(save)
                            text[temp] = [5, 5]
                            break
                
                if len(player) == 1:
                    player = player[0]
                            
        if selected_object != None:
            selected_object.location = [mouse_position[0], mouse_position[1]]
            selected_object.location[0] -= selected_offset[0]
            selected_object.location[1] -= selected_offset[1]
            selected_object.centre = [selected_object.location[0] + selected_object.width/2, selected_object.location[1] + selected_object.height/2]
            if isinstance(selected_object, Platform) and selected_object.type == 1:
                selected_object.start = [selected_object.location[0], selected_object.location[1]]
                    
        for platform in platforms:
            platform.draw()
            platform.update()
        
        for power in powerups:
            power.draw()
            
        
        player.update(platforms+powerups, d_time)
        player.draw()
        
        to_remove = []
        for name in text:
            if text[name][0] > 0:
                
                if text[name][0] > 0.4*text[name][1]:
                    name.set_alpha((1-(text[name][0]/text[name][1]))*425)
                else:
                    name.set_alpha(((text[name][0]/text[name][1]))*628)
                
                screen.get_surface().blit(name, [(0.5*screen_width) - (name.get_width()/2), (0.5*screen_height) - (name.get_height()/2)])
                text[name][0] -= d_time
            
            else:
                to_remove.append(name)
                
        for i in to_remove:
            text.pop(i)
        
            
        screen.flip()
        clock.tick(framerate)
        
        current_time = time.time()
        d_time = current_time - previous_time
        previous_time = current_time
        

menu(True)
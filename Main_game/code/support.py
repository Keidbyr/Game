from os import walk
import pygame


def sortkey(s):
    d = []
    for i in range(1, 30):
        for j in s:
            if j[-6:-5] not in '1234567890':
                if int(j[-5:-4]) == i:
                    d.append(j)
            else:
                if int(j[-6:-4]) == i:
                    d.append(j)
    return d


def import_folder(path):
    list_forpy = []
    surface_list = []
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            list_forpy.append(full_path)
        list_forpy = sortkey(list_forpy)
    for k in list_forpy:
        image_surf = pygame.image.load(k).convert_alpha()
        surface_list.append(image_surf)
    return surface_list

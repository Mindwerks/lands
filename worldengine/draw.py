from PIL import Image
import numpy
import numpy.ma as ma
import random

from worldengine.drawing_functions import draw_ancientmap, \
    draw_rivers_on_image, gradient

# -------------
# Helper values
# -------------

_biome_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (128, 128, 128),
    'subpolar moist tundra': (96, 128, 128),
    'subpolar wet tundra': (64, 128, 128),
    'subpolar rain tundra': (32, 128, 192),
    'polar desert': (192, 192, 192),
    'boreal desert': (160, 160, 128),
    'cool temperate desert': (192, 192, 128),
    'warm temperate desert': (224, 224, 128),
    'subtropical desert': (240, 240, 128),
    'tropical desert': (255, 255, 128),
    'boreal rain forest': (32, 160, 192),
    'cool temperate rain forest': (32, 192, 192),
    'warm temperate rain forest': (32, 224, 192),
    'subtropical rain forest': (32, 240, 176),
    'tropical rain forest': (32, 255, 160),
    'boreal wet forest': (64, 160, 144),
    'cool temperate wet forest': (64, 192, 144),
    'warm temperate wet forest': (64, 224, 144),
    'subtropical wet forest': (64, 240, 144),
    'tropical wet forest': (64, 255, 144),
    'boreal moist forest': (96, 160, 128),
    'cool temperate moist forest': (96, 192, 128),
    'warm temperate moist forest': (96, 224, 128),
    'subtropical moist forest': (96, 240, 128),
    'tropical moist forest': (96, 255, 128),
    'warm temperate dry forest': (128, 224, 128),
    'subtropical dry forest': (128, 240, 128),
    'tropical dry forest': (128, 255, 128),
    'boreal dry scrub': (128, 160, 128),
    'cool temperate desert scrub': (160, 192, 128),
    'warm temperate desert scrub': (192, 224, 128),
    'subtropical desert scrub': (208, 240, 128),
    'tropical desert scrub': (224, 255, 128),
    'cool temperate steppe': (128, 192, 128),
    'warm temperate thorn scrub': (160, 224, 128),
    'subtropical thorn woodland': (176, 240, 128),
    'tropical thorn woodland': (192, 255, 128),
    'tropical very dry forest': (160, 255, 128),
}


_biome_satellite_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (186, 199, 206),
    'subpolar moist tundra': (186, 195, 202),
    'subpolar wet tundra': (186, 195, 204),
    'subpolar rain tundra': (186, 200, 210),
    'polar desert': (182, 195, 201),
    'boreal desert': (132, 146, 143),
    'cool temperate desert': (183, 163, 126),
    'warm temperate desert': (166, 142, 104),
    'subtropical desert': (205, 181, 137),
    'tropical desert': (203, 187, 153),
    'boreal rain forest': (21, 29, 8),
    'cool temperate rain forest': (25, 34, 15),
    'warm temperate rain forest': (19, 28, 7),
    'subtropical rain forest': (48, 60, 24),
    'tropical rain forest': (21, 38, 6),
    'boreal wet forest': (6, 17, 11),
    'cool temperate wet forest': (6, 17, 11),
    'warm temperate wet forest': (44, 48, 19),
    'subtropical wet forest': (23, 36, 10),
    'tropical wet forest': (23, 36, 10),
    'boreal moist forest': (31, 39, 18),
    'cool temperate moist forest': (31, 39, 18),
    'warm temperate moist forest': (36, 42, 19),
    'subtropical moist forest': (23, 31, 10),
    'tropical moist forest': (24, 36, 11),
    'warm temperate dry forest': (52, 51, 30),
    'subtropical dry forest': (53, 56, 30),
    'tropical dry forest': (54, 60, 30),
    'boreal dry scrub': (73, 70, 61),
    'cool temperate desert scrub': (80, 58, 44),
    'warm temperate desert scrub': (92, 81, 49),
    'subtropical desert scrub': (68, 57, 35),
    'tropical desert scrub': (107, 87, 60),
    'cool temperate steppe': (95, 82, 50),
    'warm temperate thorn scrub': (77, 81, 48),
    'subtropical thorn woodland': (27, 40, 12),
    'tropical thorn woodland': (40, 62, 15),
    'tropical very dry forest': (87, 81, 49),
}


# ----------------
# Helper functions
# ----------------


def _elevation_color(elevation, sea_level=1.0):
    """
    Calculate color based on elevation
    :param elevation:
    :return:
    """
    color_step = 1.5
    if sea_level is None:
        sea_level = -1
    if elevation < sea_level/2:
        elevation /= sea_level
        return 0.0, 0.0, 0.75 + 0.5 * elevation
    elif elevation < sea_level:
        elevation /= sea_level
        return 0.0, 2 * (elevation - 0.5), 1.0
    else:
        elevation -= sea_level
        if elevation < 1.0 * color_step:
            return (0.0, 0.5 +
                    0.5 * elevation / color_step, 0.0)
        elif elevation < 1.5 * color_step:
            return 2 * (elevation - 1.0 * color_step) / color_step, 1.0, 0.0
        elif elevation < 2.0 * color_step:
            return 1.0, 1.0 - (elevation - 1.5 * color_step) / color_step, 0
        elif elevation < 3.0 * color_step:
            return (1.0 - 0.5 * (elevation - 2.0 *
                                 color_step) / color_step,
                    0.5 - 0.25 * (elevation - 2.0 *
                                  color_step) / color_step, 0)
        elif elevation < 5.0 * color_step:
            return (0.5 - 0.125 * (elevation - 3.0 *
                                   color_step) / (2 * color_step),
                    0.25 + 0.125 * (elevation - 3.0 *
                                    color_step) / (2 * color_step),
                    0.375 * (elevation - 3.0 *
                             color_step) / (2 * color_step))
        elif elevation < 8.0 * color_step:
            return (0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step))
        else:
            elevation -= 8.0 * color_step
            while elevation > 2.0 * color_step:
                elevation -= 2.0 * color_step
            return 1, 1 - elevation / 4.0, 1


def _sature_color(color):
    r, g, b = color
    if r < 0:
        r = 0.0
    if r > 1.0:
        r = 1.0
    if g < 0:
        g = 0.0
    if g > 1.0:
        g = 1.0
    if b < 0:
        b = 0.0
    if b > 1.0:
        b = 1.0
    return r, g, b


def elevation_color(elevation, sea_level=1.0):
    return _sature_color(_elevation_color(elevation, sea_level))


# ----------------------
# Draw on generic target
# ----------------------


class ImagePixelSetter(object):

    def __init__(self, width, height, filename):
        self.img = Image.new('RGBA', (width, height))
        self.pixels = self.img.load()
        self.filename = filename

    def set_pixel(self, x, y, color):
        if len(color) == 3:  # Convert RGB to RGBA - TODO: go through code to fix this
            color = (color[0], color[1], color[2], 255)
        self.pixels[x, y] = color

    def get_pixel(self, x, y):
        return self.pixels[x, y]

    def complete(self):
        try:
            self.img.save(self.filename)
        except KeyError:
            print("Cannot save to file `{}`, unsupported file format.".format(self.filename))
            filename = self.filename+".png"
            print("Defaulting to PNG: `{}`".format(filename))
            self.img.save(filename)

    def __getitem__(self, item):
        return self.pixels[item]

    def __setitem__(self, item, value):
        if len(value) == 3:  # Convert RGB to RGBA - TODO: go through code to fix this
            value = (value[0], value[1], value[2], 255)
        self.pixels[item] = value


def draw_simple_elevation(world, sea_level, target):
    """ This function can be used on a generic canvas (either an image to save
        on disk or a canvas part of a GUI)
    """
    min_elev_sea = None
    max_elev_sea = None
    min_elev_land = None
    max_elev_land = None
    for y in range(world.height):
        for x in range(world.width):
            e = world.elevation['data'][y,x]
            if sea_level is None:
                if min_elev_land is None or e < min_elev_land:
                    min_elev_land = e
                if max_elev_land is None or e > max_elev_land:
                    max_elev_land = e
            elif world.is_land((x, y)):
                if min_elev_land is None or e < min_elev_land:
                    min_elev_land = e
                if max_elev_land is None or e > max_elev_land:
                    max_elev_land = e
            else:
                if min_elev_sea is None or e < min_elev_sea:
                    min_elev_sea = e
                if max_elev_sea is None or e > max_elev_sea:
                    max_elev_sea = e

    elev_delta_land = (max_elev_land - min_elev_land)/11
    if sea_level != None:
        elev_delta_sea = max_elev_sea - min_elev_sea
    
    for y in range(world.height):
        for x in range(world.width):
            e = world.elevation['data'][y, x]
            if sea_level is None:
                c = ((e - min_elev_land) / elev_delta_land) + 1
            elif world.is_land((x, y)):
                c = ((e - min_elev_land) / elev_delta_land) + 1
            else:
                c = ((e - min_elev_sea) / elev_delta_sea)
            r, g, b = elevation_color(c, sea_level)
            target.set_pixel(x, y, (int(r * 255), int(g * 255),
                                    int(b * 255), 255))


def draw_riversmap(world, target):
    sea_color = (255, 255, 255, 255)
    land_color = (0, 0, 0, 255)

    for y in range(world.height):#TODO: numpy
        for x in range(world.width):
            if world.ocean[y, x]:
                target.set_pixel(x, y, sea_color)
            else:
                target.set_pixel(x, y, land_color)

    draw_rivers_on_image(world, target, factor=1)


def draw_grayscale_heightmap(world, target):
    min_elev_sea = None
    max_elev_sea = None
    min_elev_land = None
    max_elev_land = None
    for y in range(world.height):
        for x in range(world.width):
            e = world.elevation['data'][y, x]
            if world.is_land((x, y)):
                if min_elev_land is None or e < min_elev_land:
                    min_elev_land = e
                if max_elev_land is None or e > max_elev_land:
                    max_elev_land = e
            else:
                if min_elev_sea is None or e < min_elev_sea:
                    min_elev_sea = e
                if max_elev_sea is None or e > max_elev_sea:
                    max_elev_sea = e

    elev_delta_land = max_elev_land - min_elev_land
    elev_delta_sea = max_elev_sea - min_elev_sea

    for y in range(world.height):
        for x in range(world.width):
            e = world.elevation['data'][y, x]
            if world.is_land((x, y)):
                c = int(((e - min_elev_land) * 127) / elev_delta_land)+128
            else:
                c = int(((e - min_elev_sea) * 127) / elev_delta_sea)
            target.set_pixel(x, y, (c, c, c, 255))


def draw_satellite(world, target):
    # Not sure what this first part is doing - copied from draw_greyscale_heightmap 
    # I believe it is normalizing the heightmap values between 1 and 255?
    # This function will use those values later, so this loop is kept in
    min_elev_sea = None
    max_elev_sea = None
    min_elev_land = None
    max_elev_land = None
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y, x]
            if world.is_land((x, y)):
                if min_elev_land is None or e < min_elev_land:
                    min_elev_land = e
                if max_elev_land is None or e > max_elev_land:
                    max_elev_land = e
            else:
                if min_elev_sea is None or e < min_elev_sea:
                    min_elev_sea = e
                if max_elev_sea is None or e > max_elev_sea:
                    max_elev_sea = e

    elev_delta_land = max_elev_land - min_elev_land
    elev_delta_sea = max_elev_sea - min_elev_sea
    ## -----------------------------------------------------------------------###

    noise_range = 10 # a random value between -noise_range and noise_range will be added to the rgb of each pixel

    high_mountain_elev = 215
    mountain_elev      = 175
    high_hill_elev     = 160
    hill_elev          = 145

    high_mountain_noise_modifier = (10, 6,   10)
    mountain_noise_modifier =      (-4, -12, -4)
    high_hill_noise_modifier =     (-3, -10, -3)
    hill_noise_modifier =          (-2, -6, -2)

    mountain_color = (50, 57, 28)

    ## Second loop - this sets each pixel's color based on colors defined in _biome_satellite_colors
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y, x]
            v = world.biome[y, x]
            biome_r, biome_g, biome_b = _biome_satellite_colors[v]

            if world.is_land((x, y)):
                c = int(((e - min_elev_land) * 127) / elev_delta_land)+128
                
                ## Generate some random noise to apply to this pixel
                #  There is noise for each element of the rgb value
                #  This noise will be further modified by the height of this tile
                noise = (random.randint(-noise_range, noise_range), 
                         random.randint(-noise_range, noise_range), 
                         random.randint(-noise_range, noise_range))

                ####### Case 1 - elevation is very high ########
                if c > high_mountain_elev:     
                    # Take the random noise, and color it based on the mountain's modifier.
                    # In this case, it makes the area slightly brighter to simulate snow-topped mountains.
                    noise = noise[0] + high_mountain_noise_modifier[0], \
                            noise[1] + high_mountain_noise_modifier[1], \
                            noise[2] + high_mountain_noise_modifier[2]

                    # Average the biome's color with the mountain_color to tint the terrain
                    biome_r = int((biome_r + mountain_color[0])/2)
                    biome_g = int((biome_g + mountain_color[1])/2)
                    biome_b = int((biome_b + mountain_color[2])/2)
                #################################################

                ####### Case 1 - elevation is high ########
                elif c > mountain_elev:   
                    # Take the random noise, and color it based on the mountain's modifier.
                    # In this case, it makes the area slightly darker, especially draining the green
                    noise = noise[0] + mountain_noise_modifier[0], \
                            noise[1] + mountain_noise_modifier[1], \
                            noise[2] + mountain_noise_modifier[2]

                    # Average the biome's color with the mountain_color to tint the terrain
                    biome_r = int((biome_r + mountain_color[0])/2)
                    biome_g = int((biome_g + mountain_color[1])/2)
                    biome_b = int((biome_b + mountain_color[2])/2)
                #################################################

                ####### Case 3 - elevation is somewhat high ########
                elif c > high_hill_elev:   
                    # Make the random noise somewhat darker, and drain a little bit of green
                    noise = noise[0] - high_hill_noise_modifier[0], \
                            noise[1] - high_hill_noise_modifier[1], \
                            noise[2] - high_hill_noise_modifier[2]

                ####### Case 3 - elevation is a little bit high ########
                elif c > hill_elev:   
                    # Make the random noise just a little bit darker, and drain a little bit of green
                    noise = noise[0] - 2, noise[1] - 6, noise[2] - 2

            ### Ocean 
            else:
                c = int(((e - min_elev_sea) * 127) / elev_delta_sea)
                noise = (0, 0, 0)

            # This adds a base modifier to the biome color based on height
            modifier = int(c / 10)

            # Combine the biome color, the height modifier, and the noise value 
            # to get the rgb value
            r = biome_r + modifier + noise[0]
            g = biome_g + modifier + noise[1]
            b = biome_b + modifier + noise[2]

            # Set pixel to this color. This initial color will be accessed and modified later when 
            # the map is smoothed and shaded.
            target.set_pixel(x, y, (r, g, b, 255))


    # Loop through and average a pixel with its neighbors to smooth transitions between biomes
    for y in xrange(1, world.height-1):
        for x in xrange(1, world.width-1):
            ## Only smooth land tiles
            if world.is_land((x, y)):
                # Lists to hold the separated rgb values of the neighboring pixels
                all_r = []
                all_g = []
                all_b = []

                # Loop through this pixel and all neighboring pixels
                for j in xrange(y-1, y+2):
                    for i in xrange(x-1, x+2):
                        # Don't include ocean in the smoothing, if this tile happens to border an ocean
                        if world.is_land((i, j)):
                            # Grab each rgb value and append to the list
                            r, g, b, a = target.get_pixel(i, j)
                            all_r.append(r)
                            all_g.append(g)
                            all_b.append(b)

                # Making sure there is at least one valid tile to be smoothed before we attempt to average the values
                if all_r:
                    avg_r = int(sum(all_r) / len(all_r))
                    avg_g = int(sum(all_g) / len(all_g))
                    avg_b = int(sum(all_b) / len(all_b))

                    ## Setting color of the pixel again - this will be once more modified by the shading algorithm
                    target.set_pixel(x, y, (avg_r, avg_g, avg_b, 255))

    
    # How many tiles to average together when comparing this tile's elevation to the previous tiles.
    shade_size = 5
    # How much to multiply the difference in elevation between this tile and the previous tile
    # Higher will result in starker contrast between high and low areas.
    difference_multiplier = 9

    # "Shade" the map by sending beams of light west to east, and increasing or decreasing value of pixel based on elevation difference
    for y in xrange(shade_size-1, world.height-shade_size-1):
        for x in xrange(shade_size-1, world.width-shade_size-1):
            if world.is_land((x, y)):
                r, g, b, a = target.get_pixel(x, y)
                
                # Build up list of elevations in the previous n tiles, where n is the shadow size.
                # This goes left to right, so it would be the previous tiles on the same y level  
                prev_elevs = [ world.elevation['data'][y-n, x-n] for n in xrange(1, shade_size+1)]

                # Take the average of the height of the previous n tiles
                avg_prev_elev = int( sum(prev_elevs) / len(prev_elevs) )

                # Find the difference between this tile's elevation, and the average of the previous elevations
                difference = int(world.elevation['data'][y, x] - avg_prev_elev)

                # Amplify the difference
                difference = difference * difference_multiplier

                # The amplified difference is now translated into the rgb of the tile.
                # This adds light to tiles higher that the previous average, and shadow
                # to tiles lower than the previous average
                r += difference
                g += difference
                b += difference

                # Set the final color for this pixel
                target.set_pixel(x, y, (r, g, b, 255))


def draw_elevation(world, shadow, target):
    width = world.width
    height = world.height

    data = world.elevation['data']
    ocean = world.ocean

    mask = numpy.ma.array(data, mask = ocean)

    min_elev = mask.min()
    max_elev = mask.max()
    elev_delta = max_elev - min_elev

    for y in range(height):#TODO: numpy optimisation for the code below
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                e = data[y, x]
                c = 255 - int(((e - min_elev) * 255) / elev_delta)
                if shadow and y > 2 and x > 2:
                    if data[y - 1, x - 1] > e:
                        c -= 15
                    if data[y - 2, x - 2] > e \
                            and data[y - 2, x - 2] > data[y - 1, x - 1]:
                        c -= 10
                    if data[y - 3, x - 3] > e \
                            and data[y - 3, x - 3] > data[y - 1, x - 1] \
                            and data[y - 3, x - 3] > data[y - 2, x - 2]:
                        c -= 5
                    if c < 0:
                        c = 0
                target.set_pixel(x, y, (c, c, c, 255))


def draw_ocean(ocean, target):
    height, width = ocean.shape

    for y in range(height):
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                target.set_pixel(x, y, (0, 255, 255, 255))


def draw_precipitation(world, target, black_and_white=False):
    # FIXME we are drawing humidity, not precipitations
    width = world.width
    height = world.height

    if black_and_white:
        low = None
        high = None
        for y in range(height):
            for x in range(width):
                p = world.precipitations_at((x, y))
                if low is None or p < low:
                    low = p
                if high is None or p > high:
                    high = p
        for y in range(height):
            for x in range(width):
                p = world.precipitations_at((x, y))
                if p <= low:
                    target.set_pixel(x, y, (0, 0, 0, 255))
                elif p >= high:
                    target.set_pixel(x, y, (255, 255, 255, 255))
                else:
                    target.set_pixel(x, y, gradient(p, low, high, (0, 0, 0), (255, 255, 255)))
    else:
        for y in range(height):
            for x in range(width):
                if world.is_humidity_superarid((x, y)):
                    target.set_pixel(x, y, (0, 32, 32, 255))
                elif world.is_humidity_perarid((x, y)):
                    target.set_pixel(x, y, (0, 64, 64, 255))
                elif world.is_humidity_arid((x, y)):
                    target.set_pixel(x, y, (0, 96, 96, 255))
                elif world.is_humidity_semiarid((x, y)):
                    target.set_pixel(x, y, (0, 128, 128, 255))
                elif world.is_humidity_subhumid((x, y)):
                    target.set_pixel(x, y, (0, 160, 160, 255))
                elif world.is_humidity_humid((x, y)):
                    target.set_pixel(x, y, (0, 192, 192, 255))
                elif world.is_humidity_perhumid((x, y)):
                    target.set_pixel(x, y, (0, 224, 224, 255))
                elif world.is_humidity_superhumid((x, y)):
                    target.set_pixel(x, y, (0, 255, 255, 255))


def draw_world(world, target):
    width = world.width
    height = world.height

    for y in range(height):
        for x in range(width):
            if world.is_land((x, y)):
                biome = world.biome_at((x, y))
                target.set_pixel(x, y, _biome_colors[biome.name()])
            else:
                c = int(world.sea_depth[y, x] * 200 + 50)
                target.set_pixel(x, y, (0, 0, 255 - c, 255))


def draw_temperature_levels(world, target, black_and_white=False):
    width = world.width
    height = world.height

    if black_and_white:
        low = world.temperature_thresholds()[0][1]
        high = world.temperature_thresholds()[5][1]
        for y in range(height):
            for x in range(width):
                t = world.temperature_at((x, y))
                if t <= low:
                    target.set_pixel(x, y, (0, 0, 0, 255))
                elif t >= high:
                    target.set_pixel(x, y, (255, 255, 255, 255))
                else:
                    target.set_pixel(x, y, gradient(t, low, high, (0, 0, 0), (255, 255, 255)))

    else:
        for y in range(height):
            for x in range(width):
                if world.is_temperature_polar((x, y)):
                    target.set_pixel(x, y, (0, 0, 255, 255))
                elif world.is_temperature_alpine((x, y)):
                    target.set_pixel(x, y, (42, 0, 213, 255))
                elif world.is_temperature_boreal((x, y)):
                    target.set_pixel(x, y, (85, 0, 170, 255))
                elif world.is_temperature_cool((x, y)):
                    target.set_pixel(x, y, (128, 0, 128, 255))
                elif world.is_temperature_warm((x, y)):
                    target.set_pixel(x, y, (170, 0, 85, 255))
                elif world.is_temperature_subtropical((x, y)):
                    target.set_pixel(x, y, (213, 0, 42, 255))
                elif world.is_temperature_tropical((x, y)):
                    target.set_pixel(x, y, (255, 0, 0, 255))


def draw_biome(world, target):
    width = world.width
    height = world.height

    biome = world.biome

    for y in range(height):
        for x in range(width):
            v = biome[y, x]
            target.set_pixel(x, y, _biome_colors[v])

def draw_scatter_plot(world, size, target):
    """ This function can be used on a generic canvas (either an image to save
        on disk or a canvas part of a GUI)
    """

    #Find min and max values of humidity and temperature on land so we can
    #normalize temperature and humidity to the chart
    humid = ma.masked_array(world.humidity['data'], mask=world.ocean)
    temp = ma.masked_array(world.temperature['data'], mask=world.ocean)
    min_humidity = humid.min()
    max_humidity = humid.max()
    min_temperature = temp.min()
    max_temperature = temp.max()
    temperature_delta = max_temperature - min_temperature
    humidity_delta = max_humidity - min_humidity
    
    #set all pixels white
    for y in range(0, size):
        for x in range(0, size):
            target.set_pixel(x, y, (255, 255, 255, 255))

    #fill in 'bad' boxes with grey
    h_values = ['62', '50', '37', '25', '12']
    t_values = [   0,    1,    2,   3,    5 ]
    for loop in range(0,5):
        h_min = (size - 1) * ((world.humidity['quantiles'][h_values[loop]] - min_humidity) / humidity_delta)
        if loop != 4:
            h_max = (size - 1) * ((world.humidity['quantiles'][h_values[loop + 1]] - min_humidity) / humidity_delta)
        else:
            h_max = size
        v_max = (size - 1) * ((world.temperature['thresholds'][t_values[loop]][1] - min_temperature) / temperature_delta)
        if h_min < 0:
            h_min = 0
        if h_max > size:
            h_max = size
        if v_max < 0:
            v_max = 0
        if v_max > (size - 1):
            v_max = size - 1
            
        if h_max > 0 and h_min < size and v_max > 0:
            for y in range(int(h_min), int(h_max)):
                for x in range(0, int(v_max)):
                    target.set_pixel(x, (size - 1) - y, (128, 128, 128, 255))
                    
    #draw lines based on thresholds
    for t in range(0, 6):
        v = (size - 1) * ((world.temperature['thresholds'][t][1] - min_temperature) / temperature_delta)
        if v > 0 and v < size:
            for y in range(0, size):
                target.set_pixel(int(v), (size - 1) - y, (0, 0, 0, 255))
    ranges = ['87', '75', '62', '50', '37', '25', '12']
    for p in ranges:
        h = (size - 1) * ((world.humidity['quantiles'][p] - min_humidity) / humidity_delta)
        if h > 0 and h < size:
            for x in range(0, size):
                target.set_pixel(x, (size - 1) - int(h), (0, 0, 0, 255))

    #examine all cells in the map and if it is land get the temperature and
    #humidity for the cell.
    for y in range(world.height):
        for x in range(world.width):
            if world.is_land((x, y)):
                t = world.temperature_at((x, y))
                p = world.humidity['data'][y, x]

    #get red and blue values depending on temperature and humidity                
                if world.is_temperature_polar((x, y)):
                    r = 0
                elif world.is_temperature_alpine((x, y)):
                    r = 42
                elif world.is_temperature_boreal((x, y)):
                    r = 85
                elif world.is_temperature_cool((x, y)):
                    r = 128
                elif world.is_temperature_warm((x, y)):
                    r = 170
                elif world.is_temperature_subtropical((x, y)):
                    r = 213
                elif world.is_temperature_tropical((x, y)):
                    r = 255
                if world.is_humidity_superarid((x, y)):
                    b = 32
                elif world.is_humidity_perarid((x, y)):
                    b = 64
                elif world.is_humidity_arid((x, y)):
                    b = 96
                elif world.is_humidity_semiarid((x, y)):
                    b = 128
                elif world.is_humidity_subhumid((x, y)):
                    b = 160
                elif world.is_humidity_humid((x, y)):
                    b = 192
                elif world.is_humidity_perhumid((x, y)):
                    b = 224
                elif world.is_humidity_superhumid((x, y)):
                    b = 255

    #calculate x and y position based on normalized temperature and humidity
                nx = (size - 1) * ((t - min_temperature) / temperature_delta)
                ny = (size - 1) * ((p - min_humidity) / humidity_delta)
                    
                target.set_pixel(int(nx), (size - 1) - int(ny), (r, 128, b, 255))
    

# -------------
# Draw on files
# -------------


def draw_simple_elevation_on_file(world, filename, sea_level):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_simple_elevation(world, sea_level, img)
    img.complete()


def draw_riversmap_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_riversmap(world, img)
    img.complete()


def draw_grayscale_heightmap_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_grayscale_heightmap(world, img)
    img.complete()


def draw_elevation_on_file(world, filename, shadow=True):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_elevation(world, shadow, img)
    img.complete()


def draw_ocean_on_file(ocean, filename):
    height, width = ocean.shape
    img = ImagePixelSetter(width, height, filename)
    draw_ocean(ocean, img)
    img.complete()


def draw_precipitation_on_file(world, filename, black_and_white=False):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_precipitation(world, img, black_and_white)
    img.complete()


def draw_world_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_world(world, img)
    img.complete()


def draw_temperature_levels_on_file(world, filename, black_and_white=False):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_temperature_levels(world, img, black_and_white)
    img.complete()


def draw_biome_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_biome(world, img)
    img.complete()


def draw_ancientmap_on_file(world, filename, resize_factor=1,
                            sea_color=(212, 198, 169, 255),
                            draw_biome=True, draw_rivers=True, draw_mountains=True, 
                            draw_outer_land_border=False, verbose=False):
    img = ImagePixelSetter(world.width * resize_factor,
                           world.height * resize_factor, filename)
    draw_ancientmap(world, img, resize_factor, sea_color,
                    draw_biome, draw_rivers, draw_mountains, draw_outer_land_border, 
                    verbose)
    img.complete()

def draw_scatter_plot_on_file(world, filename):
    img = ImagePixelSetter(512, 512, filename)
    draw_scatter_plot(world, 512, img)
    img.complete()


def draw_satellite_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_satellite(world, img)
    img.complete()
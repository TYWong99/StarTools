'''
Logic module that can
 - TBA

USAGE EXAMPLE:
	main_logic.logic(playdo)
	raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
	pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
	conflict.FixConflicts(playdo, pruned_dict)
'''

import os
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Output
_output_folder1 = "output/"
_output_folder2 = _output_folder1 + "levels/"
_output_file    = _output_folder1 + "_merged.txt"


input_layer_name  = "_scroll"
output_layer_name = "_fg_parallax"  # If you add a / in the name, the app just crashes
auto_layer_names = [
	"raw_ BIOME _parallax",  # Input layer name of auto-tiling
	"_fg_parallax BIOME",    # Output layer name of auto-tiling
]

property_name = "scroll2"



#--------------------------------------------------#
'''Public Functions'''

def logic(playdo, scroll_x, scroll_y, make_auto_layers):
	'''TODO'''
	log.Must('')
	log.Must(f'Creating modified layer with scroll factors, x = {scroll_x}, y = {scroll_y}...')

	# Set tile ID based on how much it's scrolling / stretching
	ref_tiles2d = playdo.GetTiles2d(input_layer_name)
	level_w = playdo.map_width
	level_h = playdo.map_height
	CheckMapSize(playdo, scroll_x, scroll_y)

	# Set tile IDs
	mult_x = 1 / float(scroll_x)
	mult_y = 1 / float(scroll_y)
	new_tiles2d = playdo.GetBlankTiles2d()
	for x in range(level_w):
		ref_x = int(x * mult_x)
		if ref_x > level_w: break
		for y in range(level_h):
			ref_y = int(y * mult_y)
			if ref_y > level_h: break
			new_tiles2d[y][x] = ref_tiles2d[ref_y][ref_x]
	playdo.SetTiles2d(output_layer_name, new_tiles2d)

	# Create a blank layer, then set the scrolling properties
	AddParallaxToLayer(playdo, output_layer_name, scroll_x, scroll_y, True)
	if make_auto_layers:
		for auto_name in auto_layer_names: AddParallaxToLayer(playdo, auto_name, scroll_x, scroll_y, False)



def CheckMapSize(playdo, scroll_x, scroll_y):
	ref_tiles2d = playdo.GetTiles2d(input_layer_name)
	level_w = playdo.map_width
	level_h = playdo.map_height
	log.Info(f"  Map Size W x H    : {level_w} x {level_h}")

	layer_w = -1
	layer_h = -1
	for i in range(level_w):
		if ref_tiles2d[0][i] != 0: continue
		layer_w = i
		break
	for i in range(level_h):
		if ref_tiles2d[i][0] != 0: continue
		layer_h = i
		break
	log.Info(f"    Tilelayer Size  : {layer_w} x {layer_h}")

	# Estimate new width & height
	mult_x = 1 / float(scroll_x)
	mult_y = 1 / float(scroll_y)
	new_w = int(layer_w / mult_x)
	new_h = int(layer_h / mult_y)
	is_level_big_enough = (new_w <= level_w) and (new_h <= level_h)
	log.Info(f"    Map Requirement : {new_w} x {new_h}")
	log.Info(f"      Is level big enough? {is_level_big_enough}")







def AddParallaxToLayer(playdo, layer_name, scroll_x, scroll_y, set_properties = False):
	'''This only adds the attributes to the layer, without affecting the Tiles2d itself'''
	new_layer = playdo.GetTilelayer(layer_name, False)
	new_layer.set("parallaxx", scroll_x)
	new_layer.set("parallaxy", scroll_y)
	new_layer.set("offsetx", "-8") # Always shift layer by a certain amount?
	new_layer.set("offsety", "-8")
	if set_properties: tiled_utils.SetPropertyOnObject(new_layer, "scroll2", "")
	return new_layer
#   <layer id="1334" name="raw_spleen_parallax" width="69" height="41" visible="0" parallaxx="1.05" parallaxy="1.05">







#--------------------------------------------------#
'''General Utility, to be relocated?'''

def _Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )

def _FormatNumS2TU(num_in_str):
	'''Shortcut, for converting string (coordinates measured in pixels) intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( round(float(num_in_str))/16 ))





#--------------------------------------------------#










# End of File
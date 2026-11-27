'''
Command-Line Tool for reading a simplified map XML, then creates a XLSX file at desktop
The new XLSX contains the coloring data from the XML, and can then be imported into Google Sheet
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_map_xl.py
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.tiled_utils as tiled_utils

from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
import subprocess
import time
import os
from datetime import datetime
from PIL import Image
import copy

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# Input filename of the map XML, housed in the usual "levels" folder
# NOTE Only the bottommost will be used, the rest ignored
level_name_input = "map_simplified.xml"
level_name_input = "map_planning.xml"
level_name_input = "map_export_xlsx.xml"
level_name_input = "map_simplified2.xml"

# Output filepath of the exported XLSX
path_t           =  "/Users/Jimmy/Desktop/whale_map.xlsx"      # TY's path
path_q           = r"C:\Users\qtran\Desktop\whale_map.xlsx"    # Quang's path
filepath_output  = path_q

# Export Mode of this tool
mode_export = 1                   # 1: Export color & grid in XLSX, 2: Export room names in TXT
config_grid_preprocess = False    # Use the pre-processed method, requires auto-tiling the raw grid layer
config_grid_hardcode   = True     # Use the faster hardcoded method, requires a generated dictionary
config_grid_export     = False    # Print the hardcode values through the automated image-reading


# XML Configurations
layer_name_color      = "FILL"
layer_name_icon       = "ICON"
layer_name_biome      = "_room_letter"
layer_name_number     = "_room_num_all"
layer_name_border_raw = "LINE"
layer_name_border1    = "_map_grid_LR"
layer_name_border2    = "_map_grid_DU"

# Spreadsheet Format
column_width = 30    # (in pixels) Width of each column in the spreadsheet

grid_thickness = 'thick'   # 'thin' 'thick'
grid_color_1   = 'FFFFFF' # Wall
grid_color_2   = '888888' # Door
dict_grid_to_id = {
	"wall_l": 400+1,
	"door_l": 528+1,
	"wall_u": 273+1,
	"door_u": 274+1,
}
dict_id_to_wall = {}    # Either: Scanned during runtime, or Hardcoded into this file

room_color_save = '00FFFF' # Save rooms - Cyan
room_color_warp = '32CD32' # Warp rooms - Lime Green
dict_room_to_id = {
	"warp": [145+1,],
	"save": [144+1,146+1,148+1,149+1,],
}

bg_hex     = "0076a3"    # dict_id_to_hex[411+1]
unused_hex = "000000"
dict_id_to_hex = {
	 16+1:"6858d0",
	 17+1:"b961e9",
	 18+1:"f8ca34",
	 19+1:"34d9c1",
	 20+1:"80c84f",
	 21+1:"5299f6",
	 22+1:"ef71cd",
	 23+1:"c78855",
	 24+1:"eb2a67",
	 25+1:"ff0000",

	154+1:"444444",
	155+1:"868686",
	156+1:"c4c4c4",
	157+1:"ffffff",
	158+1:"fefeff",
	159+1:"fdffff",

	283+1:"1b1464",
	284+1:"440e62",
	410+1:"00746b",
	411+1:"0076a3",
	412+1:"004a80",
	538+1:"8c6239",
	539+1:"362f2d",
	540+1:"7b0046",
}

dict_id_to_num    = {}
dict_id_to_letter = {}




#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a simplified map XML and export a XLSX with colors'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Check if address exists, exit and do nothing if so
	output_folder = filepath_output
	if '/'  in output_folder: output_folder = output_folder.replace(filepath_output.split('/')[-1], "")
	if '\\' in output_folder: output_folder = output_folder.replace(filepath_output.split('\\')[-1], "")
#	log.Must(f"  Output: {output_folder}\n")
	if not Path(output_folder).exists():
		log.Must(f"  Output: {output_folder}\n")
		log.Must( "  Output path does not exist!")
		log.Must( "   Make sure you are setting the correct path inside the .py file")
		log.Must("")
		return

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(level_name_input))
	if   mode_export == 1: ExportMapColorInXlsx(playdo, filepath_output)
	elif mode_export == 2: ExportRoomNamesInTxt(playdo)
	else: log.Must("[EROOR] - Export Mode invalid, please go to the .py file to change")





#----------------------------------------------------------#
#-------------------- [XLSX Functions] --------------------#

def ExportMapColorInXlsx(playdo, filepath_output):
	'''
	 Reads the XML and output a XLSX spreadsheet in the designated filepath
	'''
	log.Must(f'  Exporting XLSX from map data - {playdo.map_width} x {playdo.map_height}')
	wb = openpyxl.Workbook()
	ws = wb.active

	# Create the new XLSX file with all the colors
	AddColorToXlsx(ws, playdo)
	AddGridlinesToXlsx(ws, playdo)        # Add white grid lines for each room
	if not True: log.Must(""); return
	AddFreezeLabel(ws, playdo.map_height) # Add a column & row to the left & top side respectively
	ResizeColumns(ws)                     # Resize all columns to smaller width

	# Save spreadsheet to filepath
	log.Must('')
	log.Must(f"  Exporting at : f{filepath_output}")
	log.Must(f"   Rows: {ws.max_row}, Columns: {ws.max_column}")
	wb.save(filepath_output)

	log.Must('')





#-------------------------------------------------------#
#-------------------- [XLSX - Grid] --------------------#

def AddGridlinesToXlsx(ws, playdo):
	'''
	 TODO
	'''
	log.Must('  Adding gridlines to XLSX...')

	# For the pre-process method, tool reads the 2 auto-tiled output layers instead
	if config_grid_preprocess: AddGridFromPreprocessed(ws, playdo); return

	# Set up the dictionary
	if config_grid_hardcode: _SetDictWallHardcoded()
	else:                    _SetDictWallImage()

	# Syntax
	wall_gridline = Side(style=grid_thickness, color=grid_color_1)
	door_gridline = Side(style=grid_thickness, color=grid_color_2)

	# Read map data into string
	num_row = playdo.map_height
	num_col = playdo.map_width
	tiles2d = playdo.GetTiles2d(layer_name_border_raw)
	if tiles2d == None: log.Must('   Grid layers not found, skipping operation...'); return
	log.Must('   Reading grid layers...')
	for i in range(num_row):
		if i <= 0 or i >= num_row-1: continue
		for j in range(num_col):
			# Skip outermost cells to avoid out-of-bound checking
			if j <= 0 or j >= num_col-1: continue

			# Get the tile ID needed; NOTE If any of the ID is not in the dictionary, cell is skipped
			id_c = tiles2d[i  ][j  ]
			id_l = tiles2d[i  ][j-1]
			id_u = tiles2d[i-1][j  ]
			if id_c not in dict_id_to_wall: continue
			if id_l not in dict_id_to_wall: continue
			if id_u not in dict_id_to_wall: continue

			# TODO
			gridline_l = None
			gridline_u = None
			if dict_id_to_wall[id_c][0] == 2 or dict_id_to_wall[id_l][1] == 2: gridline_l = door_gridline
			if dict_id_to_wall[id_c][3] == 2 or dict_id_to_wall[id_u][2] == 2: gridline_u = door_gridline
			if dict_id_to_wall[id_c][0] == 1 or dict_id_to_wall[id_l][1] == 1: gridline_l = wall_gridline
			if dict_id_to_wall[id_c][3] == 1 or dict_id_to_wall[id_u][2] == 1: gridline_u = wall_gridline
			ws.cell(row = i+1, column = j+1).border = Border(left=gridline_l, top=gridline_u)



def _SetDictWallImage():
	'''
	 TODO
	'''
	global dict_id_to_wall
	log.Must(f"   Setting up dictionary for grid status - Image Method")

	# Tilesheet data; NOTE Might need to update after tile migration
	start_id = 272+1   # Starts at 272 in Tiled app
	tile_w = 10        # There are ≤ 10 x 4 tiles for grids
	tile_h = 4
	offset_l = (  2,  6 ) # Offest for checking the left-side of grid for wall, measured in pixels
	offset_r = ( 13,  6 )
	offset_d = (  8, 11 )
	offset_u = (  8,  4 )

	# Open the image and convert to RGBA to ensure an alpha channel exists
	filepath_tilesheet = "/Users/Jimmy/Desktop/tiles.png"
	with Image.open(filepath_tilesheet) as img:
		rgba_img = img.convert("RGBA")
		for i in range( tile_w * tile_h ):
			curr_id = start_id + i % tile_w + (i // tile_w) * 128
			wall_l = _CheckIsWall( rgba_img, curr_id, offset_l )
			wall_r = _CheckIsWall( rgba_img, curr_id, offset_r )
			wall_d = _CheckIsWall( rgba_img, curr_id, offset_d )
			wall_u = _CheckIsWall( rgba_img, curr_id, offset_u )
			dict_id_to_wall[curr_id] = ( wall_l, wall_r, wall_d, wall_u )
			log.Extra(f'\t{curr_id}\t{dict_id_to_wall[curr_id]}')

	# Set for the other 3 tile-orientations
	temp_dict = copy.deepcopy(dict_id_to_wall)
	for key, value in temp_dict.items():
#		break
		id = key
		l, r, d, u = value
		id_x  = tiled_utils.FlipTileId(id)
		id_y  = tiled_utils.FlipTileId(tiled_utils.RotateTileId(tiled_utils.RotateTileId(id)))
		id_xy = tiled_utils.RotateTileId(tiled_utils.RotateTileId(id))
		dict_id_to_wall[id_x ] = ( r, l, d, u )
		dict_id_to_wall[id_y ] = ( l, r, u, d )
		dict_id_to_wall[id_xy] = ( r, l, u, d )

	# Empty tile
	dict_id_to_wall[0] = ( 0, 0, 0, 0 )

	# Print the result for future use, so to skip the image-rading in the future
	if not config_grid_export: return
	print('')
	print('')
	count = 0
	for key, value in dict_id_to_wall.items():
		print(f'\tdict_id_to_wall[{key}] = {value}')
		count += 1
		if count % 40 == 0: print('')
	print('')
	print('')

def _CheckIsWall( rgba_img, curr_id, offset ):
	'''
	 Returns 0 if empty
	 Returns 1 if is a wall
	 Returns 2 if is a door
	'''
	start_x = curr_id %  128 * 16 - 16    # Starting x-position, measured in pixels
	start_y = curr_id // 128 * 16
	new_x = start_x + offset[0]
	new_y = start_y + offset[1]

	alpha_value = rgba_img.getpixel( (new_x, new_y) )[3]
	if   alpha_value > 200: return 1
	elif alpha_value >  10: return 2
	else:                   return 0



def AddGridFromPreprocessed(ws, playdo):
	'''
	 TODO
	'''
	log.Must('  Adding gridlines to XLSX...')
	num_row = playdo.map_height
	num_col = playdo.map_width

	# Initialise the array
	wall_gridline = Side(style=grid_thickness, color=grid_color_1)
	door_gridline = Side(style=grid_thickness, color=grid_color_2)

	# Read map data into string
	tiles2d_lr = playdo.GetTiles2d(layer_name_border1)
	tiles2d_du = playdo.GetTiles2d(layer_name_border2)
	if tiles2d_lr == None or tiles2d_du == None:
		log.Must('   Grid layers not found, skipping operation...')
		return
	for i in range(num_row):
		for j in range(num_col):
			gridline_l = None
			gridline_u = None
			if tiles2d_lr[i][j] == dict_grid_to_id["wall_l"]: gridline_l = wall_gridline
			if tiles2d_lr[i][j] == dict_grid_to_id["door_l"]: gridline_l = door_gridline
			if tiles2d_du[i][j] == dict_grid_to_id["wall_u"]: gridline_u = wall_gridline
			if tiles2d_du[i][j] == dict_grid_to_id["door_u"]: gridline_u = door_gridline
			ws.cell(row = i+1, column = j+1).border = Border(left=gridline_l, top=gridline_u)





#----------------------------------------------------------#
#-------------------- [XLSX Functions] --------------------#

def AddColorToXlsx(ws, playdo):
	'''
	 This exports the XLSX based on the recorded coloring data
	'''
	log.Must('  Adding color to XLSX...')
	num_row = playdo.map_height
	num_col = playdo.map_width

	# Creates an array for just the color hex values
	list_key = list(dict_id_to_hex.keys())
	dict_id_to_fill = {}
	for key, value in dict_id_to_hex.items(): dict_id_to_fill[key] = PatternFill(start_color = value, end_color = value, fill_type="solid")
	for ID in dict_room_to_id["save"]: dict_id_to_fill[ID] = PatternFill(start_color = room_color_save, end_color = room_color_save, fill_type="solid")
	for ID in dict_room_to_id["warp"]: dict_id_to_fill[ID] = PatternFill(start_color = room_color_warp, end_color = room_color_warp, fill_type="solid")

	# Fill color to the XLSX
	tiles2d = playdo.GetTiles2d(layer_name_color)
	if tiles2d == None: log.Must(f"  [ERROR] - Layer {layer_name_color} not found!"); return
	for i in range(num_row):
		for j in range(num_col):
#			if not tiles2d[i][j] in list_key: continue
			if not tiles2d[i][j] in dict_id_to_fill.keys(): continue
#			hex = dict_id_to_hex[tiles2d[i][j]]
#			fill = PatternFill(start_color = hex, end_color = hex, fill_type="solid")
			fill = dict_id_to_fill[tiles2d[i][j]]
			ws.cell(row = i+1, column = j+1, value = " ").fill = fill

	# Special case - Warp and Save room
	tiles2d_icon = playdo.GetTiles2d(layer_name_icon)
	for i in range(num_row):
		if tiles2d_icon == None: log.Must("   Icon layer not found, omitting check..."); break
		for j in range(num_col):
			if tiles2d[i][j] == 0: continue                          # Quick filter
			if not tiles2d[i][j] in dict_id_to_fill.keys(): continue # Safety check
			fill = dict_id_to_fill[tiles2d[i][j]]
			ws.cell(row = i+1, column = j+1, value = " ").fill = fill

	# Set the default BG Color for the "unedited cells" and "out of bound cells"
	bg_fill    = PatternFill( start_color = bg_hex,     end_color = bg_hex,     fill_type="solid" )
	black_fill = PatternFill( start_color = unused_hex, end_color = unused_hex, fill_type="solid" )
	for row in ws.iter_rows(min_row = 1, max_row = num_row+1):
		for cell in row:
			if cell.fill.fill_type in (None, "none"): cell.fill = bg_fill
	for row in ws.iter_rows(min_row = num_row+2, max_row = 1000):	# NOTE Somehow this line crops sheet to 273 rows
#	for row in ws.iter_rows(min_row = max_y-min_y+1, max_row = max_y-min_y+1):
		for cell in row: cell.fill = black_fill
#	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):
#		for cell in row: cell.fill = black_fill



def AddFreezeLabel(ws, num_rows):
	'''
	  Add Number & Syntax to the top row & left column, then freeze them
	'''
	log.Must('  Adding frozen first row & column to XLSX...')
	ws.insert_cols(idx=1)
	ws.insert_rows(idx=1)

	# Top-row
	num = -1
	for col in ws.columns:
		column_letter = col[0].column_letter
		cell = ws[f"{column_letter}1"]
		cell.value     = num
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")
		num += 1

	# Add number in left-column
	for i in range(num_rows+1):
		cell = ws[f"A{i+1}"]
		cell.value     = num_rows - i
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")

	# Freeze first row and column
	ws[f"A1"] = ""
	ws.freeze_panes = "B2"



def ResizeColumns(ws):
	'''
	 Resize the column width so it's easier to fit into the screen
	'''
	log.Must(f'  Resizing each column to be {column_width} pixels...')
	for col in ws.columns:
		column_letter = col[0].column_letter
		ws.column_dimensions[column_letter].width = column_width / 7    # Function uses "character" as measurement, each ~7px





#---------------------------------------------------------#
#-------------------- [TXT Functions] --------------------#

def ExportRoomNamesInTxt(playdo):
	'''
	 Generate a TXT file that contains the room names at corresponding cell position
	 The entire content can be copy-pasted directly onto the spreadsheet, starting at top-left [B2]
	'''
	num_row = playdo.map_height
	num_col = playdo.map_width
	empty_id = -1

	# Initialise the array
	map_output = [[empty_id for _ in range(num_col)] for _ in range(num_row)]

	# Set up the dictionary : TileID -> Number, TileID -> Biome Letter
	MakeDictIdToNum()
#	for key, value in dict_id_to_num.items(): print(f"{key} : {value}")
#	for key, value in dict_id_to_letter.items(): print(f"{key} : {value}")

	# Read map data into string
	tiles2d_letter = playdo.GetTiles2d(layer_name_biome)
	tiles2d_number = playdo.GetTiles2d(layer_name_number)
	for i in range(num_row):
		for j in range(num_col):
			if     tiles2d_number[i][j] == 0:              continue
			if not tiles2d_number[i][j] in dict_id_to_num: continue
			map_output[i][j]  = dict_id_to_letter[tiles2d_letter[i][j]]
			map_output[i][j] += dict_id_to_num[   tiles2d_number[i][j]]
	log.Must(f"  Map W: {num_col}, Map H: {num_row}")
	log.Must("")

	# Export into TXT file
	_ExportMapToString(map_output, empty_id, "   ", '\t', False)

def _ExportMapToString(map_simple, empty_id, empty_char = " ", separator = " ", print_in_console = True):
	'''
	 Prints the map data on console instead
	 For debugging, and in case want to switch over to the "copy-paste plain text" method
	'''
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	log.Must(f"  Exporting room names in plain text: {num_col}x{num_row}...")
	log.Must(f"")

	# Generate the string here
	print_msg = f"[B2] Copy-Paste to here ; Last Exported at {datetime.now().replace(microsecond=0)}"
	for i in range(num_row):
		for j in range(num_col):
			if map_simple[i][j] == empty_id: print_msg += empty_char
#			else:                            print_msg += "x"
#			else:                            print_msg += map_simple[i][j][0]
#			else:                            print_msg += map_simple[i][j] // 10
			else:                            print_msg += f"{map_simple[i][j]}"
			print_msg += separator
		print_msg += "\n"
	
	# Output to either Console or in a TXT file
	# NOTE Make sure to close the app first before re-running, otherwise the TXT won't update
	if print_in_console: log.Must(print_msg)
	log.Must(f"  Opening the generated TXT automatically...")
	filepath = "map_exported.txt"
#	filepath = input folder + "map_exported.rxt"
	with open(filepath, "w", encoding="utf-8") as file: file.write(print_msg)
	subprocess.run(["open", "-a", "TextEdit", filepath])
	time.sleep(1)
	os.remove(filepath)
	log.Must(f"   Generated TXT deleted")
	log.Must(f"")



def MakeDictIdToNum():

	# Tile ID to Room Number
	global dict_id_to_num
	START_ID = 789+1
	WIDTH = 5
	for i in range(60):
		tile_id = START_ID + i % WIDTH + (i // WIDTH) * 128
		num_string = ""
		if i+1 < 10: num_string = "0"
		num_string += f"{i+1}"
		if i == 59: num_string = "00"
		dict_id_to_num[tile_id] = num_string
	dict_id_to_num[0] = "  "

	# Special Cases
	dict_id_to_num[1936+1] = "-natty"

	# Tile ID to Biome Letter
	global dict_id_to_letter
	START_ID = 784+1
	WIDTH = 5
	for i in range(26):
		tile_id = START_ID + i % WIDTH + (i // WIDTH) * 128
		letter_string = chr(ord('A') + i)
		dict_id_to_letter[tile_id] = letter_string
	dict_id_to_letter[0] = " "





#-----------------------------------------------------#
#-------------------- [Hard-code] --------------------#

def _SetDictWallHardcoded():
	'''
	 This sets up the dictionary by hardcoding them in
	 They are generated by first reading the tilesheet prior (with TY's setup)
	'''
	global dict_id_to_wall
	log.Must(f"   Setting up dictionary for grid status - Hardcode Method")

	dict_id_to_wall[273] = (1, 1, 1, 1)
	dict_id_to_wall[274] = (0, 0, 0, 1)
	dict_id_to_wall[275] = (0, 0, 0, 2)
	dict_id_to_wall[276] = (1, 1, 1, 1)
	dict_id_to_wall[277] = (1, 1, 0, 0)
	dict_id_to_wall[278] = (2, 1, 0, 0)
	dict_id_to_wall[279] = (2, 2, 0, 0)
	dict_id_to_wall[280] = (0, 0, 1, 1)
	dict_id_to_wall[281] = (0, 0, 1, 2)
	dict_id_to_wall[282] = (0, 0, 2, 2)
	dict_id_to_wall[401] = (1, 0, 0, 0)
	dict_id_to_wall[402] = (1, 0, 0, 1)
	dict_id_to_wall[403] = (1, 0, 0, 2)
	dict_id_to_wall[404] = (0, 0, 0, 0)
	dict_id_to_wall[405] = (1, 1, 0, 1)
	dict_id_to_wall[406] = (2, 1, 0, 1)
	dict_id_to_wall[407] = (1, 1, 0, 2)
	dict_id_to_wall[408] = (2, 1, 0, 2)
	dict_id_to_wall[409] = (2, 2, 0, 1)
	dict_id_to_wall[410] = (2, 2, 0, 2)
	dict_id_to_wall[529] = (2, 0, 0, 0)
	dict_id_to_wall[530] = (2, 0, 0, 1)
	dict_id_to_wall[531] = (2, 0, 0, 2)
	dict_id_to_wall[532] = (1, 1, 0, 0)
	dict_id_to_wall[533] = (1, 0, 1, 1)
	dict_id_to_wall[534] = (2, 0, 1, 1)
	dict_id_to_wall[535] = (1, 0, 1, 2)
	dict_id_to_wall[536] = (2, 0, 1, 2)
	dict_id_to_wall[537] = (1, 0, 2, 2)
	dict_id_to_wall[538] = (2, 0, 2, 2)
	dict_id_to_wall[657] = (1, 1, 1, 1)
	dict_id_to_wall[658] = (1, 1, 1, 1)
	dict_id_to_wall[659] = (2, 1, 1, 1)
	dict_id_to_wall[660] = (1, 1, 1, 2)
	dict_id_to_wall[661] = (2, 2, 1, 1)
	dict_id_to_wall[662] = (1, 1, 2, 2)
	dict_id_to_wall[663] = (2, 1, 1, 2)
	dict_id_to_wall[664] = (2, 2, 1, 2)
	dict_id_to_wall[665] = (2, 1, 2, 2)
	dict_id_to_wall[666] = (2, 2, 2, 2)

	dict_id_to_wall[2147483921] = (1, 1, 1, 1)
	dict_id_to_wall[1073742097] = (1, 1, 1, 1)
	dict_id_to_wall[3221225745] = (1, 1, 1, 1)
	dict_id_to_wall[2147483922] = (0, 0, 0, 1)
	dict_id_to_wall[1073742098] = (0, 0, 1, 0)
	dict_id_to_wall[3221225746] = (0, 0, 1, 0)
	dict_id_to_wall[2147483923] = (0, 0, 0, 2)
	dict_id_to_wall[1073742099] = (0, 0, 2, 0)
	dict_id_to_wall[3221225747] = (0, 0, 2, 0)
	dict_id_to_wall[2147483924] = (1, 1, 1, 1)
	dict_id_to_wall[1073742100] = (1, 1, 1, 1)
	dict_id_to_wall[3221225748] = (1, 1, 1, 1)
	dict_id_to_wall[2147483925] = (1, 1, 0, 0)
	dict_id_to_wall[1073742101] = (1, 1, 0, 0)
	dict_id_to_wall[3221225749] = (1, 1, 0, 0)
	dict_id_to_wall[2147483926] = (1, 2, 0, 0)
	dict_id_to_wall[1073742102] = (2, 1, 0, 0)
	dict_id_to_wall[3221225750] = (1, 2, 0, 0)
	dict_id_to_wall[2147483927] = (2, 2, 0, 0)
	dict_id_to_wall[1073742103] = (2, 2, 0, 0)
	dict_id_to_wall[3221225751] = (2, 2, 0, 0)
	dict_id_to_wall[2147483928] = (0, 0, 1, 1)
	dict_id_to_wall[1073742104] = (0, 0, 1, 1)
	dict_id_to_wall[3221225752] = (0, 0, 1, 1)
	dict_id_to_wall[2147483929] = (0, 0, 1, 2)
	dict_id_to_wall[1073742105] = (0, 0, 2, 1)
	dict_id_to_wall[3221225753] = (0, 0, 2, 1)
	dict_id_to_wall[2147483930] = (0, 0, 2, 2)
	dict_id_to_wall[1073742106] = (0, 0, 2, 2)
	dict_id_to_wall[3221225754] = (0, 0, 2, 2)
	dict_id_to_wall[2147484049] = (0, 1, 0, 0)
	dict_id_to_wall[1073742225] = (1, 0, 0, 0)
	dict_id_to_wall[3221225873] = (0, 1, 0, 0)
	dict_id_to_wall[2147484050] = (0, 1, 0, 1)
	dict_id_to_wall[1073742226] = (1, 0, 1, 0)
	dict_id_to_wall[3221225874] = (0, 1, 1, 0)
	dict_id_to_wall[2147484051] = (0, 1, 0, 2)
	dict_id_to_wall[1073742227] = (1, 0, 2, 0)
	dict_id_to_wall[3221225875] = (0, 1, 2, 0)
	dict_id_to_wall[2147484052] = (0, 0, 0, 0)

	dict_id_to_wall[1073742228] = (0, 0, 0, 0)
	dict_id_to_wall[3221225876] = (0, 0, 0, 0)
	dict_id_to_wall[2147484053] = (1, 1, 0, 1)
	dict_id_to_wall[1073742229] = (1, 1, 1, 0)
	dict_id_to_wall[3221225877] = (1, 1, 1, 0)
	dict_id_to_wall[2147484054] = (1, 2, 0, 1)
	dict_id_to_wall[1073742230] = (2, 1, 1, 0)
	dict_id_to_wall[3221225878] = (1, 2, 1, 0)
	dict_id_to_wall[2147484055] = (1, 1, 0, 2)
	dict_id_to_wall[1073742231] = (1, 1, 2, 0)
	dict_id_to_wall[3221225879] = (1, 1, 2, 0)
	dict_id_to_wall[2147484056] = (1, 2, 0, 2)
	dict_id_to_wall[1073742232] = (2, 1, 2, 0)
	dict_id_to_wall[3221225880] = (1, 2, 2, 0)
	dict_id_to_wall[2147484057] = (2, 2, 0, 1)
	dict_id_to_wall[1073742233] = (2, 2, 1, 0)
	dict_id_to_wall[3221225881] = (2, 2, 1, 0)
	dict_id_to_wall[2147484058] = (2, 2, 0, 2)
	dict_id_to_wall[1073742234] = (2, 2, 2, 0)
	dict_id_to_wall[3221225882] = (2, 2, 2, 0)
	dict_id_to_wall[2147484177] = (0, 2, 0, 0)
	dict_id_to_wall[1073742353] = (2, 0, 0, 0)
	dict_id_to_wall[3221226001] = (0, 2, 0, 0)
	dict_id_to_wall[2147484178] = (0, 2, 0, 1)
	dict_id_to_wall[1073742354] = (2, 0, 1, 0)
	dict_id_to_wall[3221226002] = (0, 2, 1, 0)
	dict_id_to_wall[2147484179] = (0, 2, 0, 2)
	dict_id_to_wall[1073742355] = (2, 0, 2, 0)
	dict_id_to_wall[3221226003] = (0, 2, 2, 0)
	dict_id_to_wall[2147484180] = (1, 1, 0, 0)
	dict_id_to_wall[1073742356] = (1, 1, 0, 0)
	dict_id_to_wall[3221226004] = (1, 1, 0, 0)
	dict_id_to_wall[2147484181] = (0, 1, 1, 1)
	dict_id_to_wall[1073742357] = (1, 0, 1, 1)
	dict_id_to_wall[3221226005] = (0, 1, 1, 1)
	dict_id_to_wall[2147484182] = (0, 2, 1, 1)
	dict_id_to_wall[1073742358] = (2, 0, 1, 1)
	dict_id_to_wall[3221226006] = (0, 2, 1, 1)
	dict_id_to_wall[2147484183] = (0, 1, 1, 2)
	dict_id_to_wall[1073742359] = (1, 0, 2, 1)

	dict_id_to_wall[3221226007] = (0, 1, 2, 1)
	dict_id_to_wall[2147484184] = (0, 2, 1, 2)
	dict_id_to_wall[1073742360] = (2, 0, 2, 1)
	dict_id_to_wall[3221226008] = (0, 2, 2, 1)
	dict_id_to_wall[2147484185] = (0, 1, 2, 2)
	dict_id_to_wall[1073742361] = (1, 0, 2, 2)
	dict_id_to_wall[3221226009] = (0, 1, 2, 2)
	dict_id_to_wall[2147484186] = (0, 2, 2, 2)
	dict_id_to_wall[1073742362] = (2, 0, 2, 2)
	dict_id_to_wall[3221226010] = (0, 2, 2, 2)
	dict_id_to_wall[2147484305] = (1, 1, 1, 1)
	dict_id_to_wall[1073742481] = (1, 1, 1, 1)
	dict_id_to_wall[3221226129] = (1, 1, 1, 1)
	dict_id_to_wall[2147484306] = (1, 1, 1, 1)
	dict_id_to_wall[1073742482] = (1, 1, 1, 1)
	dict_id_to_wall[3221226130] = (1, 1, 1, 1)
	dict_id_to_wall[2147484307] = (1, 2, 1, 1)
	dict_id_to_wall[1073742483] = (2, 1, 1, 1)
	dict_id_to_wall[3221226131] = (1, 2, 1, 1)
	dict_id_to_wall[2147484308] = (1, 1, 1, 2)
	dict_id_to_wall[1073742484] = (1, 1, 2, 1)
	dict_id_to_wall[3221226132] = (1, 1, 2, 1)
	dict_id_to_wall[2147484309] = (2, 2, 1, 1)
	dict_id_to_wall[1073742485] = (2, 2, 1, 1)
	dict_id_to_wall[3221226133] = (2, 2, 1, 1)
	dict_id_to_wall[2147484310] = (1, 1, 2, 2)
	dict_id_to_wall[1073742486] = (1, 1, 2, 2)
	dict_id_to_wall[3221226134] = (1, 1, 2, 2)
	dict_id_to_wall[2147484311] = (1, 2, 1, 2)
	dict_id_to_wall[1073742487] = (2, 1, 2, 1)
	dict_id_to_wall[3221226135] = (1, 2, 2, 1)
	dict_id_to_wall[2147484312] = (2, 2, 1, 2)
	dict_id_to_wall[1073742488] = (2, 2, 2, 1)
	dict_id_to_wall[3221226136] = (2, 2, 2, 1)
	dict_id_to_wall[2147484313] = (1, 2, 2, 2)
	dict_id_to_wall[1073742489] = (2, 1, 2, 2)
	dict_id_to_wall[3221226137] = (1, 2, 2, 2)
	dict_id_to_wall[2147484314] = (2, 2, 2, 2)
	dict_id_to_wall[1073742490] = (2, 2, 2, 2)
	dict_id_to_wall[3221226138] = (2, 2, 2, 2)

	dict_id_to_wall[0] = (0, 0, 0, 0)





#--------------------------------------------------#

main()










# End of File
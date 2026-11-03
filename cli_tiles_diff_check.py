'''
Command-Line Tool for ... TBA
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_tiles_diff_check.py

'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils

import os
import shutil
import subprocess
from PIL import Image, ImageChops, ImageDraw

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# File names
file_name = "tiles.png"
filepath_diff_highlight = file_utils.GetInputFolder() + "tiles_highlights_DELETE.png" # This file rests in the input folder

# User-based filepaths & app of choice
curr_user = "Quang"    # Change this when running on a different computer
config_user = {}
config_user["TY"] = {
	"app_path":        "Preview",
	"folder_download": "/Users/Jimmy/Desktop",
	"folder_current":  "/Users/Jimmy/Documents/10 Star Iliad tasks/00-Tiling/10-workspace",
}
config_user["Quang"] = {
	"app_path":        r"C:\Program Files\ImageGlass\ImageGlass.exe",
	"folder_download": r"E:\Downloads",
	"folder_current":  r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\StarIliad\Assets\Graphics",
#	"app_path":        "C:\\Program Files\\ImageGlass\\ImageGlass.exe",
#	"folder_download": "E:\\Downloads\\",
#	"folder_current":  "C:\\Users\\qtran\\Desktop\\PROJECT Whale Nebula\\StarIliad\\Assets\\Graphics\\",
}

# Color of the pixels in the output hignlight tilesheet
hex_base  = '#000000' # Black
hex_pixel = '#00FFFF' # Bright blue
hex_tile  = '#FF0000' # Red





#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Identify the paths automatically based on user's system
	curr_user_config = config_user[curr_user]
	app_path        = curr_user_config["app_path"]
	folder_download = file_utils.FixFolderPath(curr_user_config["folder_download"])
	folder_current  = file_utils.FixFolderPath(curr_user_config["folder_current"])
	img_path_dl = folder_download + file_name
	img_path_pj = folder_current  + file_name

    # Error-check in case file does not exist
#	if not os.path.exists(app_path):    log.Must(f"[ERROR] Image-viewing app not found at {app_path}"); return
	if not os.path.exists(img_path_dl): log.Must(f"[ERROR] Downloaded Tilesheet PNG not found at {img_path_dl}"); return
	if not os.path.exists(img_path_pj): log.Must(f"[ERROR] In-Project Tilesheet PNG not found at {img_path_pj}"); return

	# Step 1 - Check diff, then output the diff PNG
	log.Must(f"  Checking the following:\n    {img_path_dl}\n  with\n    {img_path_pj}")
	compare_images(img_path_dl, img_path_pj, filepath_diff_highlight)
	log.Must(f"  Difference highlight saved to: {filepath_diff_highlight}")
	log.Must("")

	# Step 2 - Open image automatically
	try:
		if curr_user == "TY": subprocess.run(["open", "-a", app_path, filepath_diff_highlight])
		else:                 subprocess.Popen([app_path, filepath_diff_highlight])
	except Exception as e:
		log.Must(f"Failed to open image:\n  {e}")

	# Step 3 - Ask user to confirm changes
	user_input = input(f"  Copy tilesheet to new location? (Y/N) ")
	if user_input[0].lower() != 'y': log.Must(''); log.Must("  No changes applied.\n"); os.remove(filepath_diff_highlight); return
	os.remove(filepath_diff_highlight)
	log.Must("")

	# Step 4 - Copy tilesheet to new location
	shutil.copy(img_path_dl, img_path_pj)
	log.Must("  Tilesheet overwritten.")
	log.Must("")





#-------------------------------------------------#
#-------------------- [Logic] --------------------#

def compare_images(image1_path, image2_path, output_path, grid_size=16):
	with Image.open(image1_path) as image1, Image.open(image2_path) as image2:
		if image1.size != image2.size:
			raise ValueError(
				f"Images must have the same dimensions. "
				f"Got {image1.size} and {image2.size}."
			)

		image1 = image1.convert("RGBA")
		image2 = image2.convert("RGBA")

		difference = ImageChops.difference(image1, image2)

		# Mark a pixel as changed if any RGBA channel differs.
		channels = difference.split()
		mask = channels[0]
		for channel in channels[1:]:
			mask = ImageChops.lighter(mask, channel)
		mask = mask.point(lambda value: 255 if value > 0 else 0)

		width, height = image1.size
		output = Image.new("RGB", image1.size, hex_base)
		draw = ImageDraw.Draw(output)

		# Color each grid cell blue if it contains at least one changed pixel.
		for y in range(0, height, grid_size):
			for x in range(0, width, grid_size):
				right = min(x + grid_size, width)
				bottom = min(y + grid_size, height)

				cell_mask = mask.crop((x, y, right, bottom))
				if cell_mask.getbbox() is not None:
					draw.rectangle(
						(x, y, right - 1, bottom - 1),
						fill=hex_tile
					)

		# Paint the differing pixels red on top of the blue cells.
		red = Image.new("RGB", image1.size, hex_pixel)
		output.paste(red, mask=mask)

		output.save(output_path)
#        print(f"Difference image saved to: {output_path}")





#--------------------------------------------------#

main()










# End of File
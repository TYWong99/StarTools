'''
Command-Line Tool for ... TBA
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_tiles_diff_check.py

'''
import argparse
import logic.common.log_utils as log
from PIL import Image, ImageChops, ImageDraw
import shutil

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# In-editor object layers for nodes & routes
hex_base  = '#000000' # Black
hex_pixel = '#00FFFF' # Bright blue
hex_tile  = '#FF0000' # Red

# TY's directory
filepath_old_tilesheet  = '/Users/Jimmy/Desktop/tiles.png'
filepath_new_tilesheet  = '/Users/Jimmy/Desktop/tiles_new_unchecked.png'
filepath_diff_highlight = '/Users/Jimmy/Desktop/_diff.png'
filepath_app_tilesheet  = '/Users/Jimmy/Desktop/tiles_at_new_location.png'

# TODO Quang's directory - Edit your filepaths here when testing
filepath_old_tilesheet  = '/Users/Jimmy/Desktop/tiles.png'
filepath_new_tilesheet  = '/Users/Jimmy/Desktop/tiles_new_unchecked.png'
filepath_diff_highlight = '/Users/Jimmy/Desktop/_diff.png'
filepath_app_tilesheet  = '/Users/Jimmy/Desktop/tiles_at_new_location.png'





#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
#	parser.add_argument('filename', type=str, help = arg_help1)
#	parser.add_argument('--rewind', action='store_true')
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Step 1 - Check diff, then output the diff PNG
	log.Must(f"  Checking the following:\n    {filepath_old_tilesheet}\n  with\n    {filepath_new_tilesheet}")
#	compare_images_old(filepath_old_tilesheet, filepath_new_tilesheet, filepath_diff_highlight)
	compare_images(filepath_old_tilesheet, filepath_new_tilesheet, filepath_diff_highlight)
	log.Must(f"  Difference highlight saved to: {filepath_diff_highlight}")
	log.Must("")

	# Step 2 - Ask user to confirm changes
	user_input = input(f"  Copy tilesheet to new location? (Y/N) ")
	if user_input[0].lower() != 'y': log.Must(''); return
	log.Must("")

	# Step 3 - Copy tilesheet to new location
#	os.makedirs(filepath_app_tilesheet, exist_ok = True)
	shutil.copy(filepath_new_tilesheet, filepath_app_tilesheet)
	log.Must("  Done")
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




def compare_images_old(image1_path, image2_path, output_path):
    with Image.open(image1_path) as image1, Image.open(image2_path) as image2:
        if image1.size != image2.size:
            raise ValueError(
                f"Images must have the same dimensions. "
                f"Got {image1.size} and {image2.size}."
            )

        # Convert both images to the same format, including transparency.
        image1 = image1.convert("RGBA")
        image2 = image2.convert("RGBA")

        difference = ImageChops.difference(image1, image2)

        # Build a mask that marks a pixel if any RGBA channel differs.
        channels = difference.split()
        mask_pixel = channels[0]
        for channel in channels[1:]:
            mask_pixel = ImageChops.lighter(mask_pixel, channel)

        mask_pixel = mask_pixel.point(lambda value: 255 if value > 0 else 0)

        # Black for matching pixels; red for changed pixels.
        output = Image.new("RGB", image1.size, hex_base)
 #       tile   = Image.new("RGB", image1.size, hex_tile)
        pixel  = Image.new("RGB", image1.size, hex_tile)
#        output.paste(tile,  mask = mask_pixel)
        output.paste(pixel, mask = mask_pixel)

        output.save(output_path)
        print(f"Difference image saved to: {output_path}")





#--------------------------------------------------#

main()










# End of File
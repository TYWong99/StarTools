'''
Command-Line Tool to search all levels for a tile ID (+ its 7 other permutations)

This is useful for when we need references and would like to know where a tile
has been used. Also good for when we suspect a tile ID has become obsoleted and
would like to confirm that no levels are using it.

USAGE EXAMPLE:
	python cli_search.py 657    # where 657 is a number ID assigned by TILED
'''

import sys
import time
import argparse
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils
import logic.finder.tile_finder as tile_finder
import logic.common.log_utils as log


#--------------------------------------------------#
'''Main'''

tool_description = 'Searches all levels for usecases of a tile ID'
arg_desc_tile_id = 'ID of the tile we wish to search'
arg_desc_prefix = 'Narrows the search selection requiring files match a prefix. For Ex: "--prefix=f" targets the stomach area'
arg_desc_verbosity = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'


def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('tile_id', type=int, help=arg_desc_tile_id)
    parser.add_argument('--prefix', type=str, default=None, help=arg_desc_prefix)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=0, help=arg_desc_verbosity)
    args = parser.parse_args()

    log.SetVerbosityLevel(args.v)
    log.Must(f'Running cli_find on TILE ID {args.tile_id} ...')
    
    true_tile_id = args.tile_id + 1 # TILE's funny offset thing
    tiles_to_search = tiled_utils.GetTileIdPermutations(true_tile_id)
    files_to_search = file_utils.GetAllLevelFiles()
    
    # prune the list of files to search if "prefix" is specified
    if args.prefix is not None:
        log.Info(f"Narrowing search to select prefix '{args.prefix}'")
        files_to_search = [fn for fn in files_to_search if file_utils.StripFilename(fn).startswith(args.prefix)]
        
    num_files =  len(files_to_search)
    log.Must(f"Preparing to search {num_files} files...\n")
    
    files_w_errors = []     # List of files that could not be searched, likely due to using wrong encoding
    files_w_matches = {}    # dict mapping file_name to another dict of {tile_layer_name : coordinates}
                            # In other words: {file_name : {tile_layer_name : [(x1,y1), (x2, y2), ...]}
    for num, filename in enumerate(files_to_search):
        search_results = tile_finder.SearchFileForTileIds(filename, tiles_to_search)
        PrintProgressBar(num + 1, num_files, prefix='Find Progress:', suffix=f'processing {_FormatName(filename)}', length=30)
        if search_results:
            files_w_matches[file_utils.StripFilename(filename)] = search_results
        elif search_results is None:
            files_w_errors.append(filename)
    
    time.sleep(0.25)
    if files_w_errors:
        log.Info(f"\nWARNING: The below {len(files_w_errors)} files were unsearchable! Likely do to their encoding")
        for erred_file in files_w_errors:
            log.Info(f" - {file_utils.StripFilename(erred_file)}")
            
    if files_w_matches:
        log.Must(f"\n\nSUCCESS! TILE ID {args.tile_id} was discovered in {len(files_w_matches)} files...\n")
        for index, (filename, search_results) in enumerate(files_w_matches.items(), start=1):
            log.Must(f"    {index}. {filename}.xml ".ljust(50, '-'))
            log.Must(tile_finder.FormatSearchResult(search_results))
    else:
        log.Must(f"\nNOT FOUND! TILE ID {args.tile_id} was not used in any files...")
    
    log.Must(f"\n\ncli_find concluded! {len(files_w_matches)} files found with a match!")


def PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='='):
    """Call in a loop to create terminal progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()


def _FormatName(name):
    name = file_utils.StripFilename(name)
    if len(name) > 20:
        # Truncate and add "..." to the end
        formatted_name = name[:17] + "..."
    else:
        # Pad with spaces to make it 20 characters
        formatted_name = name.ljust(20)
    return formatted_name

#--------------------------------------------------#



main()
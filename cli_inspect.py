'''
Command-Line Tool to inspect & count a level's rectangles, polygons, and polylines

TODO: Expand this tool to do additional things like count the number of lights, AT's, relic blocks,
and so forth. Make the tool able to run on all files and let us sort which levels are most in need
of reddressment

USAGE EXAMPLE:
    python cli_inspect.py j01
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.pattern.pattern_matcher as PM
import logic.remapper.tile_remapper as TM

#--------------------------------------------------#
'''Pattern Lists'''



#--------------------------------------------------#
'''Main'''

arg_description = "Inspect a tiled level XML to inform aboutthe level's costs in terms of colliders, lights, and more"
arg_help1 = 'Name of the tiled level XML in which to count the rectangles, polygons, and polylines'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

def IsPolyline(tiled_object):
    polyline = tiled_object.find('polyline')
    if polyline is not None:
        return True
        
    return False

def IsPolygon(tiled_object):    
    polygon = tiled_object.find('polygon')
    if polygon is not None:
        return True
        
    return False

def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    
    obj_grp = playdo.GetObjectGroup("collisions", False)
    num_rects = 0
    num_polys = 0
    num_lines = 0
    for shape in obj_grp:
        if IsPolygon(shape):
            num_polys += 1
        elif IsPolyline(shape):
            num_lines += 1
        else:
            num_rects += 1
    
    print(f'Found {num_rects} rectangles, {num_polys} polygons, and {num_lines} lines!')
        
    
    #breakpoint()
    
    # Flush changes to File!
    #playdo.Write()


#--------------------------------------------------#

main()










# End of File
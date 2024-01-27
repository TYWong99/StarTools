''' Command-Line Tool to auto-add ground, BBs, and skell reefs to a level. 
    
    <summary>
    
    USAGE: <FILL

'''
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

#--------------------------------------------------#
'''Pattern Lists'''

# Breakable Blocks and Skell Reefs
_LIST_PATTERN_BB = [
    "breakables",
    "reef1",
    "reef2",
    "reef3",
    "reef4",
    "reef5",
    "reef6"
]

# Ground and Slopes
_LIST_PATTERN_GROUND = [
    "ground",
    "owp_flat",
    "owp_1x1",
    "owp_1x2",
    "owp_1x4",
    "slope_1x1",
    "slope_1x2",
    "slope_1x2a",
    "slope_1x2b",
    "slope_1x4",
    "slope_1x4a"
]

# Crystals
_LIST_CRYSTAL = [
    "crystal_1x1",
    "crystal_1x2",
    "crystal_1x2a",
    "crystal_1x2b",
    "crystal_1x4",
    "crystal_solid",
]


#--------------------------------------------------#
'''Main'''

def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description='Process a tiled level XML and add BB + reef objects to a "_BB" layer.')
    parser.add_argument('filename', type=str, help='Name of the tiled level XML to add BB & reef objects to')
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
    args = parser.parse_args()

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetLevelRoot() + args.filename)

    # Create a PatternMatcher for "_BB" : Breakable Blocks and Skell Reefs
    pattern_matcher_bb = PM.PatternMatcher()
    for pattern in _LIST_PATTERN_BB:
        pattern_matcher_bb.LoadPattern(pattern_root + pattern + ".xml")

    # Create a PatternMatcher for "fg_raw" : Ground and Slopes
    pattern_matcher_ground = PM.PatternMatcher()
    for pattern in _LIST_PATTERN_GROUND:
        pattern_matcher_ground.LoadPattern(pattern_root + pattern + ".xml")
    
    # Create a PatternMatcher for "fg_crystal" : Crystals
    pattern_matcher_crystal = PM.PatternMatcher()
    for pattern in _LIST_CRYSTAL:
        pattern_matcher_crystal.LoadPattern(pattern_root + pattern + ".xml")
        
    # Perform the matching - mold the playdo
    pattern_matcher_bb.FindAndCreate(playdo, "_BB", "collisions_BB", allow_repeats = False)
    pattern_matcher_ground.FindAndCreate(playdo, "fg_raw", "collisions", allow_repeats = False)
    pattern_matcher_crystal.FindAndCreate(playdo, "fg_crystal", "collisions_crystal", allow_repeats = False)
    
    # Flush changes to File!
    playdo.Write()

main()



#--------------------------------------------------#










# End of File
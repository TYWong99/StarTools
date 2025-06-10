'''
Convert the old BB format to new ones
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# For logging



#--------------------------------------------------#
'''Public Functions'''

def logic(playdo):
	log.Info("\n--- Updating old BB format to newer ones ---\n")

	count = 0
	objectgroup_bb = playdo.GetObjectGroup("collisions_BB", False)
	objectgroup_new1 = playdo.GetObjectGroup("collisions_BB 1", True)
	objectgroup_new2 = None
	for object in objectgroup_bb:
		is_bb = False
		if fix_1x1(object): is_bb = True
		if fix_2x2(object): is_bb = True
		if is_bb:
			count += 1
			objectgroup_new1.append(object)
		else:
			if objectgroup_new2 == None: objectgroup_new2 = playdo.GetObjectGroup("collisions_BB 2", True)
			objectgroup_new2.append(object)
	log.Info(f"{count} BB have been fixed")

	count = 0
	list_door = playdo.GetAllObjectsWithName("door")
	for obj in list_door:
		if tiled_utils.GetPropertyFromObject(obj, "_type") == "BLANK":
			obj.set("type", "9")	# Color it white
			continue
		obj.set("type", "8")		# Color it pink
		tiled_utils.SetPropertyOnObject( obj, "fg_sort",         "fg_tiles,-1" )
		tiled_utils.SetPropertyOnObject( obj, "fg_sort_on_open", "fg_tiles,23" )
		count += 1
	log.Info(f"{count} valve doors have been fixed")

	log.Must("\n--- All Procedures have finished! ---\n")





#--------------------------------------------------#
'''Utility'''

def fix_1x1( bb_obj ):
	if bb_obj.get("width")  != "16": return False
	if bb_obj.get("height") != "16": return False
	add_new_bb_properties(bb_obj, "LUNG_1x1")
	return True

def fix_2x2( bb_obj ):
	if bb_obj.get("width")  != "32": return False
	if bb_obj.get("height") != "32": return False
	add_new_bb_properties(bb_obj, "LUNG_2x2")
	return True



def add_new_bb_properties( bb_obj, str_type = "_1x1" ):
	# Replace properties
	bb_obj.set("name", "relic_block")
	add_property_if_absent( bb_obj, "_sort",   "fg_tiles,-1" )
	add_property_if_absent( bb_obj, "_type",   str_type )
	add_property_if_absent( bb_obj, "autoset", "" )

def add_property_if_absent( bb_obj, p_name, p_value ):
	# Return if property is already present
	for curr_property in bb_obj.find('properties').findall('property'):
		if curr_property.get('name') == p_name:
			return

	# Otherwise add new property to object
	tiled_utils.SetPropertyOnObject( bb_obj, p_name, p_value )




#--------------------------------------------------#










# End of File
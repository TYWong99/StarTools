'''
Logic module that can
 - TBA

Steps:
 1.	Filter the applicable collision objects from playdo as polygons
 2.	Merge all polygons that are adjacent into big simple polygons
 3.	Split into smaller polygons based on methods
 4.	Output polygons into a new object layer

USAGE EXAMPLE:
	main_logic.logic(playdo)
	raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
	pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
	conflict.FixConflicts(playdo, pruned_dict)
'''

import os
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

import shapely
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
import numpy as np

#-----------------------------------------------------#
#-------------------- [Variables] --------------------#

# Output
_output_folder1 = "output/"
_output_folder2 = _output_folder1 + "levels/"
_output_file    = _output_folder1 + "_merged.txt"

# Names
layer_name_big_poly = "_big_poly"
layer_name_final    = "collisions split"
layer_name_excluded = "collisions excluded"

# Config
config_always_merge_big_poly = True



#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def logic(playdo, arguments):
	'''TODO'''
	log.Must('')
	log.Must(f'  Starting procedure...')

	# Check if Big Polygon layer exists prior
	layer = playdo.GetObjectGroup(layer_name_big_poly, discard_old = False, create_new = False)
	does_big_poly_layer_exist = (layer != None)
	log.Must('')
	log.Must(f' Big Polygon Layer exists? {does_big_poly_layer_exist}')

	# Skips checking big poly if already
	if not does_big_poly_layer_exist or config_always_merge_big_poly:
#		log.Must('')
		log.Must(f'  vvvvv New Big Polygon layer will now be created vvvvv')

	 	# Process 1 - Filter the applicable collision objects from playdo as polygons
		list_objects, list_excluded = FilterObjects(playdo)
		list_vertices = ObjectToVertices(list_objects)

	 	# Process 2 - Merge all polygons that are adjacent (recursively)
		list_merged_verrices = MergePolygons(list_vertices)
#		SetBigPolygons(playdo, list_merged_verrices, list_excluded)
		SetVerticesToObjectLayer(playdo, list_merged_verrices, layer_name_big_poly)
		if len(list_excluded) > 0:
			layer_excluded = playdo.GetObjectGroup(layer_name_excluded, discard_old = True, create_new = True)
			for obj in list_excluded: layer_excluded.append(obj)
	else:
		# TODO
		return
		list_merged_verrices = list_vertices

 	# Process 3 - Split into smaller polygons based on methods
	log.Must('')
#	list_split_vertices = SplitPolygonsByGrid(list_merged_verrices, 1)
	list_split_vertices = SplitPolygonsByGrid(list_merged_verrices, 2)

 	# Process 4 - Output polygons into a new object layer
#	MakeNewObjectLayer(playdo, list_split_vertices)
	SetVerticesToObjectLayer(playdo, list_split_vertices, layer_name_final)

	log.Must('')



#----------------------------------------------------------#
#-------------------- [Testing Ground] --------------------#

def SplitPolygonsByGrid(list_merged_verrices, grid_size_unit):
	log.Extra('')
	log.Must(f'  Splitting {len(list_merged_verrices)} objects, by grid of size {grid_size_unit}...')
	grid_size_px = grid_size_unit * 16

	list_new_vertices = []
	for vertices in list_merged_verrices:
		polygon = VerticesToPolygon(vertices)
		pieces = split_polygon_by_grid( polygon, grid_size_px )
		for polygon_piece in pieces: list_new_vertices.append(PolygonToVertices(polygon_piece))
#		print()
#		print(vertices)
#		print(f"Original polygon split into {len(pieces)} pieces.")
#		for idx, piece in enumerate(pieces[:3]):  # show bounds for first 3 pieces
#			print(f" Piece {idx+1} Bounding Box: {piece.bounds}")

	log.Must(f'   Split into a total of {len(list_new_vertices)} objects...')
	return list_new_vertices


def split_polygon_by_grid(polygon, grid_size_px = 1):
    """
    Splits a shapely polygon into pieces no larger than max_size x max_size.
    """
    # 1. Get the bounding box limits of the input polygon
    minx, miny, maxx, maxy = polygon.bounds
    
    # 2. Create grid sequences with intervals of max_size
    x_coords = np.arange(minx, maxx + grid_size_px, grid_size_px)
    y_coords = np.arange(miny, maxy + grid_size_px, grid_size_px)
    
    split_pieces = []
    
    # 3. Iterate through every cell in the grid
    for i in range(len(x_coords) - 1):
        for j in range(len(y_coords) - 1):
            # Create a 10x10 bounding box for the current grid tile
            grid_box = box(x_coords[i], y_coords[j], x_coords[i+1], y_coords[j+1])
            
            # 4. Intersect the original polygon with this box tile
            intersection_piece = polygon.intersection(grid_box)
            
            # 5. Save the piece if it contains a valid polygon structure
            if not intersection_piece.is_empty:
                # If a tile splits a complex shape into multiple separate parts,
                # flatten them out into individual single polygons.
                if isinstance(intersection_piece, MultiPolygon):
                    for sub_poly in intersection_piece.geoms:
                        if isinstance(sub_poly, Polygon) and not sub_poly.is_empty:
                            split_pieces.append(sub_poly)
                elif isinstance(intersection_piece, Polygon):
                    split_pieces.append(intersection_piece)
                    
    return split_pieces




def MakeNewObjectLayer(playdo, list_vertices):
	SetVerticesToObjectLayer(playdo, list_vertices, layer_name_final)
	return

	log.Extra('')
	log.Must(f'  Doing stuff... {4}')

	# Big polygon objects
	layer_split_poly = playdo.GetObjectGroup(layer_name_final, discard_old = True, create_new = True)
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		tiled_utils.SetVerticesOnObject(obj, vertices)
		layer_split_poly.append(obj)

def SetVerticesToObjectLayer(playdo, list_vertices, layer_name):
	log.Extra('')
	log.Must(f'  Setting {len(list_vertices)} polygon objects onto \"{layer_name}\" layer...')
	layer = playdo.GetObjectGroup(layer_name, discard_old = True, create_new = True)
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		tiled_utils.SetVerticesOnObject(obj, vertices)
		layer.append(obj)





#-------------------------------------------------------#
#-------------------- [Procedure 1] --------------------#

def FilterObjects(playdo):
	log.Extra('')
	log.Must(f'  Filtering objects from playdo...')
	list_objectgroup = playdo.GetAllObjectgroup()
	list_obj      = []
	list_excluded = []
	for layer in list_objectgroup:
		layer_name = layer.get('name')
		if not layer_name.startswith('collisions'): continue
		for obj in layer:
			if obj.find('polyline') != None or obj.find('properties') != None:
				list_excluded.append(obj)
			else:
				list_obj.append(obj)
#	print(len(list_obj))
	return list_obj, list_excluded

def ObjectToVertices(list_obj):
	log.Must(f'   Converting {len(list_obj)} objects into vertices / polypoints...')
	count = 0
	list_vertices = []
	for obj in list_obj:
		count += 1
		log.Extra(f'    Polygon {count}:')
		vertices = tiled_utils.GetVerticesFromObject(obj)
		for index, pt_tuple in enumerate(vertices):
			new_x = int(pt_tuple[0])
			new_y = int(pt_tuple[1])
			vertices[index] = (new_x, new_y)
			log.Extra(f'     {index} : {vertices[index]}')
			if new_x % 4 != 0 or new_y % 4 != 0: log.Must(f'\nWARNING! Vertex position is not snapped to grid! {vertices[index]}')
#			print(index)
		list_vertices.append(vertices)
	x=1
	return list_vertices



#-------------------------------------------------------#
#-------------------- [Procedure 2] --------------------#

def MergePolygons(list_vertices):
	'''TODO recursive'''
	log.Extra('')
	log.Must(f'  Merging {len(list_vertices)} polygons...')

	list_polygon = []
	for vertices in list_vertices:
		list_polygon.append(Polygon(vertices))
	merged_polygons = unary_union(list_polygon)

	list_new_vertices = []
	if merged_polygons.geom_type != 'MultiPolygon': merged_polygons = MultiPolygon([merged_polygons])
	log.Info(f'   Is MultiPolygon? {merged_polygons.geom_type == "MultiPolygon"}')

	# Simplify the polygons and add vertices into new array
	for polygon in merged_polygons.geoms:
		new_vertices = PolygonToVertices(polygon)
		'''	
			polygon = polygon.simplify(0)    # This removes the collinear points
			new_vertices = []
			for x, y in polygon.exterior.coords:
				pos = (int(x), int(y))
	#			print(pos)
				new_vertices.append(pos)
	#		print(new_vertices)
		'''
		list_new_vertices.append(new_vertices)
	return list_new_vertices

def PolygonToVertices(polygon):
	polygon = polygon.simplify(0)    # This removes the collinear points
	new_vertices = []
	for x, y in polygon.exterior.coords:
		pos = (int(x), int(y))
		new_vertices.append(pos)
	return new_vertices

def VerticesToPolygon(vertices):
	return Polygon(vertices)



def SetBigPolygons(playdo, list_vertices, list_excluded_objects):
	'''TODO'''
	log.Extra('')
	log.Must(f'   Setting {len(list_vertices)} polygons in layer...')

	# Big polygon objects
	SetVerticesToObjectLayer(playdo, list_vertices, layer_name_big_poly)
	'''
	layer_big_poly = playdo.GetObjectGroup(layer_name_big_poly, discard_old = True, create_new = True)
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		tiled_utils.SetVerticesOnObject(obj, vertices)
		layer_big_poly.append(obj)
#		print('make new obj')
	'''

	# Unmodified objects
	if len(list_excluded_objects) == 0: return
	layer_excluded = playdo.GetObjectGroup(layer_name_excluded, discard_old = True, create_new = True)
	for obj in list_excluded_objects: layer_excluded.append(obj)



#-------------------------------------------------------#
#-------------------- [Procedure 3] --------------------#



#-------------------------------------------------------#
#-------------------- [Procedure 4] --------------------#



#-----------------------------------------------------------#
#-------------------- [General Utility] --------------------#
# to be relocated?

def _Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )

def _FormatNumS2TU(num_in_str):
	'''Shortcut, for converting string (coordinates measured in pixels) intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( round(float(num_in_str))/16 ))





#--------------------------------------------------#










# End of File
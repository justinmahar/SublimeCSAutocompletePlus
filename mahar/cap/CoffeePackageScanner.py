
from CoffeeDocumentScanner import CoffeeDocumentScanner

class CoffeePackageScanner:

	def __init__(self, view_id_to_file_contents_dict, current_view_id, package_directories, excluded_directories, restricted_to_directories):
		pass

	def get_type_for_operation(self, operation_string, selection_region):
		pass
		
		# Util function:
			# Collapse strings.
			# Collapse arrays.
			# Collapse regex. 
			# Collapse etc.
			# Collapse params
			# Replace starting @ with "this."
			# Split by dot operator
			# Return list of tokens
		# Determine type for each token starting at the left-most
		# Check for built-in types (array inits, strings, numbers, regexes)
		# If not a built-in type, 

		return "String"

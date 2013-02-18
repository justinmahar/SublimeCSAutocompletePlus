
from CoffeeDocumentScanner import CoffeeDocumentScanner

class CoffeePackageScanner:

	def __init__(self, view_id_to_file_contents_dict, current_view_id, package_directories, excluded_directories, restricted_to_directories, built_in_types):
		pass

		def get_this_type(self):
			return "String"

		def get_return_type_for_method(self):
			return "String"

		def get_assignment_expression(self, token):
			# Searching for "token = some_expression"
			return "new String()"

		def get_super_type_of(self):
			return "Object"

		def get_(self):
			pass
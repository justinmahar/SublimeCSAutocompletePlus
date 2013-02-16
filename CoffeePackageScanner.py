
from CoffeeDocumentScanner import CoffeeDocumentScanner

class CoffeePackageScanner:

	def __init__(self, view_id_to_file_contents_dict, current_view_id, package_directories, excluded_directories, restricted_to_directories, built_in_types):
		pass

	def extract_expression_type(expression_string):
		# Check for built-in expressions, like [a,b,c], "blah", {}, etc
		# Start from left, use package scanner to determine types of each
		# Return last expression type determined, or None if the chain can't be completed.
		expression_type = ExpressionInfo("String", False)
		return expression_type

	def get_definition_location(expression_string):

		pass

	def tokenize_expression(expression_string):
		# Collapse built-in expressions ("blah" to "", [a, b, c] to [], regex, etc)
		# Replace starting @ with "this."
		# Collapse params
		# Split by dot operator
		return ["this"]

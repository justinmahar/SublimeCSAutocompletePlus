from TokenInfo import TokenInfo


class TokenAnalyzer:

	def __init__(self, package_scanner):
		self.package_scanner = package_scanner

	def extract_expression_type(expression_string):
		# Check for built-in expressions, like [a,b,c], "blah", {}, etc
		# Collapse built-in expressions
		# Split by dot operator
		token_info = TokenInfo("String")
		return token_info
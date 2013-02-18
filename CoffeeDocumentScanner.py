from SearchResult import SearchResult


class CoffeeDocumentScanner:

	def __init__(self, contents):
		self.contents = contents

	# Search for regex backwards from index, taking into account indentation
	def search_backwards_from_index(regex, index):
		search_result = None
		# Horrible matching logic. This is a placeholder.
		match = re.search(regex, self.contents)
		if match:
			search_result = SearchResult()
			search_result.set_line_match(match)
			search_result.set_file_contents(self.contents)
		return search_result

	# Search for regex forwards from beginning of document
	def search_forwards_from_beginning(regex):
		search_result = None
		# Horrible matching logic. This is a placeholder.
		match = re.search(regex, self.contents)
		if match:
			search_result = SearchResult()
			search_result.set_line_match(match)
			search_result.set_file_contents(self.contents)
		return search_result
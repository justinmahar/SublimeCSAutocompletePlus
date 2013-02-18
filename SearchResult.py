

class SearchResult:

	def __init__(self):
		self.file_name = None
		self.view_id = None
		self.file_contents = None
		self.file_lines = None
		self.line_match = None
		self.row_index = -1
		self.column_index = -1
		self.match_start_index = -1

	def is_view(self):
		return self.view_id != None

	def get_row_index(self):
		return self.row_index

	def set_row_index(self, row_index):
		self.row_index = row_index

	def get_column_index(self):
		return self.column_index

	def set_column_index(self, column_index):
		self.column_index = column_index

	def get_match_start_index(self):
		return self.match_start_index

	def set_match_start_index(self, match_start_index):
		self.match_start_index = match_start_index

	def get_file_name(self):
		return self.file_name

	def set_file_name(self, file_name):
		self.file_name = file_name

	def get_file_contents(self):
		return self.file_contents

	def set_file_contents(self, file_contents):
		self.file_contents = file_contents

	def get_view_id(self):
		return self.view_id

	def set_view_id(self, view_id):
		self.view_id = view_id

	def get_line_match(self):
		return self.line_match

	def set_line_match(self, line_match):
		self.line_match = line_match
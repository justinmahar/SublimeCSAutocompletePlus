

class Selection:

	def __init__(self, start_index, end_index):
		if start_index > end_index:
			temp = end_index
			end_index = start_index
			start_index = temp
		self.start_index = start_index
		self.end_index = end_index

	def start(self):
		return self.start_index

	def end(self):
		self.end_index

	def size(self):
		return self.end() - self.start()

	def is_empty(self):
		return (self.start() == self.end())
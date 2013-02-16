
class TokenAnalyzer:

	def __init__(self, name):
		self.name = name
		self.argument_infos = []
		self.return_type_name = None

	def get_name():
		return self.name

	def set_name(name):
		self.name = name

	def get_argument_infos():
		return self.argument_infos

	def has_arguments():
		return (self.get_argument_count() > 0)

	def get_argument_count():
		return len(self.argument_infos)

	def add_argument_info(arg_info):
		self.argument_infos.append(arg_info)

	def get_return_type_name():
		return self.return_type_name

	def set_return_type_name(name):
		self.return_type_name = return_type_name
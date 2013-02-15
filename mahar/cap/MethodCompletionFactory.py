
class MethodCompletionFactory:

	@staticmethod
	def create_completion(method_info, owner_type_info):
		alias = method_info.get_name() + "()"
		insertion = method_info.get_name() + "()"
		completion_tuple = (alias, insertion)
		return completion_tuple
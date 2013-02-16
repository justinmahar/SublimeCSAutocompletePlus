
class PropertyCompletionFactory:

	@staticmethod
	def create_completion(property_info):
		alias = property_info.get_name()
		insertion = property_info.get_name()
		completion_tuple = (alias, insertion)
		return completion_tuple

	

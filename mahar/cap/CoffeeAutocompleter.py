

class CoffeeAutocompleter:

	def __init__(self, package_scanner):
		self.package_scanner = package_scanner

	def get_instance_completions_for_class(class_name):
		return [("instanceVar1", "instanceVar1"), ("instanceMethod1(arg1, arg2)", "instanceMethod1(${1:arg1}, ${2:arg2})")]

	def get_static_completions_for_class(class_name):
		return [("staticVar1", "staticVar1")]

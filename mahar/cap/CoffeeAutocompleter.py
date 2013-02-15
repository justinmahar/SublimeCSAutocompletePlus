

class CoffeeAutocompleter:

	def __init__(self, package_scanner, built_in_completions):
		self.package_scanner = package_scanner

	def get_instance_completions_for_class(self, class_name):
		completions = []
		completions = [("instanceVar1", "instanceVar1"), ("instanceMethod1(arg1, arg2)", "instanceMethod1(${1:arg1}, ${2:arg2})")]
		return completions

	def get_static_completions_for_class(self, class_name):
		completions = []
		completions = [("staticVar1", "staticVar1")]
		return completions
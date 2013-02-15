

class TypeInfo:

	def __init__(self, name):
		self.name = name
		self.super_name = None
		self.constructor = None
		self.static_properties = []
		self.static_methods = []
		self.instance_properties = []
		self.instance_methods = []

	def get_super_name(self):
		return self.super_name

	def set_super_name(self, name):
		self.super_name = name

	def get_constructor_method_info(self):
		return self.constructor

	def set_constructor_method_info(self, method_info):
		self.constructor = method_info

	def get_static_properties(self):
		return self.static_properties

	def add_static_property(self, property_info):
		self.static_properties.append(property_info)

	def get_static_methods(self):
		return self.static_methods

	def add_static_method(self, method_info):
		self.static_methods.append(method_info)

	def get_instance_properties(self):
		return self.instance_properties

	def add_instance_property(self, property_info):
		self.instance_properties.append(property_info)

	def get_instance_methods(self):
		return self.instance_methods

	def add_instance_method(self, method_info):
		self.instance_methods.append(method_info)
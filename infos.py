
class PropertyInfo:
	def __init__(self, name):
		self.name = name
		self.display_name = name
		self.insertion = name
		self.type_name = None

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_display_name(self):
		return self.display_name

	def set_display_name(self, display_name):
		self.display_name = display_name

	def get_insertion(self):
		return self.insertion

	def set_insertion(self, insertion):
		self.insertion = insertion

	def get_type_name(self):
		return self.type_name

	def set_type_name(self, type_name):
		self.type_name = type_name

class ArgumentInfo:

	def __init__(self, name):
		self.name = name
		self.display_name = name
		self.insertion = name
		self.type_name = None

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_display_name(self):
		return self.display_name

	def set_display_name(self, display_name):
		self.display_name = display_name

	def get_insertion(self):
		return self.insertion

	def set_insertion(self, insertion):
		self.insertion = insertion

	def get_type_name(self):
		return self.type_name

	def set_type_name(self, name):
		self.type_name = name

class MethodInfo:

	def __init__(self, name):
		self.name = name
		self.display_name = name
		self.insertion = name
		self.argument_infos = []
		self.return_type_name = None

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_display_name(self):
		return self.display_name

	def set_display_name(self, display_name):
		self.display_name = display_name

	def get_insertion(self):
		return self.insertion

	def set_insertion(self, insertion):
		self.insertion = insertion

	def get_return_type_name(self):
		return self.return_type_name

	def set_return_type_name(self, name):
		self.return_type_name = return_type_name

	def get_argument_infos(self):
		return self.argument_infos

	def add_argument_info(self, arg_info):
		self.argument_infos.append(arg_info)

	def has_arguments(self):
		return (self.get_argument_count() > 0)

	def get_argument_count(self):
		return len(self.argument_infos)

class TypeInfo:

	def __init__(self, name):
		self.name = name
		self.display_name = name
		self.insertion = name
		self.super_type_name = None
		self.constructor_infos = []
		self.static_property_infos = []
		self.static_method_infos = []
		self.instance_property_infos = []
		self.instance_method_infos = []

	def __str__(self):
		return self.get_name()

	def __repr__(self):
		return self.__str__()

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_display_name(self):
		return self.display_name

	def set_display_name(self, display_name):
		self.display_name = display_name

	def get_insertion(self):
		return self.insertion

	def set_insertion(self, insertion):
		self.insertion = insertion

	def get_super_type_name(self):
		return self.super_type_name

	def set_super_type_name(self, name):
		self.super_type_name = name

	def get_constructor_infos(self):
		return self.constructor_infos

	def get_static_property_infos(self):
		return self.static_property_infos

	def get_static_method_infos(self):
		return self.static_method_infos

	def get_instance_property_infos(self):
		return self.instance_property_infos

	def get_instance_method_infos(self):
		return self.instance_method_infos

	def add_constructor_info(self, method_info):
		self.constructor_infos.append(method_info)

	def add_static_property_info(self, property_info):
		self.static_property_infos.append(property_info)

	def add_static_method_info(self, method_info):
		self.static_method_infos.append(method_info)

	def add_instance_property_info(self, property_info):
		self.instance_property_infos.append(property_info)

	def add_instance_method_info(self, method_info):
		self.instance_method_infos.append(method_info)
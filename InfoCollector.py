from infos import ArgumentInfo, MethodInfo, PropertyInfo, TypeInfo

# Type keys
TYPE_ENABLED_KEY = "enabled"
TYPE_NAME_KEY = "name"
TYPE_DISPLAY_NAME_KEY = "display_name"
TYPE_INSERTION_KEY = "insertion"
TYPE_SUPER_TYPE_NAME_KEY = "super_type_name"
TYPE_CONSTRUCTORS_KEY = "constructors"
TYPE_STATIC_PROPERTIES_KEY = "static_properties"
TYPE_STATIC_METHODS_KEY = "static_methods"
TYPE_INSTANCE_PROPERTIES_KEY = "instance_properties"
TYPE_INSTANCE_METHODS_KEY = "instance_methods"
# Property keys
PROPERTY_NAME_KEY = "name"
PROPERTY_DISPLAY_NAME_KEY = "display_name"
PROPERTY_TYPE_NAME_KEY = "type_name"
PROPERTY_INSERTION_KEY = "insertion"
# Method keys
METHOD_NAME_KEY = "name"
METHOD_DISPLAY_NAME_KEY = "display_name"
METHOD_INSERTION_KEY = "insertion"
METHOD_ARGS_KEY = "args"
METHOD_RETURN_TYPE_NAME_KEY = "return_type_name"
# Argument keys
ARGUMENT_NAME_KEY = "name"
ARGUMENT_DISPLAY_NAME_KEY = "display_name"
ARGUMENT_TYPE_NAME_KEY = "type_name"
ARGUMENT_INSERTION_KEY = "insertion"

class InfoCollector:

	@staticmethod
	def get_type_infos_from(type_dictionaries):
		
		type_infos = []
		for next_type_dict in type_dictionaries:
			next_type_info = InfoCollector.get_type_info_from(next_type_dict)
			if next_type_info:
				type_infos.append(next_type_info)
		return type_infos

	@staticmethod
	def get_type_info_from(type_dictionary):
		type_info = None
		try:
			# Enabled
			enabled = type_dictionary[TYPE_ENABLED_KEY]
			if enabled:
				# Name
				name = type_dictionary[TYPE_NAME_KEY]
				type_info = TypeInfo(name)

				try:
					# Display name
					display_name = type_dictionary[TYPE_DISPLAY_NAME_KEY]
					type_info.set_display_name(display_name)
				except KeyError, e:
					pass

				try:
					# Insertion
					insertion = type_dictionary[TYPE_INSERTION_KEY]
					type_info.set_insertion(insertion)
				except KeyError, e:
					pass

				try:
					# Super type name
					super_type_name = type_dictionary[TYPE_SUPER_TYPE_NAME_KEY]
					type_info.set_super_type_name(super_type_name)
				except KeyError, e:
					pass

				try:
					# Constructors
					constructor_dictionaries = type_dictionary[TYPE_CONSTRUCTORS_KEY]
					for next_constructor_dict in constructor_dictionaries:
						next_constructor_info = InfoCollector.get_method_info_from(next_constructor_dict)
						if next_constructor_info:
							type_info.add_constructor_info(next_constructor_info)
				except KeyError, e:
					pass
				
				try:
					# Static properties
					static_property_dictionaries = type_dictionary[TYPE_STATIC_PROPERTIES_KEY]
					for next_static_property_dict in static_property_dictionaries:
						next_static_property_info = InfoCollector.get_property_info_from(next_static_property_dict)
						if next_static_property_info:
							type_info.add_static_property_info(next_static_property_info)
				except KeyError, e:
					pass
				
				try:
					# Static methods
					static_method_dictionaries = type_dictionary[TYPE_STATIC_METHODS_KEY]
					for next_static_method_dict in static_method_dictionaries:
						next_static_method_info = InfoCollector.get_method_info_from(next_static_method_dict)
						if next_static_method_info:
							type_info.add_static_method_info(next_static_method_info)
				except KeyError, e:
					pass
				
				try:	
					# Instance properties
					instance_property_dictionaries = type_dictionary[TYPE_INSTANCE_PROPERTIES_KEY]
					for next_instance_property_dict in instance_property_dictionaries:
						next_instance_property_info = InfoCollector.get_property_info_from(next_instance_property_dict)
						if next_instance_property_info:
							type_info.add_instance_property_info(next_instance_property_info)
				except KeyError, e:
					pass
				
				try:	
					# Instance methods
					instance_method_dictionaries = type_dictionary[TYPE_INSTANCE_METHODS_KEY]
					for next_instance_method_dict in instance_method_dictionaries:
						next_instance_method_info = InfoCollector.get_method_info_from(next_instance_method_dict)
						if next_instance_method_info:
							type_info.add_instance_method_info(next_instance_method_info)
				except KeyError, e:
					pass

		except Exception, e:
			print "Exception getting type info: " + str(e)
			type_info = None

		return type_info

	@staticmethod
	def get_property_info_from(property_dictionary):
		property_info = None
		try:
			# Name
			name = property_dictionary[PROPERTY_NAME_KEY]
			property_info = PropertyInfo(name)
			
			try:
				# Display name
				display_name = property_dictionary[PROPERTY_DISPLAY_NAME_KEY]
				property_info.set_display_name(display_name)
			except KeyError, e:
				pass

			try:
				# Insertion
				insertion = property_dictionary[PROPERTY_INSERTION_KEY]
				property_info.set_insertion(insertion)
			except KeyError, e:
				pass

			try:
				# Type name
				type_name = property_dictionary[PROPERTY_TYPE_NAME_KEY]
				property_info.set_type_name(type_name)
			except KeyError, e:
				pass

		except KeyError, e:
			print "Key \"" + PROPERTY_NAME_KEY + "\" required for property.\n" + str(property_dictionary)
			property_info = None
			
		return property_info

	@staticmethod
	def get_method_info_from(method_dictionary):
		method_info = None
		try:
			# Name
			name = method_dictionary[METHOD_NAME_KEY]
			method_info = MethodInfo(name)
			
			try:
				# Display name
				display_name = method_dictionary[METHOD_DISPLAY_NAME_KEY]
				method_info.set_display_name(display_name)
			except KeyError, e:
				pass

			try:
				# Insertion
				insertion = method_dictionary[METHOD_INSERTION_KEY]
				type_info.set_insertion(insertion)
			except KeyError, e:
				pass

			try:
				# Argument infos
				arg_dictionaries = method_dictionary[METHOD_ARGS_KEY]
				for next_arg_dictionary in arg_dictionaries:
					next_arg_info = InfoCollector.get_argument_info_from(next_arg_dictionary)
					if next_arg_info:
						method_info.add_argument_info(next_arg_info)
			except KeyError, e:
				pass

			try:
				# Return type name
				return_type_name = method_dictionary[METHOD_RETURN_TYPE_NAME_KEY]
				method_info.set_return_type_name(return_type_name)
			except KeyError, e:
				pass

		except KeyError, e:
			print "Key \"" + METHOD_NAME_KEY + "\" required for method.\n" + str(method_dictionary)
			method_info = None

		return method_info

	@staticmethod
	def get_argument_info_from(argument_dictionary):
		argument_info = None
		try:
			# Name
			name = argument_dictionary[ARGUMENT_NAME_KEY]
			argument_info = ArgumentInfo(name)
			
			try:
				# Display name
				display_name = argument_dictionary[ARGUMENT_DISPLAY_NAME_KEY]
				argument_info.set_display_name(display_name)
			except KeyError, e:
				pass

			try:
				# Insertion
				insertion = argument_dictionary[ARGUMENT_INSERTION_KEY]
				argument_info.set_insertion(insertion)
			except KeyError, e:
				pass

			try:
				# Type
				type_name = argument_dictionary[ARGUMENT_TYPE_NAME_KEY]
				argument_info.set_type_name(type_name)
			except KeyError, e:
				pass

		except KeyError, e:
			print "Key \"" + ARGUMENT_NAME_KEY + "\" required for argument.\n" + str(argument_dictionary)
			argument_info = None

		return argument_info
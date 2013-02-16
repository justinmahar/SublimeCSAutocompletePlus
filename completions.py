

class Completions:

	OBJECT_TYPE_NAME = "Object"
	FUNCTION_TYPE_NAME = "Function"

	STATIC_PROPERTY_INDICATOR = u'\u25A1'
	STATIC_METHOD_INDICATOR = u'\u25A0'
	INSTANCE_PROPERTY_INDICATOR = u'\u25CB'
	INSTANCE_METHOD_INDICATOR = u'\u25CF'
	INHERITED_INDICATOR = u'\u251C'

	@staticmethod
	def get_completions_for(type_info, all_type_infos, is_static):

		completions = []

		static_flag = is_static
		properties_flag = True
		methods_flag = False

		# First, get immediate property completions.
		immediate_property_completions = Completions.get_property_completions(type_info, static_flag)
		# Next, get immediate method completions.
		immediate_method_completions = Completions.get_method_completions(type_info, static_flag)
		# Then, get inherited property completions.
		inherited_property_completions = Completions.get_inherited_completions(type_info, all_type_infos, static_flag, properties_flag)
		# Then, get inherited method completions.
		inherited_method_completions = Completions.get_inherited_completions(type_info, all_type_infos, static_flag, methods_flag)

		# Put them all together.
		completions.extend(immediate_property_completions)
		completions.extend(immediate_method_completions)
		completions.extend(inherited_property_completions)
		completions.extend(inherited_method_completions)
		
		return completions

	@staticmethod
	def get_property_completions(type_info, is_static, is_inherited=False):
		completions = []
		
		if is_static:
			property_indicator = Completions.STATIC_PROPERTY_INDICATOR
			property_infos = type_info.get_static_property_infos()
		else:
			property_indicator = Completions.INSTANCE_PROPERTY_INDICATOR
			property_infos = type_info.get_instance_property_infos()

		for next_property_info in property_infos:
			next_display_name = property_indicator + " " + next_property_info.get_display_name()
			if is_inherited:
				next_display_name = Completions.INHERITED_INDICATOR + next_display_name
			next_insertion = next_property_info.get_insertion()
			next_completion = (next_display_name, next_insertion)
			completions.append(next_completion)

		# Sort them alphabetically before returning them
		completions.sort()

		return completions

	@staticmethod
	def get_method_completions(type_info, is_static, is_inherited=False):
		completions = []
		
		if is_static:
			method_indicator = Completions.STATIC_METHOD_INDICATOR
			method_infos = type_info.get_static_method_infos()
		else:
			method_indicator = Completions.INSTANCE_METHOD_INDICATOR
			method_infos = type_info.get_instance_method_infos()

		for next_method_info in method_infos:
			next_display_text = method_indicator + " " + next_method_info.get_display_name()
			next_insertion_text = next_method_info.get_insertion()
			
			argument_infos = next_method_info.get_argument_infos()
			use_parens = True
			if next_method_info.get_argument_count() == 1:
				# If there's 1 argument and it's a Function, don't use parentheses.
				# This makes writing methods with callbacks easier.
				argument_info = argument_infos[0]
				if argument_info.get_type_name() == Completions.FUNCTION_TYPE_NAME:
					use_parens = False
			display_arg_string = ""
			insertion_arg_string = ""
			for index in range(len(argument_infos)):
				next_argument_info = argument_infos[index]
				display_arg_string = display_arg_string + next_argument_info.get_display_name()
				next_arg_insertion = next_argument_info.get_insertion()
				# Make insertion tabbable
				next_arg_insertion = "${" + str(index + 1) + ":" + next_arg_insertion + "}"
				insertion_arg_string = insertion_arg_string + next_arg_insertion
				if index < (len(argument_infos) - 1): # If there is another arg, add a comma.
					display_arg_string = display_arg_string + ", "
					insertion_arg_string = insertion_arg_string + ", "
			
			if use_parens:
				display_arg_string = "(" + display_arg_string + ")"
				insertion_arg_string = "(" + insertion_arg_string + ")"
			else:
				display_arg_string = " " + display_arg_string
				insertion_arg_string = " " + insertion_arg_string

			next_display_text = next_display_text + display_arg_string
			next_insertion_text = next_insertion_text + insertion_arg_string

			if is_inherited:
				next_display_text = Completions.INHERITED_INDICATOR + next_display_text

			next_completion = (next_display_text, next_insertion_text)
			completions.append(next_completion)

		# Sort them alphabetically before returning them
		completions.sort()

		return completions

	@staticmethod
	def get_inherited_completions(type_info, all_type_infos, is_static, is_properties):

		completions = []
		# Check to see if it's not an Object, and if it inherits anything else.
		if type_info.get_name() != Completions.OBJECT_TYPE_NAME:
			# Does it inherit anything else (besides Object)? If so, get the completions for that.
			super_type_name = type_info.get_super_type_name()
			super_is_object = super_type_name == Completions.OBJECT_TYPE_NAME
			super_type_info_found = False
			if super_type_name and not super_is_object:
				for next_type_info in all_type_infos:
					# Find the info for the super class...
					if next_type_info.get_name() == super_type_name: # RECURSIVE CASE
						super_type_info = next_type_info

						# First, get the super's completions...
						if is_properties:
							super_completions = Completions.get_property_completions(super_type_info, is_static, True) # Inherited
						else:
							super_completions = Completions.get_method_completions(super_type_info, is_static, True) # Inherited

						completions.extend(super_completions)
						# Now, recursively check if the super's super has completions.
						super_super_completions = Completions.get_inherited_completions(super_type_info, all_type_infos, is_static, is_properties)
						completions.extend(super_super_completions)
						super_type_info_found = True
						break
			# Otherwise, everything inherits instance members from Object, so get those completions.
			# If we didn't find the super type info, at least return Object's.
			if not super_type_info_found or super_is_object: # BASE CASE
				for next_type_info in all_type_infos:
					# Find the info for Object...
					if next_type_info.get_name() == Completions.OBJECT_TYPE_NAME:
						object_type_info = next_type_info
						if is_properties:
							object_completions = Completions.get_property_completions(object_type_info, False, True) # Inherited
						else:
							object_completions = Completions.get_method_completions(object_type_info, False, True) # Inherited
						completions.extend(object_completions)
						break
		elif is_static: # If accessing Object statically, it still inherits instance members of Object. Special case.
			object_type_info = type_info
			if is_properties:
				object_completions = Completions.get_property_completions(object_type_info, False, True) # Inherited
			else:
				object_completions = Completions.get_method_completions(object_type_info, False, True) # Inherited
			completions.extend(object_completions)


		# Sort them alphabetically before returning them
		completions.sort()

		return completions
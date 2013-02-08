import sublime
import re
import os

# TODO:
# - Document this file.
# - Split out functionality where possible.

# Set to true to enable debug output
DEBUG = False

SETTINGS_FILE_NAME = "CoffeeScript Autocomplete Plus.sublime-settings"
PREFERENCES_COFFEE_EXCLUDED_DIRS = "coffee_autocomplete_plus_excluded_dirs"
PREFERENCES_COFFEE_RESTRICTED_TO_PATHS = "coffee_autocomplete_plus_restricted_to_paths"
PREFERENCES_THIS_ALIASES = "coffee_autocomplete_plus_this_aliases"

COFFEESCRIPT_SYNTAX = "CoffeeScript"
COFFEE_EXTENSION_WITH_DOT = ".coffee"
CONSTRUCTOR_KEYWORD = "constructor"
THIS_SUGAR_SYMBOL = "@"
THIS_KEYWORD = "this"
PERIOD_OPERATOR = "."
COFFEE_FILENAME_REGEX = r".+?" + re.escape(COFFEE_EXTENSION_WITH_DOT)
CLASS_REGEX = r"class\s+%s((\s*$)|[^a-zA-Z0-9_$])"
CLASS_REGEX_ANY = r"class\s+([a-zA-Z0-9_$]+)((\s*$)|[^a-zA-Z0-9_$])"
CLASS_REGEX_WITH_EXTENDS = r"class\s+%s\s*($|(\s+extends\s+([a-zA-Z0-9_$.]+)))"
SINGLE_LINE_COMMENT_REGEX = r"#.*?$"
# Function regular expression. Matches:
# methodName  =   (aas,bsa, casd )	->
FUNCTION_REGEX = r"(^|[^a-zA-Z0-9_$])(%s)\s*[:]\s*(\((.*?)\))?\s*\->"
FUNCTION_REGEX_ANY = r"(^|[^a-zA-Z0-9_$])(([a-zA-Z0-9_$]+))\s*[:]\s*(\((.*?)\))?\s*\->"
# Assignment regular expression. Matches:
# asdadasd =
ASSIGNMENT_REGEX = r"(^|[^a-zA-Z0-9_$])%s\s*="
# Static assignment regex
STATIC_ASSIGNMENT_REGEX = r"^\s*([@]|(this\s*[.]))\s*([a-zA-Z0-9_$]+)\s*[:=]"
# Static function regex
STATIC_FUNCTION_REGEX = r"(^|[^a-zA-Z0-9_$])\s*([@]|(this\s*[.]))\s*([a-zA-Z0-9_$]+)\s*[:]\s*(\((.*?)\))?\s*\->"
# Regex for finding a function parameter. Requires the same item 4 times in a tuple.
PARAM_REGEX = r"\(\s*((%s)|(%s\s*[,].*?)|(.*?[,]\s*%s\s*[,].*?)|(.*?[,]\s*%s))\s*\)\s*\->"
# Regex for finding a variable declared in a for loop.
FOR_LOOP_REGEX = r"for\s*.*?[^a-zA-Z0-9_$]%s[^a-zA-Z0-9_$]"



# Assignment with the value it's being assigned to. Matches:
# blah = new Dinosaur()
ASSIGNMENT_VALUE_REGEX = r"(^|[^a-zA-Z0-9_$])%s\s*=\s*(.*)"

# Used to determining what class is being created with the new keyword. Matches:
# new Macaroni
NEW_OPERATION_REGEX = r"new\s+([a-zA-Z0-9_$]+)"

PROPERTY_INDICATOR = u'\u25CB'
METHOD_INDICATOR = u'\u25CF'

# Utility functions
def debug(message):
	if DEBUG:
		print message

def select_current_word(view):
	if len(view.sel()) > 0:
		selected_text = view.sel()[0]
		word_region = view.word(selected_text)
		view.sel().clear()
		view.sel().add(word_region)

def get_selected_word(view):
	word = ""
	if len(view.sel()) > 0:
		selected_text = view.sel()[0]
		word_region = view.word(selected_text)
		word = get_word_at(view, word_region)
	return word

def get_word_at(view, region):
	word = ""
	word_region = view.word(region)
	word = view.substr(word_region)
	word = re.sub('[\W]', '', word)
	word = word.strip()
	return word

def get_preceding_symbol(view):
	symbol = ""
	if len(view.sel()) > 0:
		selected_text = view.sel()[0]
		if selected_text.begin() > 0:
			symbol_region = sublime.Region(selected_text.begin() - 1, selected_text.begin())
			symbol = view.substr(symbol_region)
	return symbol

def get_preceding_word(view):
	word = ""
	if len(view.sel()) > 0:
		selected_text = view.sel()[0]
		if selected_text.begin() > 2:
			word_region = sublime.Region(selected_text.begin() - 1, selected_text.begin() - 1)
			word = get_word_at(view, word_region)
	return word

def is_capitalized(word): 
	capitalized = False
	# Underscores are sometimes used to indicate an internal property, so we
	# find the first occurrence of an a-zA-Z character. If not found, we assume lowercase.
	az_word = re.sub("[^a-zA-Z]", "", word)
	if len(az_word) > 0:
		first_letter = az_word[0]
		capitalized = first_letter.isupper()
	return capitalized

def get_files_in(directory_list, filename_regex, excluded_dirs):
	files = []
	for next_directory in directory_list:
		# http://docs.python.org/2/library/os.html?highlight=os.walk#os.walk
		for path, dirs, filenames in os.walk(next_directory):
			# print str(path)
			for next_excluded_dir in excluded_dirs:
				try:
					dirs.remove(next_excluded_dir)
				except:
					pass
			for next_file_name in filenames:
				# http://docs.python.org/2/library/re.html
				match = re.search(filename_regex, next_file_name)
				if match:
					# http://docs.python.org/2/library/os.path.html?highlight=os.path.join#os.path.join
					next_full_path = os.path.join(path, next_file_name)
					files.append(next_full_path)
	return files

def get_lines_for_file(file_path):
	lines = []
	try:
		# http://docs.python.org/2/tutorial/inputoutput.html
		opened_file = open(file_path, "r") # r = read only
		lines = opened_file.readlines()
	except:
		pass
	return lines

# Returns a tuple with (row, column, match, row_start_index), or None
def get_positions_of_regex_match_in_file(file_lines, regex):
	found_a_match = False
	matched_row = -1
	matched_column = -1
	match_found = None
	line_start_index = -1

	current_row = 0

	current_line_start_index = 0
	for next_line in file_lines:
		# Remove comments
		modified_next_line = re.sub(SINGLE_LINE_COMMENT_REGEX, "", next_line)
		match = re.search(regex, modified_next_line)
		if match:
			found_a_match = True
			matched_row = current_row
			matched_column = match.end()
			match_found = match
			line_start_index = current_line_start_index
			break
		current_row = current_row + 1
		current_line_start_index = current_line_start_index + len(next_line)

	positions_tuple = None
	if found_a_match:
		# Row and column are incremented because the Sublime open_file function's row and 
		# column start counting at 1, not 0.
		positions_tuple = ((matched_row + 1), (matched_column + 1), match_found, line_start_index)

	return positions_tuple

def open_file_at_position(window, file_path, row, column):
	# Beef
	# http://www.sublimetext.com/docs/2/api_reference.html#sublime.Window
	path_with_position_encoding = file_path + ":" + str(row) + ":" + str(column)
	window.open_file(path_with_position_encoding, sublime.ENCODED_POSITION)
	return

# Returns a tuple with (file_path, row, column, match, row_start_index)
def find_location_of_regex_in_files(contents_regex, local_file_lines, global_file_path_list=[]):
	# The match tuple containing the filename and positions.
	# Will be returned as None if no matches are found.
	file_match_tuple = None

	if local_file_lines:
		# Search the file for the regex.
		positions_tuple = get_positions_of_regex_match_in_file(local_file_lines, contents_regex)
		if positions_tuple:
			# We've found a match! Save the file path plus the positions and the match itself
			file_match_tuple = tuple([None]) + positions_tuple
	
	# If we are to search globally...
	if not file_match_tuple and global_file_path_list:
		for next_file_path in global_file_path_list:
			if next_file_path:
				file_lines = get_lines_for_file(next_file_path)
				# Search the file for the regex.
				positions_tuple = get_positions_of_regex_match_in_file(file_lines, contents_regex)
				if positions_tuple:
					# We've found a match! Save the file path plus the positions and the match itself
					file_match_tuple = tuple([next_file_path]) + positions_tuple
					# Stop the for loop
					break
	return file_match_tuple

def select_region_in_view(view, region):
	view.sel().clear()
	view.sel().add(region)
	# Refresh hack.
	original_position = view.viewport_position()
	view.set_viewport_position((original_position[0], original_position[1] + 1))
	view.set_viewport_position(original_position)

def get_progress_indicator_tuple(previous_indicator_tuple):
	STATUS_MESSAGE_PROGRESS_INDICATOR = "[%s=%s]"
	if not previous_indicator_tuple:
		previous_indicator_tuple = ("", 0, 1)
	PROGRESS_INDICATOR = "[%s=%s]"
	progress_indicator_position = previous_indicator_tuple[1]
	progress_indicator_direction = previous_indicator_tuple[2]
	# This animates a little activity indicator in the status area.
	# It animates an equals symbol bouncing back and fourth between square brackets.
	# We calculate the padding around the equal based on the last known position.
	num_spaces_before = progress_indicator_position % 8
	num_spaces_after = (7) - num_spaces_before  
	# When the equals hits the edge, we change directions.
	# Direction is -1 for moving left and 1 for moving right.
	if not num_spaces_after:  
		progress_indicator_direction = -1  
	if not num_spaces_before:  
		progress_indicator_direction = 1  
	progress_indicator_position += progress_indicator_direction
	padding_before = ' ' * num_spaces_before
	padding_after = ' ' * num_spaces_after
	# Create the progress indication text
	progress_indicator_text = STATUS_MESSAGE_PROGRESS_INDICATOR % (padding_before, padding_after)
	# Return the progress indication tuple
	return (progress_indicator_text, progress_indicator_position, progress_indicator_direction)

def get_syntax_name(view):
	syntax = os.path.splitext(os.path.basename(view.settings().get('syntax')))[0]
	return syntax

def is_coffee_syntax(view):
	return get_syntax_name(view) == COFFEESCRIPT_SYNTAX

def get_this_type(file_lines, start_region):

	type_found = None
	# Search backwards from current position for the type
	# We're looking for a class definition
	class_regex = CLASS_REGEX_ANY

	match_tuple = search_backwards_for(file_lines, class_regex, start_region)
	if match_tuple:
		# debug(str(match_tuple[0]) + ", " + str(match_tuple[1]) + ", " + match_tuple[2].group(1))
		type_found = match_tuple[2].group(1)
	else:
		debug("No match!")

	return type_found

def get_variable_type(file_lines, variable_name, start_region):

	type_found = None
	# Search backwards from current position for the type
	# We're looking for a variable assignent
	assignment_regex = ASSIGNMENT_VALUE_REGEX % variable_name

	match_tuple = search_backwards_for(file_lines, assignment_regex, start_region)
	if match_tuple:
		match = match_tuple[2]
		type_found = get_type_from_assignment_value(match_tuple[2].group(2))
	# If backwards searching isn't working, at least try to find something...
	else:
		# Forward search from beginning for assignment:
		match_tuple = get_positions_of_regex_match_in_file(file_lines, assignment_regex)
		if match_tuple:
			match = match_tuple[2]
			type_found = get_type_from_assignment_value(match.group(2))

	return type_found

def get_type_from_assignment_value(assignment_value_string):
	determined_type = None

	assignment_value_string = assignment_value_string.strip()

	new_operation_regex = NEW_OPERATION_REGEX
	match = re.search(new_operation_regex, assignment_value_string)
	if match:
		determined_type = match.group(1)
	else:
		# TODO: Handle internal types ("string", [Arrays], etc)
		pass

	return determined_type

# Tuple returned: (matched_row, matched_column, match, row_start_index)
def search_backwards_for(file_lines, regex, start_region):
	
	matched_row = -1
	matched_column = -1
	match_found = None
	row_start_index = -1

	start_index = start_region.begin()
	# debug("start: " + str(start_index))
	characters_consumed = 0
	start_line = -1
	indentation_size = 0
	current_line_index = 0	
	for next_line in file_lines:
		# Find the line we're starting on...
		offset = start_index - characters_consumed
		if offset <= len(next_line) + 1:
			# debug("Start line: " + next_line)
			characters_consumed = characters_consumed + len(next_line)
			indentation_size = get_indentation_size(next_line)
			start_line = current_line_index
			break

		characters_consumed = characters_consumed + len(next_line)
		current_line_index = current_line_index + 1

	row_start_index = characters_consumed

	if start_line >= 0:
		# debug("start line: " + str(start_line))
		# Go backwards, searching for the class definition. 
		for i in reversed(range(start_line+1)):
			previous_line = file_lines[i]
			row_start_index = row_start_index - len(previous_line)
			# debug("Line " + str(i) + ": " + re.sub("\n", "", previous_line))
			# Returns -1 for empty lines or lines with comments only.
			next_line_indentation = get_indentation_size(previous_line)
			#debug("Seeking <= indentation_size: " + str(indentation_size) + ", Current: " + str(next_line_indentation))
			# Ignore lines with larger indentation sizes and empty lines (or lines with comments only)
			if next_line_indentation >= 0 and next_line_indentation <= indentation_size:
				indentation_size = next_line_indentation
				# Check for the class
				match = re.search(regex, previous_line)
				if match:
					matched_row = i
					matched_column = match.end()
					match_found = match
					break
	match_tuple = None
	if match_found:
		match_tuple = (matched_row, matched_column, match_found, row_start_index)
	return match_tuple

def get_indentation_size(line_of_text):
	size = -1
	mod_line = re.sub("\n", "", line_of_text)
	mod_line = re.sub(SINGLE_LINE_COMMENT_REGEX, "", mod_line)
	# If it wasn't just a comment line...
	if len(mod_line.strip()) > 0:
		mod_line = re.sub(r"[^\t ].*", "", mod_line)
		size = len(mod_line)
	# debug("Indent size [" + str(size) + "]:\n" + re.sub("\n", "", line_of_text))
	return size

def get_completions_for_class(class_name, search_statically, local_file_lines, global_file_path_list=[]):
	
	completions = []
	scanned_classes = []	
	
	# TODO: Implement built in types...
	# TBD: First, determine if it is a built in type and return those completions...
	#      Maybe these are passed as an optional arg? That way you can define your own...

	current_class_name = class_name
	while current_class_name and current_class_name not in scanned_classes:
		# print "Scanning " + current_class_name + "..."
		completion_tuple = None
		if local_file_lines:
			# print "Searching locally..."
			# Search in local file.
			if search_statically:
				completion_tuple = collect_static_completions_from_file(local_file_lines, current_class_name)
			else:
				completion_tuple = collect_instance_completions_from_file(local_file_lines, current_class_name)

		# Search globally if nothing found and not local only...
		if global_file_path_list and (not completion_tuple or not completion_tuple[0]):
			class_regex = CLASS_REGEX % re.escape(current_class_name)
			global_class_location_search_tuple = find_location_of_regex_in_files(class_regex, None, global_file_path_list)
			if global_class_location_search_tuple:
				# If found, perform Class method collection.
				file_to_open = global_class_location_search_tuple[0]
				class_file_lines = get_lines_for_file(file_to_open)
				if search_statically:
					completion_tuple = collect_static_completions_from_file(class_file_lines, current_class_name)
				else:
					completion_tuple = collect_instance_completions_from_file(class_file_lines, current_class_name)
		# print "Tuple: " + str(completion_tuple)
		completions.extend(completion_tuple[1])
		scanned_classes.append(current_class_name)
		current_class_name = completion_tuple[2]

	# Remove all duplicates
	completions = list(set(completions))
	# Sort
	completions.sort()
	return completions

def collect_instance_completions_from_file(file_lines, class_name):

	completions = []
	extended_class = None
	class_found = False

	scanned_classes = []

	property_completions = []
	function_completions = []

	class_and_extends_regex = CLASS_REGEX_WITH_EXTENDS % class_name

	# Find class in file lines
	match_tuple = get_positions_of_regex_match_in_file(file_lines, class_and_extends_regex)
	if match_tuple:
		class_found = True
		row = match_tuple[0] - 1
		match = match_tuple[2]

		extended_class = match.group(3)
		if extended_class:
			# Clean it up.
			next_period_index = extended_class.find(PERIOD_OPERATOR)
			while next_period_index >= 0:
				extended_class = extended_class[(next_period_index + 1):]
				extended_class.strip()
				next_period_index = extended_class.find(PERIOD_OPERATOR)
			if len(extended_class) == 0:
				extended_class = None

		# If anything is equal to this after the first line, stop looking.
		# At that point, the class definition has ended.
		indentation_size = get_indentation_size(file_lines[row])
		# print str(indentation_size) + ": " + file_lines[row]
		# Let's dig for some info on this class!
		if row + 1 < len(file_lines):
			inside_constructor = False
			constructor_indentation = -1
			for row_index in range(row + 1, len(file_lines)):
				next_row = file_lines[row_index]
				next_indentation = get_indentation_size(next_row)
				# print str(next_indentation) + ": " + next_row
				if next_indentation >= 0:
					if next_indentation > indentation_size:
						if inside_constructor and next_indentation <= constructor_indentation:
							inside_constructor = False
						if inside_constructor:
							this_assignment_regex = "([@]|(this\s*[.]))\s*([a-zA-Z0-9_$]+)\s*="
							match = re.search(this_assignment_regex, next_row)
							if match:
								prop = match.group(3)
								prop_completion_alias = get_property_completion_alias(prop)
								prop_completion_insertion = get_property_completion_insertion(prop)
								prop_completion = (prop_completion_alias, prop_completion_insertion)
								if prop_completion not in property_completions:
									property_completions.append(prop_completion)
						else: # Not in constructor
							# Look for method definitions
							function_regex = FUNCTION_REGEX_ANY
							match = re.search(function_regex, next_row)
							if match and not re.search(STATIC_FUNCTION_REGEX, next_row):
								function_name = match.group(2)
								function_args_string = match.group(5)
								if function_name != CONSTRUCTOR_KEYWORD:
									function_args_list = []
									if function_args_string:
										function_args_list = function_args_string.split(",")
									for i in range(len(function_args_list)):
										# Fix each one up...
										next_arg = function_args_list[i]
										next_arg = next_arg.strip()
										next_arg = re.sub("[^a-zA-Z0-9_$].*", "", next_arg)
										function_args_list[i] = re.sub(THIS_SUGAR_SYMBOL, "", next_arg)
									function_alias = get_method_completion_alias(function_name, function_args_list)
									function_insertion = get_method_completion_insertion(function_name, function_args_list)
									function_completion = (function_alias, function_insertion)
									if function_completion not in function_completions:
										function_completions.append(function_completion)
								else:
									function_args_list = []
									if function_args_string:
										function_args_list = function_args_string.split(",")
									for i in range(len(function_args_list)):
										# Check if it starts with @ -- this indicates an auto-set class variable
										next_arg = function_args_list[i]
										next_arg = next_arg.strip()
										if next_arg.startswith(THIS_SUGAR_SYMBOL):
											# Clean it up...
											next_arg = re.sub(THIS_SUGAR_SYMBOL, "", next_arg)
											next_arg = re.sub("[^a-zA-Z0-9_$].*", "", next_arg)
											prop_completion_alias = get_property_completion_alias(next_arg)
											prop_completion_insertion = get_property_completion_insertion(next_arg)
											prop_completion = (prop_completion_alias, prop_completion_insertion)
											if prop_completion not in property_completions:
												property_completions.append(prop_completion)
									inside_constructor = True
									constructor_indentation = get_indentation_size(next_row)
					else:
						# Indentation limit hit. We're not in the class anymore.
						break

	completions = property_completions + function_completions
	completion_tuple = (class_found, completions, extended_class)
	return completion_tuple

def collect_static_completions_from_file(file_lines, class_name):
	
	completions = []
	extended_class = None
	class_found = False

	property_completions = []
	function_completions = []

	class_and_extends_regex = CLASS_REGEX_WITH_EXTENDS % class_name

	# Find class in file lines
	match_tuple = get_positions_of_regex_match_in_file(file_lines, class_and_extends_regex)
	if match_tuple:
		class_found = True
		row = match_tuple[0] - 1
		match = match_tuple[2]

		extended_class = match.group(3)
		if extended_class:
			# Clean it up.
			next_period_index = extended_class.find(PERIOD_OPERATOR)
			while next_period_index >= 0:
				extended_class = extended_class[(next_period_index + 1):]
				extended_class.strip()
				next_period_index = extended_class.find(PERIOD_OPERATOR)
			if len(extended_class) == 0:
				extended_class = None

		# If anything is equal to this after the first line, stop looking.
		# At that point, the class definition has ended.
		indentation_size = get_indentation_size(file_lines[row])
		
		# Let's dig for some info on this class!
		if row + 1 < len(file_lines):

			definition_indentation = -1
			previous_indentation = -1

			for row_index in range(row + 1, len(file_lines)):
				next_row = file_lines[row_index]
				next_indentation = get_indentation_size(next_row)
				# print str(next_indentation) + ": " + next_row
				if next_indentation >= 0:
					if next_indentation > indentation_size:
						# print "Next: " + str(next_indentation) + ", Prev: " + str(previous_indentation)
						# Haven't found anything yet...
						# Look for class-level definitions...
						# If current line indentation is greater than previous indentation, we're in a definition
						if next_indentation > previous_indentation and previous_indentation >= 0:
							inside_definition = True
						# Otherwise, save this indentation and examine the current line, as it's class-level
						else:
							previous_indentation = next_indentation
							function_regex = STATIC_FUNCTION_REGEX
							match = re.search(function_regex, next_row)
							if match:
								function_name = match.group(4)
								function_args_string = match.group(6)
								function_args_list = []
								if function_args_string:
									function_args_list = function_args_string.split(",")
								for i in range(len(function_args_list)):
									# Fix each one up...
									next_arg = function_args_list[i]
									next_arg = next_arg.strip()
									next_arg = re.sub("[^a-zA-Z0-9_$].*", "", next_arg)
									function_args_list[i] = next_arg
								function_alias = get_method_completion_alias(function_name, function_args_list)
								function_insertion = get_method_completion_insertion(function_name, function_args_list)
								function_completion = (function_alias, function_insertion)
								if function_completion not in function_completions:
									function_completions.append(function_completion)
							else:
								# Look for static assignment
								assignment_regex = STATIC_ASSIGNMENT_REGEX
								match = re.search(assignment_regex, next_row)
								if match:
									prop = match.group(3)
									prop_completion_alias = get_property_completion_alias(prop)
									prop_completion_insertion = get_property_completion_insertion(prop)
									prop_completion = (prop_completion_alias, prop_completion_insertion)
									if prop_completion not in property_completions:
										property_completions.append(prop_completion)
					else:
						# Indentation limit hit. We're not in the class anymore.
						break

	completions = property_completions + function_completions
	completion_tuple = (class_found, completions, extended_class)
	return completion_tuple

def get_property_completion_alias(property_name):
	completion_string = PROPERTY_INDICATOR + " " + property_name
	return completion_string

def get_property_completion_insertion(property_name):
	completion_string = property_name
	completion_string = re.sub("[$]", "\$", completion_string)
	return completion_string

def get_method_completion_alias(method_name, args):
	completion_string = METHOD_INDICATOR + " " + method_name + "("
	for i in range(len(args)):
		completion_string = completion_string + args[i]
		if i < len(args) - 1:
			completion_string = completion_string + ", "
	completion_string = completion_string + ")"
	return completion_string

def get_method_completion_insertion(method_name, args):
	completion_string = method_name + "("
	for i in range(len(args)):
		escaped_arg = re.sub("[$]", "\$", args[i])
		completion_string = completion_string + "${" + str(i + 1) + ":" + escaped_arg + "}"
		if i < len(args) - 1:
			completion_string = completion_string + ", "
	completion_string = completion_string + ")"
	return completion_string

def get_view_contents(view):
	contents = ""
	start = 0
	end = view.size() - 1
	if end > start:
		entire_doc_region = sublime.Region(start, end)
		contents = view.substr(entire_doc_region)
	return contents

def convert_file_contents_to_lines(contents):
	lines = contents.split("\n")
	count = len(lines)
	for i in range(count):
		# Don't add to the last one--that would put an extra \n
		if i < count - 1:
			lines[i] = lines[i] + "\n"
	return lines

def get_view_content_lines(view):
	return convert_file_contents_to_lines(get_view_contents(view))

def is_autocomplete_trigger(text):
	trigger = False
	trigger = trigger or text == THIS_SUGAR_SYMBOL
	trigger = trigger or text == PERIOD_OPERATOR
	return trigger
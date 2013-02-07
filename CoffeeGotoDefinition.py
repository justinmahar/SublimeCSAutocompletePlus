import sublime, sublime_plugin
import re
import os
import threading
import coffee_utils
from coffee_utils import debug

COMMAND_NAME = 'coffee_goto_definition'
STATUS_MESSAGE_DEFINITION_FOUND = "Coffee: Definition for \"%s\" found."
STATUS_MESSAGE_NO_DEFINITION_FOUND = "Coffee: No definition for \"%s\" found."
STATUS_MESSAGE_COFFEE_GOTO_DEFINITION = "Coffee: Goto Definition of \"%s\""

# SEARCH ORDER:
# Current file class (TitleCaps only)
# Current file function
# Current file assignment
# Global TitleCaps.coffee class
# Global search for class (TitleCaps only)
# Global search for function

# TODO:
# X Add config for "this" aliases (DONE)
# - Codo docs searching for function parameter types
# - Goto definition knows about function parameters
# - Smarter operand parsing. E.g. Given: this.test = "test", when goto "test", look for "this.test = ", not "test ="
# - Add "bad_coding_practices" config for checking for badly named classes and functions
#      For Readme: Do you suck at naming classes and variables? Don't worry, I've got you covered (but seriously, stop it).
# - Check contents of currently open views
# - Menu integration

class CoffeeGotoDefinitionCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		# Get the window
		self.window = sublime.active_window()
		# List of all project folders
		project_folder_list = self.window.folders()
		# The current view
		view = self.view
		# The current file name
		current_file_name = view.file_name()
		
		# Get currently selected word
		coffee_utils.select_current_word(view)
		selected_word = coffee_utils.get_selected_word(view)

		# Pull the excluded dirs from preferences
		excluded_dirs = view.settings().get(coffee_utils.PREFERENCES_COFFEE_EXCLUDED_DIRS)
		if not excluded_dirs:
			excluded_dirs = []

		# If there is a word selection and we're looking at a coffee file...
		if len(selected_word) > 0 and coffee_utils.is_coffee_syntax(view):

			thread = CoffeeGotoDefinitionThread(project_folder_list, current_file_name, selected_word, excluded_dirs)
			thread.start()
			self.check_operation(thread)

	def check_operation(self, thread, previous_progress_indicator_tuple=None):
		selected_word = thread.selected_word
		if not thread.is_alive():

			# Flatten any selection ranges
			if len(self.view.sel()) > 0:
				region = self.view.sel()[0]
				debug(region)
				end_point = region.end()
				region_to_select = sublime.Region(end_point, end_point)
				coffee_utils.select_region_in_view(self.view, region_to_select)

			matched_location_tuple = thread.matched_location_tuple
			if matched_location_tuple:
				# debug("Match found!")
				file_to_open = matched_location_tuple[0]
				row = matched_location_tuple[1]
				column = matched_location_tuple[2]
				match = matched_location_tuple[3]
				row_start_index = matched_location_tuple[4]
				# If there is a file to open...
				if file_to_open:
					# Open the file in the editor
					coffee_utils.open_file_at_position(self.window, file_to_open, row, column)
				# Otherwise, assume we found the match in the current view
				else:
					match_end = row_start_index + match.start() + len(match.group())
					region_to_select = sublime.Region(match_end, match_end)
					coffee_utils.select_region_in_view(self.view, region_to_select)
					self.view.show(region_to_select)

				self.window.active_view().set_status(COMMAND_NAME, STATUS_MESSAGE_DEFINITION_FOUND % selected_word)
			else:
				self.window.active_view().set_status(COMMAND_NAME, STATUS_MESSAGE_NO_DEFINITION_FOUND % selected_word)

		else:
			# Create the command's goto definition text, including the selected word. For the status bar.
			goto_definition_status_text = STATUS_MESSAGE_COFFEE_GOTO_DEFINITION % selected_word
			# Get a tuple containing the progress text, progress position, and progress direction.
			# This is used to animate a progress indicator in the status bar.
			current_progress_indicator_tuple = coffee_utils.get_progress_indicator_tuple(previous_progress_indicator_tuple)
			# Get the progress text
			progress_indicator_status_text = current_progress_indicator_tuple[0]
			# Set the status bar text so the user knows what's going on
			self.window.active_view().set_status(COMMAND_NAME, goto_definition_status_text + " " + progress_indicator_status_text)
			# Check again momentarily to see if the operation has completed.
			sublime.set_timeout(lambda: self.check_operation(thread, current_progress_indicator_tuple), 100)

class CoffeeGotoDefinitionThread(threading.Thread):
	
	def __init__(self, project_folder_list, current_file_name, selected_word, excluded_dirs):
		self.project_folder_list = project_folder_list
		self.current_file_name = current_file_name
		self.selected_word = selected_word
		self.excluded_dirs = excluded_dirs
		# None if no match was found, or a tuple containing the filename, row and column
		self.matched_location_tuple = None
		threading.Thread.__init__(self)

	def run(self):

		project_folder_list = self.project_folder_list
		current_file_name = self.current_file_name
		selected_word = self.selected_word
		excluded_dirs = self.excluded_dirs

		# This will be assigned whem a match is made
		matched_location_tuple = None


		# The regular expression used to search for the selected class
		class_regex = coffee_utils.CLASS_REGEX % re.escape(selected_word)
		# The regex used to search for the selected function
		function_regex = coffee_utils.FUNCTION_REGEX % re.escape(selected_word)
		# The regex used to search for the selected variable assignment
		assignment_regex = coffee_utils.ASSIGNMENT_REGEX % re.escape(selected_word)

		# Lines for currently viewed file
		current_file_lines = coffee_utils.get_lines_for_file(current_file_name)

		debug(("Selected: \"%s\"" % selected_word))

		# ------ IS A CLASS ------------------------------------------
		# Check if the selected text starts with a capital letter
		if coffee_utils.is_capitalized(selected_word):

			# ------ CURRENT FILE: CLASS (TitleCaps ONLY) ------------

			if not matched_location_tuple:

					# If so, we assume it is a class. 
					debug("Checking for local class %s..." % selected_word)
					class_location_search_tuple = coffee_utils.find_location_of_regex_in_files(class_regex, current_file_lines)
					if class_location_search_tuple:
						matched_location_tuple = class_location_search_tuple

			# ------ GLOBAL SEARCH: CLASS ----------------------------

			if not matched_location_tuple:

				# Coffeescript filename regex
				coffeescript_filename_regex = coffee_utils.COFFEE_FILENAME_REGEX
				# All coffeescript file paths
				all_coffee_file_paths = coffee_utils.get_files_in(project_folder_list, coffeescript_filename_regex, excluded_dirs)

				debug("Checking globally for class %s..." % selected_word)
				# Assume it is a file called selected_word.coffee
				exact_file_name_regex = "^" + re.escape(selected_word + coffee_utils.COFFEE_EXTENSION_WITH_DOT) + "$"
				exact_name_file_paths = coffee_utils.get_files_in(project_folder_list, exact_file_name_regex, excluded_dirs)
				exact_location_search_tuple = coffee_utils.find_location_of_regex_in_files(class_regex, None, exact_name_file_paths)
				if exact_location_search_tuple:
					matched_location_tuple = exact_location_search_tuple
				else:
					global_class_location_search_tuple = coffee_utils.find_location_of_regex_in_files(class_regex, None, all_coffee_file_paths)
					if global_class_location_search_tuple:
						matched_location_tuple = global_class_location_search_tuple

		# ------ NOT A CLASS -----------------------------------------
		else:
			# ------ CURRENT FILE: FUNCTION --------------------------
			if not matched_location_tuple:
				debug("Checking for local function %s..." % selected_word)
				local_function_location_search_tuple = coffee_utils.find_location_of_regex_in_files(function_regex, current_file_lines)
				if local_function_location_search_tuple:
					matched_location_tuple = local_function_location_search_tuple

			# ------ CURRENT FILE: ASSIGNMENT ------------------------

			if not matched_location_tuple:
				# TODO: While this indeed works, it's not good enough to find the first occurrence. 
				#	   Instead, check from the current position backwards. 
				#	   Take scope into consideration using indentation.
				debug("Checking for local assignment of %s..." % selected_word)
				local_assignment_location_search_tuple = coffee_utils.find_location_of_regex_in_files(assignment_regex, current_file_lines)
				if local_assignment_location_search_tuple:
					matched_location_tuple = local_assignment_location_search_tuple		

			# ------ GLOBAL SEARCH: FUNCTION -------------------------

			if not matched_location_tuple:

				# Coffeescript filename regex
				coffeescript_filename_regex = coffee_utils.COFFEE_FILENAME_REGEX
				# All coffeescript file paths
				all_coffee_file_paths = coffee_utils.get_files_in(project_folder_list, coffeescript_filename_regex, excluded_dirs)

				debug("Checking globally for function %s..." % selected_word)
				global_function_location_search_tuple = coffee_utils.find_location_of_regex_in_files(function_regex, None, all_coffee_file_paths)
				if global_function_location_search_tuple:
					matched_location_tuple = global_function_location_search_tuple

		# ------ DOT OPERATION LOOKUP (TBD) ----------------------
		# TODO: Pull out dot operator object, determine its assignment type, find class, goto method/property.
		#	    Also, determine where to put this lookup.

		# ------ SUPER METHOD LOOKUP (TBD) -----------------------
		# TODO: If selected_word is "super", assume a function and then attempt to find 
		#       extending class and open it to the function the cursor is within.

		# ------ STORE MATCH RESULTS -----------------------------
		# If not None, then we found a file that matched the search!
		if matched_location_tuple:
			self.matched_location_tuple = matched_location_tuple
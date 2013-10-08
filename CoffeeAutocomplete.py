import sublime, sublime_plugin
import re
import os
import threading
from copy import copy

try:
	# Python 3
	from . import coffee_utils
	from .coffee_utils import debug
except (ValueError):
	# Python 2
	import coffee_utils
	from coffee_utils import debug

COFFEESCRIPT_AUTOCOMPLETE_STATUS_KEY = "coffee_autocomplete"
COFFEESCRIPT_AUTOCOMPLETE_STATUS_MESSAGE = "Coffee: Autocompleting \"%s\"..."

final_completions = []
status = {"working": False}

# TODO:
# - Type hinting using comments containing square brackets [Type] on same line or previous line
# - Codo docs searching for function parameter types
# - Better symbol parsing. Assignment lookups should consider the entire set of operands.
# X Consider all super classes (support extends)
# - Consider another feature: Override/implement methods
# - Full assignment traceback (that = this, a = b = c, knows what c is)
# - Check contents of currently open views
# - Built in types

class CoffeeAutocomplete(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):

		completions = copy(final_completions)
		working = status["working"]

		# If there is a word selection and we're looking at a coffee file...
		if not completions and coffee_utils.is_coffee_syntax(view) and not working:
			if not view.match_selector(locations[0], "source.coffee -comment"):
				return []

			status["working"] = True

			current_location = locations[0]

			# Get the window
			self.window = sublime.active_window()

			# http://www.sublimetext.com/forum/viewtopic.php?f=6&t=9076
			settings = sublime.load_settings(coffee_utils.SETTINGS_FILE_NAME)

			built_in_types_settings = sublime.load_settings(coffee_utils.BUILT_IN_TYPES_SETTINGS_FILE_NAME)
			built_in_types = built_in_types_settings.get(coffee_utils.BUILT_IN_TYPES_SETTINGS_KEY)
			if not built_in_types:
				built_in_types = []

			custom_types_settings = sublime.load_settings(coffee_utils.CUSTOM_TYPES_SETTINGS_FILE_NAME)
			custom_types = custom_types_settings.get(coffee_utils.CUSTOM_TYPES_SETTINGS_KEY)
			if not custom_types:
				custom_types = []

			built_in_types.extend(custom_types)

			# Pull the excluded dirs from preferences
			excluded_dirs = settings.get(coffee_utils.PREFERENCES_COFFEE_EXCLUDED_DIRS)
			if not excluded_dirs:
				excluded_dirs = []

			restricted_to_dirs = settings.get(coffee_utils.PREFERENCES_COFFEE_RESTRICTED_TO_PATHS)
			if not restricted_to_dirs:
				restricted_to_dirs = []

			# List of all project folders
			project_folder_list = self.window.folders()

			if restricted_to_dirs:
				specific_project_folders = []
				for next_restricted_dir in restricted_to_dirs:
					for next_project_folder in project_folder_list:
						next_specific_folder = os.path.normpath(os.path.join(next_project_folder, next_restricted_dir))
						specific_project_folders.append(next_specific_folder)
				project_folder_list = specific_project_folders

			function_return_types = settings.get(coffee_utils.FUNCTION_RETURN_TYPES_SETTINGS_KEY)
			if not function_return_types:
				function_return_types = []

			this_aliases = settings.get(coffee_utils.PREFERENCES_THIS_ALIASES)
			if not this_aliases:
				this_aliases = []

			member_exclusion_regexes = settings.get(coffee_utils.PREFERENCES_MEMBER_EXCLUSION_REGEXES)
			if not member_exclusion_regexes:
				member_exclusion_regexes = []

			# Lines for the current file in view
			current_file_lines = coffee_utils.get_view_content_lines(view)

			# TODO: Smarter previous word selection
			preceding_symbol = coffee_utils.get_preceding_symbol(view, prefix, locations)
			immediately_preceding_symbol = coffee_utils.get_preceding_symbol(view, "", locations)

			preceding_function_call = coffee_utils.get_preceding_function_call(view).strip()

			# Determine preceding token, if any (if a period was typed).
			token = coffee_utils.get_preceding_token(view).strip()

			# TODO: Smarter region location
			symbol_region = sublime.Region(locations[0] - len(prefix), locations[0] - len(prefix))

			if (preceding_function_call or token or coffee_utils.THIS_SUGAR_SYMBOL == preceding_symbol) and coffee_utils.is_autocomplete_trigger(immediately_preceding_symbol):
				self.window.active_view().run_command('hide_auto_complete')

				thread = CoffeeAutocompleteThread(project_folder_list, excluded_dirs, this_aliases, current_file_lines, preceding_symbol, prefix, preceding_function_call, function_return_types, token, symbol_region, built_in_types, member_exclusion_regexes)
				thread.start()
				self.check_operation(thread, final_completions, current_location, token, status)
			else: 
				status["working"] = False

		elif completions:
			self.clear_completions(final_completions)

		return completions

	def check_operation(self, thread, final_completions, current_location, token, status, previous_progress_indicator_tuple=None):

		if not thread.is_alive():
			if thread.completions:
				final_completions.extend(thread.completions)
				# Hide the default auto-complete and show ours
				self.window.active_view().run_command('hide_auto_complete')
				sublime.set_timeout(lambda: self.window.active_view().run_command('auto_complete'), 1)

			self.window.active_view().erase_status(COFFEESCRIPT_AUTOCOMPLETE_STATUS_KEY)
			status["working"] = False
		else:
			token = thread.token
			# Create the command's goto definition text, including the selected word. For the status bar.
			status_text = COFFEESCRIPT_AUTOCOMPLETE_STATUS_MESSAGE % token
			# Get a tuple containing the progress text, progress position, and progress direction.
			# This is used to animate a progress indicator in the status bar.
			current_progress_indicator_tuple = coffee_utils.get_progress_indicator_tuple(previous_progress_indicator_tuple)
			# Get the progress text
			progress_indicator_status_text = current_progress_indicator_tuple[0]
			# Set the status bar text so the user knows what's going on
			self.window.active_view().set_status(COFFEESCRIPT_AUTOCOMPLETE_STATUS_KEY, status_text + " " + progress_indicator_status_text)
			# Check again momentarily to see if the operation has completed.
			sublime.set_timeout(lambda: self.check_operation(thread, final_completions, current_location, token, status, current_progress_indicator_tuple), 100)

	def clear_completions(self, final_completions):
		debug("Clearing completions...")
		while len(final_completions) > 0:
			final_completions.pop()

class CoffeeAutocompleteThread(threading.Thread):

	def __init__(self, project_folder_list, excluded_dirs, this_aliases, current_file_lines, preceding_symbol, prefix, preceding_function_call, function_return_types, token, symbol_region, built_in_types, member_exclusion_regexes):
		
		self.project_folder_list = project_folder_list
		self.excluded_dirs = excluded_dirs
		self.this_aliases = this_aliases
		self.current_file_lines = current_file_lines
		self.preceding_symbol = preceding_symbol
		self.prefix = prefix
		self.preceding_function_call = preceding_function_call
		self.function_return_types = function_return_types
		self.token = token
		self.symbol_region = symbol_region
		self.built_in_types = built_in_types
		self.member_exclusion_regexes = member_exclusion_regexes

		# None if no completions found, or an array of the completion tuples
		self.completions = None
		threading.Thread.__init__(self)

	def run(self):

		project_folder_list = self.project_folder_list
		excluded_dirs = self.excluded_dirs
		this_aliases = self.this_aliases
		current_file_lines = self.current_file_lines
		preceding_symbol = self.preceding_symbol
		prefix = self.prefix
		preceding_function_call = self.preceding_function_call
		function_return_types = self.function_return_types
		token = self.token
		symbol_region = self.symbol_region
		built_in_types = self.built_in_types
		member_exclusion_regexes = self.member_exclusion_regexes

		selected_word = token[token.rfind(".") + 1:]

		completions = []

		# First see if it is a special function return definition, like $ for $("#selector")
		if preceding_function_call:
			for next_return_type in function_return_types:
				function_names = next_return_type[coffee_utils.FUNCTION_RETURN_TYPE_FUNCTION_NAMES_KEY]
				if preceding_function_call in function_names:
					return_type = next_return_type[coffee_utils.FUNCTION_RETURN_TYPE_TYPE_NAME_KEY]
					completions = coffee_utils.get_completions_for_class(return_type, False, None, prefix, None, built_in_types, member_exclusion_regexes, False)

		if not completions:
			# Prepare to search globally if we need to...
			# Coffeescript filename regex
			coffeescript_filename_regex = coffee_utils.COFFEE_FILENAME_REGEX
			# All coffeescript file paths
			all_coffee_file_paths = coffee_utils.get_files_in(project_folder_list, coffeescript_filename_regex, excluded_dirs)

			# If @ typed, process as "this."
			if preceding_symbol == coffee_utils.THIS_SUGAR_SYMBOL:
				# Process as "this."
				this_type = coffee_utils.get_this_type(current_file_lines, symbol_region)
				if this_type:
					completions = coffee_utils.get_completions_for_class(this_type, False, current_file_lines, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, True)
				pass
			elif preceding_symbol == coffee_utils.PERIOD_OPERATOR:
				# If "this" or a substitute for it, process as "this."
				if selected_word == coffee_utils.THIS_KEYWORD or selected_word in this_aliases:
					# Process as "this."
					this_type = coffee_utils.get_this_type(current_file_lines, symbol_region)
					if this_type:
						completions = coffee_utils.get_completions_for_class(this_type, False, current_file_lines, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, True)
				else:
					# If TitleCase, assume a class, and that we want static properties and functions.
					if coffee_utils.is_capitalized(selected_word):
						# Assume it is either in the current view or in a coffee file somewhere
						completions = coffee_utils.get_completions_for_class(selected_word, True, current_file_lines, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, False)
						if not completions:
							# Now we search globally...
							completions = coffee_utils.get_completions_for_class(selected_word, True, None, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, False)

					# If nothing yet, assume a variable.
					if not completions:
						variable_type = coffee_utils.get_variable_type(current_file_lines, token, symbol_region, all_coffee_file_paths, built_in_types, [])
						if variable_type:
							# Assume it is either in the current view or in a coffee file somewhere
							completions = coffee_utils.get_completions_for_class(variable_type, False, current_file_lines, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, False)
					if not completions:
						# Now we search globally for a class... Maybe they're making a static call on something lowercase? Bad design, but check anyways.
						completions = coffee_utils.get_completions_for_class(selected_word, True, None, prefix, all_coffee_file_paths, built_in_types, member_exclusion_regexes, False)
		if completions:
			self.completions = completions
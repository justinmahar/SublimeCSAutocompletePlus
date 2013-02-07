import sublime, sublime_plugin
import re
import os
import threading
import coffee_utils
from coffee_utils import debug
from copy import copy

COFFEESCRIPT_AUTOCOMPLETE_STATUS_KEY = "coffee_autocomplete"
COFFEESCRIPT_AUTOCOMPLETE_STATUS_MESSAGE = "Coffee: Autocompleting \"%s\"..."

final_completions = []
status = {"working": False}

# TODO:
# - Type hinting using comments containing square brackets [Type] on same line or previous line
# - Codo docs searching for function parameter types
# - Better symbol parsing. Assignment lookups should consider the entire set of operands.
# - Consider all super classes (support extends)
# - Consider another feature: Override/implement methods
# - Full assignment traceback (that = this, a = b = c, knows what c is)
# - Check contents of currently open views

class CoffeeAutocomplete(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):

		completions = copy(final_completions)
		working = status["working"]

		# If there is a word selection and we're looking at a coffee file...
		if not completions and coffee_utils.is_coffee_syntax(view) and not working:

			status["working"] = True

			current_location = locations[0]

			# Get the window
			self.window = sublime.active_window()

			# List of all project folders
			project_folder_list = self.window.folders()

			# Pull the excluded dirs from preferences
			excluded_dirs = view.settings().get(coffee_utils.PREFERENCES_COFFEE_EXCLUDED_DIRS)
			if not excluded_dirs:
				excluded_dirs = []

			this_aliases = view.settings().get(coffee_utils.PREFERENCES_THIS_ALIASES)
			if not this_aliases:
				this_aliases = []

			# Lines for the current file in view
			current_file_lines = coffee_utils.get_view_content_lines(view)

			# TODO: Smarter previous word selection
			preceding_symbol = coffee_utils.get_preceding_symbol(view)

			# Determine preceding token, if any (if a period was typed).
			token = coffee_utils.get_preceding_word(view)

			# TODO: Smarter region location
			symbol_region = view.sel()[0]

			if coffee_utils.is_autocomplete_trigger(preceding_symbol):

				self.window.active_view().run_command('hide_auto_complete')

				thread = CoffeeAutocompleteThread(project_folder_list, excluded_dirs, this_aliases, current_file_lines, preceding_symbol, token, symbol_region)
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

	def __init__(self, project_folder_list, excluded_dirs, this_aliases, current_file_lines, preceding_symbol, token, symbol_region):
		
		self.project_folder_list = project_folder_list
		self.excluded_dirs = excluded_dirs
		self.this_aliases = this_aliases
		self.current_file_lines = current_file_lines
		self.preceding_symbol = preceding_symbol
		self.token = token
		self.symbol_region = symbol_region

		# None if no completions found, or an array of the completion tuples
		self.completions = None
		threading.Thread.__init__(self)

	def run(self):

		project_folder_list = self.project_folder_list
		excluded_dirs = self.excluded_dirs
		this_aliases = self.this_aliases
		current_file_lines = self.current_file_lines
		preceding_symbol = self.preceding_symbol
		token = self.token
		symbol_region = self.symbol_region

		completions = []

		# If @ typed, process as "this."
		if preceding_symbol == coffee_utils.THIS_SUGAR_SYMBOL:
			# Process as "this."
			this_type = coffee_utils.get_this_type(current_file_lines, symbol_region)
			if this_type:
				completions = coffee_utils.get_completions_for_class(this_type, False, current_file_lines)
			pass
		elif preceding_symbol == coffee_utils.PERIOD_OPERATOR:
			# If "this" or a substitute for it, process as "this."
			if token == coffee_utils.THIS_KEYWORD or token in this_aliases:
				# Process as "this."
				this_type = coffee_utils.get_this_type(current_file_lines, symbol_region)
				if this_type:
					completions = coffee_utils.get_completions_for_class(this_type, False, current_file_lines)
			else:
				
				# Prepare to search globally if we need to...
				# Coffeescript filename regex
				coffeescript_filename_regex = coffee_utils.COFFEE_FILENAME_REGEX
				# All coffeescript file paths
				all_coffee_file_paths = coffee_utils.get_files_in(project_folder_list, coffeescript_filename_regex, excluded_dirs)

				# If TitleCase, assume a class, and that we want static properties and functions.
				if coffee_utils.is_capitalized(token):
					# Assume it is either in the current view or in a file called token.coffee
					exact_file_name_regex = "^" + re.escape(token + coffee_utils.COFFEE_EXTENSION_WITH_DOT) + "$"
					exact_name_file_paths = coffee_utils.get_files_in(project_folder_list, exact_file_name_regex, excluded_dirs)
					completions = coffee_utils.get_completions_for_class(token, True, current_file_lines, exact_name_file_paths)
					if not completions:
						# Now we search globally...
						completions = coffee_utils.get_completions_for_class(token, True, None, all_coffee_file_paths)

				# If nothing yet, assume a variable.
				if not completions:
					variable_type = coffee_utils.get_variable_type(current_file_lines, token, symbol_region)
					if variable_type:
						# Assume it is either in the current view or in a file called variable_type.coffee
						exact_file_name_regex = "^" + re.escape(variable_type + coffee_utils.COFFEE_EXTENSION_WITH_DOT) + "$"
						exact_name_file_paths = coffee_utils.get_files_in(project_folder_list, exact_file_name_regex, excluded_dirs)
						completions = coffee_utils.get_completions_for_class(variable_type, False, current_file_lines, exact_name_file_paths)
						if not completions:
							# Now we search globally...
							completions = coffee_utils.get_completions_for_class(variable_type, False, None, all_coffee_file_paths)
		if completions:
			self.completions = completions
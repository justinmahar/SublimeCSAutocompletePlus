import sublime
import re
import os

# TODO:
# - Document this file.
# - Split out functionality where possible.

# This file is what happens when you code non-stop for several days.
# I tried to make the main files as easy to follow along as possible.
# This file, not so much.

# Set to true to enable debug output
DEBUG = False

SETTINGS_FILE_NAME = "CoffeeComplete Plus.sublime-settings"
PREFERENCES_COFFEE_EXCLUDED_DIRS = "coffee_autocomplete_plus_excluded_dirs"
PREFERENCES_COFFEE_RESTRICTED_TO_PATHS = "coffee_autocomplete_plus_restricted_to_paths"
PREFERENCES_THIS_ALIASES = "coffee_autocomplete_plus_this_aliases"
PREFERENCES_MEMBER_EXCLUSION_REGEXES = "coffee_autocomplete_plus_member_exclusion_regexes"
BUILT_IN_TYPES_SETTINGS_FILE_NAME = "CoffeeComplete Plus Built-In Types.sublime-settings"
BUILT_IN_TYPES_SETTINGS_KEY = "coffee_autocomplete_plus_built_in_types"
CUSTOM_TYPES_SETTINGS_FILE_NAME = "CoffeeComplete Plus Custom Types.sublime-settings"
CUSTOM_TYPES_SETTINGS_KEY = "coffee_autocomplete_plus_custom_types"
FUNCTION_RETURN_TYPES_SETTINGS_KEY = "coffee_autocomplete_plus_function_return_types"
FUNCTION_RETURN_TYPE_TYPE_NAME_KEY = "type_name"
FUNCTION_RETURN_TYPE_FUNCTION_NAMES_KEY = "function_names"

COFFEESCRIPT_SYNTAX = r"CoffeeScript"
COFFEE_EXTENSION_WITH_DOT = "\.coffee|\.litcoffee|\.coffee\.md"
CONSTRUCTOR_KEYWORDS = ["constructor", "initialize", "init"]
THIS_SUGAR_SYMBOL = "@"
THIS_KEYWORD = "this"
PERIOD_OPERATOR = "."
COFFEE_FILENAME_REGEX = r".+?" + re.escape(COFFEE_EXTENSION_WITH_DOT)
CLASS_REGEX = r"class\s+%s((\s*$)|[^a-zA-Z0-9_$])"
CLASS_REGEX_ANY = r"class\s+([a-zA-Z0-9_$]+)((\s*$)|[^a-zA-Z0-9_$])"
CLASS_REGEX_WITH_EXTENDS = r"class\s+%s\s*($|(\s+extends\s+([a-zA-Z0-9_$.]+)))"
SINGLE_LINE_COMMENT_REGEX = r"#.*?$"
TYPE_HINT_COMMENT_REGEX = r"#.*?\[([a-zA-Z0-9_$]+)\].*$"
TYPE_HINT_PARAMETER_COMMENT_REGEX = r"#.*?(\[([a-zA-Z0-9_$]+)\]\s*{var_name}((\s*$)|[^a-zA-Z0-9_$]))|({var_name}\s*\[([a-zA-Z0-9_$]+)\]((\s*$)|[^a-zA-Z0-9_$]))"
# Function regular expression. Matches:
# methodName  =   (aas,bsa, casd )    ->
FUNCTION_REGEX = r"(^|[^a-zA-Z0-9_$])(%s)\s*[:]\s*(\((.*?)\))?\s*[=\-]>"
FUNCTION_REGEX_ANY = r"(^|[^a-zA-Z0-9_$])(([a-zA-Z0-9_$]+))\s*[:]\s*(\((.*?)\))?\s*[=\-]>"
# Assignment regular expression. Matches:
# asdadasd =
ASSIGNMENT_REGEX = r"(^|[^a-zA-Z0-9_$])%s\s*="
# Static assignment regex
STATIC_ASSIGNMENT_REGEX = r"^\s*([@]|(this\s*[.]))\s*([a-zA-Z0-9_$]+)\s*[:=]"
# Static function regex
STATIC_FUNCTION_REGEX = r"(^|[^a-zA-Z0-9_$])\s*([@]|(this\s*[.]))\s*([a-zA-Z0-9_$]+)\s*[:]\s*(\((.*?)\))?\s*[=\-]>"
# Regex for finding a function parameter. Call format on the string, with name=var_name
PARAM_REGEX = r"\(\s*(({name})|({name}\s*=?.*?[,].*?)|(.*?[,]\s*{name}\s*=?.*?[,].*?)|(.*?[,]\s*{name}))\s*=?.*?\)\s*[=\-]>"
# Regex for finding a variable declared in a for loop.
FOR_LOOP_REGEX = r"for\s*.*?[^a-zA-Z0-9_$]%s[^a-zA-Z0-9_$]"
# Regex for constructor @ params, used for type hinting.
CONSTRUCTOR_SELF_ASSIGNMENT_PARAM_REGEX = r"(?:(?:constructor)|(?:initialize)|(?:init))\s*[:]\s*\(\s*((@{name})|(@{name}\s*[,].*?)|(.*?[,]\s*@{name}\s*[,].*?)|(.*?[,]\s*@{name}))\s*\)\s*[=\-]>\s*$"

# Assignment with the value it's being assigned to. Matches:
# blah = new Dinosaur()
ASSIGNMENT_VALUE_WITH_DOT_REGEX = r"(^|[^a-zA-Z0-9_$])%s\s*=\s*(.*)"
ASSIGNMENT_VALUE_WITHOUT_DOT_REGEX = r"(^|[^a-zA-Z0-9_$.])%s\s*=\s*(.*)"

# Used to determining what class is being created with the new keyword. Matches:
# new Macaroni
NEW_OPERATION_REGEX = r"new\s+([a-zA-Z0-9_$.]+)"

PROPERTY_INDICATOR = u'\u25CB'
METHOD_INDICATOR = u'\u25CF'
INHERITED_INDICATOR = u'\u2C75'

BUILT_IN_TYPES_TYPE_NAME_KEY = "name"
BUILT_IN_TYPES_TYPE_ENABLED_KEY = "enabled"
BUILT_IN_TYPES_CONSTRUCTOR_KEY = "constructor"
BUILT_IN_TYPES_STATIC_PROPERTIES_KEY = "static_properties"
BUILT_IN_TYPES_STATIC_PROPERTY_NAME_KEY = "name"
BUILT_IN_TYPES_STATIC_METHODS_KEY = "static_methods"
BUILT_IN_TYPES_STATIC_METHOD_NAME_KEY = "name"
BUILT_IN_TYPES_INSTANCE_PROPERTIES_KEY = "instance_properties"
BUILT_IN_TYPES_INSTANCE_PROPERTY_NAME_KEY = "name"
BUILT_IN_TYPES_INSTANCE_METHODS_KEY = "instance_methods"
BUILT_IN_TYPES_INSTANCE_METHOD_NAME_KEY = "name"
BUILT_IN_TYPES_METHOD_NAME_KEY = "name"
BUILT_IN_TYPES_METHOD_INSERTION_KEY = "insertion"
BUILT_IN_TYPES_METHOD_ARGS_KEY = "args"
BUILT_IN_TYPES_METHOD_ARG_NAME_KEY = "name"
BUILT_IN_TYPES_INHERITS_FROM_OBJECT_KEY = "inherits_from_object"


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
    word = re.sub(r'[^a-zA-Z0-9_$]', '', word)
    word = word.strip()
    return word


def get_token_at(view, region):
    token = ""
    if len(view.sel()) > 0:
        selected_line = view.line(region)
        preceding_text = view.substr(sublime.Region(selected_line.begin(), region.begin())).strip()
        token_regex = r"[^a-zA-Z0-9_$.@]*?([a-zA-Z0-9_$.@]+)$"
        match = re.search(token_regex, preceding_text)
        if match:
            token = match.group(1)
    token = token.strip()
    return token


def get_preceding_symbol(view, prefix, locations):
    index = locations[0]
    symbol_region = sublime.Region(index - 1 - len(prefix), index - len(prefix))
    symbol = view.substr(symbol_region)
    return symbol


def get_preceding_function_call(view):
    function_call = ""
    if len(view.sel()) > 0:
        selected_text = view.sel()[0]
        selected_line = view.line(sublime.Region(selected_text.begin() - 1, selected_text.begin() - 1))
        preceding_text = view.substr(sublime.Region(selected_line.begin(), selected_text.begin() - 1)).strip()
        function_call_regex = r".*?([a-zA-Z0-9_$]+)\s*\(.*?\)"
        match = re.search(function_call_regex, preceding_text)
        if match:
            function_call = match.group(1)
    return function_call


def get_preceding_token(view):
    token = ""
    if len(view.sel()) > 0:
        selected_text = view.sel()[0]
        if selected_text.begin() > 2:
            token_region = sublime.Region(selected_text.begin() - 1, selected_text.begin() - 1)
            token = get_token_at(view, token_region)
    return token


# Complete this.
def get_preceding_call_chain(view):
    word = ""
    if len(view.sel()) > 0:
        selected_text = view.sel()[0]
        selected_text = view.sel()[0]
        selected_line = view.line(sublime.Region(selected_text.begin() - 1, selected_text.begin() - 1))
        preceding_text = view.substr(sublime.Region(selected_line.begin(), selected_text.begin() - 1)).strip()
        function_call_regex = r".*?([a-zA-Z0-9_$]+)\s*\(.*?\)"
        match = re.search(function_call_regex, preceding_text)
        if match:
            #function_call = match.group(1)
            pass
    return word


def is_capitalized(word):
    capitalized = False
    # Underscores are sometimes used to indicate an internal property, so we
    # find the first occurrence of an a-zA-Z character. If not found, we assume lowercase.
    az_word = re.sub("[^a-zA-Z]", "", word)
    if len(az_word) > 0:
        first_letter = az_word[0]
        capitalized = first_letter.isupper()

    # Special case for $
    capitalized = capitalized | word.startswith("$")

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
        opened_file = open(file_path, "r")  # r = read only
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
        positions_tuple = (matched_row, matched_column, match_found, line_start_index)

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
    return bool(re.match(COFFEESCRIPT_SYNTAX, get_syntax_name(view)))


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


def get_variable_type(file_lines, token, start_region, global_file_path_list, built_in_types, previous_variable_names=[]):

    type_found = None

    # Check for "this"
    if token == "this":
        type_found = get_this_type(file_lines, start_region)
    elif token.startswith("@"):
        token = "this." + token[1:]

    # We're looking for a variable assignent
    assignment_regex = ASSIGNMENT_VALUE_WITH_DOT_REGEX % token

    # print "Assignment regex: " + assignment_regex

    # Search backwards from current position for the type
    if not type_found:
        match_tuple = search_backwards_for(file_lines, assignment_regex, start_region)
        if match_tuple:
            type_found = get_type_from_assignment_match_tuple(token, match_tuple, file_lines, previous_variable_names)
            # Well, we found the assignment. But we don't know what it is.
            # Let's try to find a variable name and get THAT variable type...
            if not type_found:
                type_found = get_type_from_assigned_variable_name(file_lines, token, match_tuple, global_file_path_list, built_in_types, previous_variable_names)

    # Let's try searching backwards for parameter hints in comments...
    if not type_found:
        # The regex used to search for the variable as a parameter in a method
        param_regex = PARAM_REGEX.format(name=re.escape(token))
        match_tuple = search_backwards_for(file_lines, param_regex, start_region)
        # We found the variable! it's a parameter. Let's find a comment with a type hint.
        if match_tuple:
            type_found = get_type_from_parameter_match_tuple(token, match_tuple, file_lines, previous_variable_names)

    # If backwards searching isn't working, at least try to find something...
    if not type_found:
        # Forward search from beginning for assignment:
        match_tuple = get_positions_of_regex_match_in_file(file_lines, assignment_regex)
        if match_tuple:
            type_found = get_type_from_assignment_match_tuple(token, match_tuple, file_lines, previous_variable_names)
            if not type_found:
                type_found = get_type_from_assigned_variable_name(file_lines, token, match_tuple, global_file_path_list, built_in_types, previous_variable_names)

    # If still nothing, maybe it's an @ parameter in the constructor?
    if not type_found:

        # Get the last word in the chain, if it's a chain.
        # E.g. Get variableName from this.variableName.[autocomplete]
        selected_word = token[token.rfind(".") + 1:]

        if token.startswith(THIS_KEYWORD + ".") or token.startswith(THIS_SUGAR_SYMBOL):

            # The regex used to search for the variable as a parameter in a method
            param_regex = CONSTRUCTOR_SELF_ASSIGNMENT_PARAM_REGEX.format(name=re.escape(selected_word))

            # Forward search from beginning for param:
            match_tuple = get_positions_of_regex_match_in_file(file_lines, param_regex)
            # We found the variable! it's a parameter. Let's find a comment with a type hint.
            if match_tuple:
                type_found = get_type_from_parameter_match_tuple(selected_word, match_tuple, file_lines)

        if not type_found:
            # Find something. Anything!
            word_assignment_regex = ASSIGNMENT_VALUE_WITHOUT_DOT_REGEX % selected_word

            # Forward search from beginning for assignment:
            match_tuple = get_positions_of_regex_match_in_file(file_lines, word_assignment_regex)
            if match_tuple:
                type_found = get_type_from_assignment_match_tuple(token, match_tuple, file_lines, previous_variable_names)
                if not type_found:
                    type_found = get_type_from_assigned_variable_name(file_lines, token, match_tuple, global_file_path_list, built_in_types, previous_variable_names)

    return type_found


def get_type_from_assigned_variable_name(file_lines, token, match_tuple, global_file_path_list, built_in_types, previous_variable_names=[]):

    type_found = None

    assignment_value_string = match_tuple[2].group(2).strip()
    # row start index + column index
    token_index = match_tuple[3] + match_tuple[1]
    token_region = sublime.Region(token_index, token_index)
    token_match = re.search(r"^([a-zA-Z0-9_$.]+)$", assignment_value_string)
    if token_match:
        next_token = token_match.group(1)
        if next_token not in previous_variable_names:
            previous_variable_names.append(token)
            type_found = get_variable_type(file_lines, next_token, token_region, global_file_path_list, built_in_types, previous_variable_names)

    # Determine what type a method returns
    if not type_found:
        # print "assignment_value_string: " + assignment_value_string
        method_call_regex = r"([a-zA-Z0-9_$.]+)\s*[.]\s*([a-zA-Z0-9_$]+)\s*\("
        method_call_match = re.search(method_call_regex, assignment_value_string)
        if method_call_match:
            object_name = method_call_match.group(1)
            method_name = method_call_match.group(2)
            object_type = get_variable_type(file_lines, object_name, token_region, global_file_path_list, built_in_types, previous_variable_names)
            if object_type:
                type_found = get_return_type_for_method(object_type, method_name, file_lines, global_file_path_list, built_in_types)

    return type_found


def get_return_type_for_method(object_type, method_name, file_lines, global_file_path_list, built_in_types):

    type_found = None

    next_class_to_scan = object_type

    # Search the class and all super classes
    while next_class_to_scan and not type_found:

        class_regex = CLASS_REGEX % re.escape(next_class_to_scan)
        # (file_path, row, column, match, row_start_index)
        class_location_search_tuple = find_location_of_regex_in_files(class_regex, file_lines, global_file_path_list)
        if class_location_search_tuple:

            file_found = class_location_search_tuple[0]

            # Consider if it was found locally, in the view
            if not file_found:
                class_file_lines = file_lines
            else:
                class_file_lines = get_lines_for_file(file_found)

            # If found, search for the method in question.
            method_regex = FUNCTION_REGEX % re.escape(method_name)
            positions_tuple = get_positions_of_regex_match_in_file(class_file_lines, method_regex)
            # (row, column, match, row_start_index)
            if positions_tuple:
                # Check for comments, and hopefully the return hint, on previous rows.
                matched_row = positions_tuple[0]
                row_to_check_index = matched_row - 1

                non_comment_code_reached = False
                while not non_comment_code_reached and row_to_check_index >= 0 and not type_found:
                    current_row_text = class_file_lines[row_to_check_index]

                    # Make sure this line only contains comments.
                    mod_line = re.sub(SINGLE_LINE_COMMENT_REGEX, "", current_row_text).strip()
                    # If it wasn't just a comment line...
                    if len(mod_line) > 0:
                        non_comment_code_reached = True
                    else:
                        # Search for hint: @return [TYPE]
                        return_type_hint_regex = r"@return\s*\[([a-zA-Z0-9_$]+)\]"
                        hint_match = re.search(return_type_hint_regex, current_row_text)
                        if hint_match:
                            # We found it!
                            type_found = hint_match.group(1)
                    row_to_check_index = row_to_check_index - 1

            # If nothing was found, see if the class extends another one and is inheriting the method.
            if not type_found:
                extends_regex = CLASS_REGEX_WITH_EXTENDS % next_class_to_scan
                # (row, column, match, row_start_index)
                extends_match_positions = get_positions_of_regex_match_in_file(class_file_lines, extends_regex)
                if extends_match_positions:
                    extends_match = extends_match_positions[2]
                    next_class_to_scan = extends_match.group(3)
                else:
                    next_class_to_scan = None
    return type_found


def get_type_from_assignment_match_tuple(variable_name, match_tuple, file_lines, previous_variable_names=[]):

    type_found = None
    if match_tuple:
        match = match_tuple[2]
        assignment_value_string = match.group(2)
        # Check for a type hint on current row or previous row.
        # These will override anything else.
        matched_row = match_tuple[0]
        previous_row = matched_row - 1
        current_row_text = file_lines[matched_row]
        hint_match = re.search(TYPE_HINT_COMMENT_REGEX, current_row_text)
        if hint_match:
            type_found = hint_match.group(1)
        if not type_found and previous_row >= 0:
            previous_row_text = file_lines[previous_row]
            hint_match = re.search(TYPE_HINT_COMMENT_REGEX, previous_row_text)
            if hint_match:
                type_found = hint_match.group(1)
        if not type_found:
            assignment_value_string = re.sub(SINGLE_LINE_COMMENT_REGEX, "", assignment_value_string).strip()
            type_found = get_type_from_assignment_value(assignment_value_string)
    return type_found


def get_type_from_parameter_match_tuple(variable_name, match_tuple, file_lines, previous_variable_names=[]):

    type_found = None
    if match_tuple:
        # Check for comments, and hopefully type hints, on previous rows.
        matched_row = match_tuple[0]
        row_to_check_index = matched_row - 1

        non_comment_code_reached = False
        while not non_comment_code_reached and row_to_check_index >= 0 and not type_found:
            current_row_text = file_lines[row_to_check_index]

            # Make sure this line only contains comments.
            mod_line = re.sub(SINGLE_LINE_COMMENT_REGEX, "", current_row_text).strip()
            # If it wasn't just a comment line...
            if len(mod_line) > 0:
                non_comment_code_reached = True
            else:
                # It's a comment. Let's look for a type hint in the form:
                # variable_name [TYPE] ~OR~ [TYPE] variable_name
                hint_regex = TYPE_HINT_PARAMETER_COMMENT_REGEX.format(var_name=re.escape(variable_name))
                hint_match = re.search(hint_regex, current_row_text)
                if hint_match:
                    # One of these two groups contains the type...
                    if hint_match.group(2):
                        type_found = hint_match.group(2)
                    else:
                        type_found = hint_match.group(6)
            row_to_check_index = row_to_check_index - 1
    return type_found


def get_type_from_assignment_value(assignment_value_string):
    determined_type = None

    assignment_value_string = assignment_value_string.strip()

    # Check for built in types
    object_regex = r"^\{.*\}$"
    if not determined_type:
        match = re.search(object_regex, assignment_value_string)
        if match:
            determined_type = "Object"
    double_quote_string_regex = r"(^\".*\"$)|(^.*?\+\s*\".*?\"$)|(^\".*?\"\s*\+.*?$)|(^.*?\s*\+\s*\".*?\"\s*\+\s*.*?$)"
    if not determined_type:
        match = re.search(double_quote_string_regex, assignment_value_string)
        if match:
            determined_type = "String"
    single_quote_string_regex = r"(^['].*[']$)|(^.*?\+\s*['].*?[']$)|(^['].*?[']\s*\+.*?$)|(^.*?\s*\+\s*['].*?[']\s*\+\s*.*?$)"
    if not determined_type:
        match = re.search(single_quote_string_regex, assignment_value_string)
        if match:
            determined_type = "String"
    array_regex = r"^\[.*\]\s*$"
    if not determined_type:
        match = re.search(array_regex, assignment_value_string)
        if match:
            determined_type = "Array"
    boolean_regex = r"^(true)|(false)$"
    if not determined_type:
        match = re.search(boolean_regex, assignment_value_string)
        if match:
            determined_type = "Boolean"
    # http://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string-in-python
    number_regex = r"^[-+]?\d*\.\d+|\d+$"
    if not determined_type:
        match = re.search(number_regex, assignment_value_string)
        if match:
            determined_type = "Number"
    regexp_regex = r"^/.*/[a-z]*$"
    if not determined_type:
        match = re.search(regexp_regex, assignment_value_string)
        if match:
            determined_type = "RegExp"
    new_operation_regex = NEW_OPERATION_REGEX
    if not determined_type:
        match = re.search(new_operation_regex, assignment_value_string)
        if match:
            determined_type = get_class_from_end_of_chain(match.group(1))

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
        for i in reversed(range(start_line + 1)):
            previous_line = file_lines[i]
            # print "Next line: " + previous_line[:-1]
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


def get_completions_for_class(class_name, search_statically, local_file_lines, prefix, global_file_path_list, built_in_types, member_exclusion_regexes, show_private):

    # TODO: Use prefix to make suggestions.

    completions = []
    scanned_classes = []
    original_class_name_found = False

    function_completions = []
    object_completions = []

    # First, determine if it is a built in type and return those completions...
    # Built-in types include String, Number, etc, and are configurable in settings.
    for next_built_in_type in built_in_types:
        try:
            if next_built_in_type[BUILT_IN_TYPES_TYPE_ENABLED_KEY]:
                next_class_name = next_built_in_type[BUILT_IN_TYPES_TYPE_NAME_KEY]
                if next_class_name == class_name:
                    # We are looking at a built-in type! Collect completions for it...
                    completions = get_completions_for_built_in_type(next_built_in_type, search_statically, False, member_exclusion_regexes)
                    original_class_name_found = True
                elif next_class_name == "Function" and not function_completions:
                    function_completions = get_completions_for_built_in_type(next_built_in_type, False, True, member_exclusion_regexes)
                elif next_class_name == "Object" and not object_completions:
                    object_completions = get_completions_for_built_in_type(next_built_in_type, False, True, member_exclusion_regexes)
        except Exception, e:
            print repr(e)

    # If we didn't find completions for a built-in type, look further...
    if not completions:
        current_class_name = class_name
        is_inherited = False
        while current_class_name and current_class_name not in scanned_classes:
            # print "Scanning " + current_class_name + "..."
            # (class_found, completions, next_class_to_scan)
            completion_tuple = (False, [], None)
            if local_file_lines:
                # print "Searching locally..."
                # Search in local file.
                if search_statically:
                    completion_tuple = collect_static_completions_from_file(local_file_lines, current_class_name, is_inherited, member_exclusion_regexes, show_private)
                else:
                    completion_tuple = collect_instance_completions_from_file(local_file_lines, current_class_name, is_inherited, member_exclusion_regexes, show_private)

            # Search globally if nothing found and not local only...
            if global_file_path_list and (not completion_tuple or not completion_tuple[0]):
                class_regex = CLASS_REGEX % re.escape(current_class_name)
                global_class_location_search_tuple = find_location_of_regex_in_files(class_regex, None, global_file_path_list)
                if global_class_location_search_tuple:
                    # If found, perform Class method collection.
                    file_to_open = global_class_location_search_tuple[0]
                    class_file_lines = get_lines_for_file(file_to_open)
                    if search_statically:
                        completion_tuple = collect_static_completions_from_file(class_file_lines, current_class_name, is_inherited, member_exclusion_regexes, show_private)
                    else:
                        completion_tuple = collect_instance_completions_from_file(class_file_lines, current_class_name, is_inherited, member_exclusion_regexes, show_private)

            if current_class_name == class_name and completion_tuple[0]:
                original_class_name_found = True

            # print "Tuple: " + str(completion_tuple)
            completions.extend(completion_tuple[1])
            scanned_classes.append(current_class_name)
            current_class_name = completion_tuple[2]
            is_inherited = True

    if original_class_name_found:
        # Add Object completions (if available) -- Everything is an Object
        completions.extend(object_completions)
        if search_statically:
            completions.extend(function_completions)

    # Remove all duplicates
    completions = list(set(completions))
    # Sort
    completions.sort()
    return completions


def case_insensitive_startswith(original_string, prefix):
    return original_string.lower().startswith(prefix.lower())


def get_completions_for_built_in_type(built_in_type, is_static, is_inherited, member_exclusion_regexes):
    completions = []
    if is_static:
        static_properties = []
        static_property_objs = built_in_type[BUILT_IN_TYPES_STATIC_PROPERTIES_KEY]
        for next_static_property_obj in static_property_objs:
            next_static_property = next_static_property_obj[BUILT_IN_TYPES_STATIC_PROPERTY_NAME_KEY]
            if not is_member_excluded(next_static_property, member_exclusion_regexes):
                static_properties.append(next_static_property)
        for next_static_property in static_properties:
            next_completion = get_property_completion_tuple(next_static_property, is_inherited)
            completions.append(next_completion)

        static_methods = built_in_type[BUILT_IN_TYPES_STATIC_METHODS_KEY]
        for next_static_method in static_methods:
            method_name = next_static_method[BUILT_IN_TYPES_METHOD_NAME_KEY]
            if not is_member_excluded(method_name, member_exclusion_regexes):
                method_args = []
                method_insertions = []
                method_args_objs = next_static_method[BUILT_IN_TYPES_METHOD_ARGS_KEY]
                for next_method_arg_obj in method_args_objs:
                    method_arg = next_method_arg_obj[BUILT_IN_TYPES_METHOD_ARG_NAME_KEY]
                    method_args.append(method_arg)
                    method_insertion = method_arg
                    try:
                        method_insertion = next_method_arg_obj[BUILT_IN_TYPES_METHOD_INSERTION_KEY]
                    except:
                        pass
                    method_insertions.append(method_insertion)
                next_completion = get_method_completion_tuple(method_name, method_args, method_insertions, is_inherited)
                completions.append(next_completion)
    else:
        instance_properties = []
        instance_property_objs = built_in_type[BUILT_IN_TYPES_INSTANCE_PROPERTIES_KEY]
        for next_instance_property_obj in instance_property_objs:
            next_instance_property = next_instance_property_obj[BUILT_IN_TYPES_INSTANCE_PROPERTY_NAME_KEY]
            if not is_member_excluded(next_instance_property, member_exclusion_regexes):
                instance_properties.append(next_instance_property_obj[BUILT_IN_TYPES_INSTANCE_PROPERTY_NAME_KEY])
        for next_instance_property in instance_properties:
            next_completion = get_property_completion_tuple(next_instance_property, is_inherited)
            completions.append(next_completion)

        instance_methods = built_in_type[BUILT_IN_TYPES_INSTANCE_METHODS_KEY]
        for next_instance_method in instance_methods:
            method_name = next_instance_method[BUILT_IN_TYPES_METHOD_NAME_KEY]
            if not is_member_excluded(method_name, member_exclusion_regexes):
                method_args = []
                method_insertions = []
                method_args_objs = next_instance_method[BUILT_IN_TYPES_METHOD_ARGS_KEY]
                for next_method_arg_obj in method_args_objs:
                    method_arg = next_method_arg_obj[BUILT_IN_TYPES_METHOD_ARG_NAME_KEY]
                    method_args.append(method_arg)
                    method_insertion = method_arg
                    try:
                        method_insertion = next_method_arg_obj[BUILT_IN_TYPES_METHOD_INSERTION_KEY]
                    except:
                        pass
                    method_insertions.append(method_insertion)
                next_completion = get_method_completion_tuple(method_name, method_args, method_insertions, is_inherited)
                completions.append(next_completion)
    return completions


def collect_instance_completions_from_file(file_lines, class_name, is_inherited, member_exclusion_regexes, show_private):

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
        row = match_tuple[0]
        match = match_tuple[2]

        extended_class = match.group(3)
        if extended_class:
            extended_class = get_class_from_end_of_chain(extended_class)

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
                                if show_private or not is_member_excluded(prop, member_exclusion_regexes):
                                    prop_completion_alias = get_property_completion_alias(prop, is_inherited)
                                    prop_completion_insertion = get_property_completion_insertion(prop)
                                    prop_completion = (prop_completion_alias, prop_completion_insertion)
                                    if prop_completion not in property_completions:
                                        property_completions.append(prop_completion)
                        else:  # Not in constructor
                            # Look for method definitions
                            function_regex = FUNCTION_REGEX_ANY
                            match = re.search(function_regex, next_row)
                            if match and not re.search(STATIC_FUNCTION_REGEX, next_row):
                                function_name = match.group(2)
                                function_args_string = match.group(5)
                                if show_private or not is_member_excluded(function_name, member_exclusion_regexes):
                                    if not function_name in CONSTRUCTOR_KEYWORDS:
                                        function_args_list = []
                                        if function_args_string:
                                            function_args_list = function_args_string.split(",")
                                        for i in range(len(function_args_list)):
                                            # Fix each one up...
                                            next_arg = function_args_list[i]
                                            next_arg = next_arg.strip()
                                            next_arg = re.sub("[^a-zA-Z0-9_$].*", "", next_arg)
                                            function_args_list[i] = re.sub(THIS_SUGAR_SYMBOL, "", next_arg)
                                        function_alias = get_method_completion_alias(function_name, function_args_list, is_inherited)
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
                                                if show_private or not is_member_excluded(next_arg, member_exclusion_regexes):
                                                    prop_completion_alias = get_property_completion_alias(next_arg, is_inherited)
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


def get_class_from_end_of_chain(dot_operation_chain):
    class_at_end = dot_operation_chain
    next_period_index = class_at_end.find(PERIOD_OPERATOR)
    while next_period_index >= 0:
        class_at_end = class_at_end[(next_period_index + 1):]
        class_at_end.strip()
        next_period_index = class_at_end.find(PERIOD_OPERATOR)
    if len(class_at_end) == 0:
        class_at_end = None
    return class_at_end


def collect_static_completions_from_file(file_lines, class_name, is_inherited, member_exclusion_regexes, show_private):

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
        row = match_tuple[0]
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
                            pass
                        # Otherwise, save this indentation and examine the current line, as it's class-level
                        else:
                            previous_indentation = next_indentation
                            function_regex = STATIC_FUNCTION_REGEX
                            match = re.search(function_regex, next_row)
                            if match:
                                function_name = match.group(4)
                                if show_private or not is_member_excluded(function_name, member_exclusion_regexes):
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
                                    function_alias = get_method_completion_alias(function_name, function_args_list, is_inherited)
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
                                    if show_private or not is_member_excluded(prop, member_exclusion_regexes):
                                        prop_completion_alias = get_property_completion_alias(prop, is_inherited)
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


def get_property_completion_alias(property_name, is_inherited=False):
    indicator = PROPERTY_INDICATOR
    if is_inherited:
        indicator = INHERITED_INDICATOR + indicator
    completion_string = indicator + " " + property_name
    return completion_string


def get_property_completion_insertion(property_name):
    completion_string = property_name
    completion_string = re.sub("[$]", "\$", completion_string)
    return completion_string


def get_property_completion_tuple(property_name, is_inherited=False):
    completion_tuple = (get_property_completion_alias(property_name, is_inherited), get_property_completion_insertion(property_name))
    return completion_tuple


def get_method_completion_alias(method_name, args, is_inherited=False):
    indicator = METHOD_INDICATOR
    if is_inherited:
        indicator = INHERITED_INDICATOR + indicator
    completion_string = indicator + " " + method_name + "("
    for i in range(len(args)):
        completion_string = completion_string + args[i]
        if i < len(args) - 1:
            completion_string = completion_string + ", "
    completion_string = completion_string + ")"
    return completion_string


def get_method_completion_insertion(method_name, args):

    no_parens = False

    completion_string = re.sub("[$]", "\$", method_name)

    if len(args) == 1:
        function_match = re.search(r".*?[=\-]>.*", args[0])
        if function_match:
            no_parens = True

    if no_parens:
        completion_string = completion_string + " "
    else:
        completion_string = completion_string + "("

    for i in range(len(args)):
        escaped_arg = re.sub("[$]", "\$", args[i])
        completion_string = completion_string + "${" + str(i + 1) + ":" + escaped_arg + "}"
        if i < len(args) - 1:
            completion_string = completion_string + ", "

    if not no_parens:
        completion_string = completion_string + ")"

    return completion_string


def get_method_completion_tuple(method_name, arg_names, arg_insertions, is_inherited=False):
    completion_tuple = (get_method_completion_alias(method_name, arg_names, is_inherited), get_method_completion_insertion(method_name, arg_insertions))
    return completion_tuple


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


def is_member_excluded(member, exclusion_regexes):
    excluded = False
    for next_exclusion_regex in exclusion_regexes:
        if re.search(next_exclusion_regex, member):
            excluded = True
    return excluded

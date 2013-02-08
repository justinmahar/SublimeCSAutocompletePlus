CoffeeScript Autocomplete Plus (CAP)
====================================

Can it be true? Autocompletions for CoffeeScript? I'm here to tell you: They're real, and they're spectacular.

CoffeeScript Autocomplete Plus scans your CoffeeScript files on demand and makes autocomplete suggestions for you.

In addition, this plugin adds the "Coffee: Goto Definition" command, which will look up the class, function or variable definition of the selected token. 

Do you miss having a control-click key combination to go to a definition? Well, that's here too. Oh baby.

Features
--------

### Autocomplete

Autocomplete will make suggestions when you trigger autocomplete after a dot operator. It starts with the current view, then branches out to other coffee files. Because of this, most lookups are blazingly fast. You can configure CAP to exclude certain directories and to only look in others. This will further increase speed as less searching will be needed.

Here are the main features: 
* Suggests instance properties and methods when operating on an instance.

		myLamp = new LavaLamp()
		# Lists all instance properties and methods
		myLamp.[autocomplete]

* Suggests static properties and methods when operating on a class.

		# Lists all static properties and methods
		LavaLamp.[autocomplete]

* Supports "this" keyword and any defined aliases.

		class LavaLamp
			heatUp: ->
				console.log "Heating up!"
			coolDown: ->
				console.log "Cooling down!"
			beAwesome: ->
				# Lists heatUp() and coolDown()
				this.[autocomplete]

* Any variable assigned to `this` in the constructor will be considered an instance property.
* After autocompleting a method, tab stops for parameters are provided (if applicable).
* Suggests super class properties and functions. This applies to both instance and static suggestions.
* Expects that you don't suck at naming things. Will assume a class is UpperCamelCase and everything else is lowerCamelCase. It still works either way; it will just be faster if things are named properly.
* For every 1 million autocompletions, a beautiful masseuse appears and give you a massage. You must be tired after all that coding.

### Goto Definition

Goto Definition is useful for finding where a class, function, or variable was defined or declared. Again, searching is performed from the current view and branches out to other files if nothing is found. You can quickly jump between classes and zoom to functions--even ones defined in other files--with ease.

* Supports classes, functions and variable assignment.
* Searches backwards from selected token for assignment.
* Considers variables declared in for loops.
* Considers method parameters.
* Tries to find something rather than nothing.
* Includes both mouse and keyboard shortcuts for convenience. Code your way.

### General 

* Generally fast lookups.
* You can configure directories to be be excluded from global .coffee search (recommended)
* You can configure the tool to only search in specific locations (recommended)

Installation
------------

### Package Control

It is recommended that you use [Sublime Package Control](http://wbond.net/sublime_packages/package_control) to install CoffeeScript Autocomplete Plus. If you have Package Control installed, use the Package Control: Install Package command and search for CoffeeScript Autocomplete Plus. Ouila. Start coding easier.

### Manual Installation

In order to manually install CoffeeScript Autocomplete Plus, clone the repository into your Sublime Text 2 `Packages` directory, which can be located by navigating to Preferences -> Browse Packages. Name the directory `CoffeeScript Autocomplete Plus`.

For your convenience:

```
git clone https://github.com/justinmahar/SublimeCSAutocompletePlus.git "CoffeeScript Autocomplete Plus"
```

Usage
-----

### Autocomplete

Autocomplete can be triggered in coffee files after the dot operator. With the cursor after a dot operator `.`, press `ctrl+space`. This will trigger autocomplete, which will then try to figure out what you're doing and propose a list of suggestions.

Example usage: Inside a class, you type `this.` and would like a list of the available methods and properties. Press `ctrl+space` to trigger autocomplete, and view the available suggestions.

### Goto Definition

Looking for where a class, function or variable was defined? Look no further.

Place your cursor on any word and press `ctrl+alt+d` in Windows/Linux, and `ctrl+alt+d` in OS X, to goto the definition of the selected class, function or variable.

Alternatively, use `ctrl+alt` + `left click` in Windows/Linux, and `ctrl+alt` + `left click` in OS X.

Default Key Bindings
--------------------

### Windows/Linux:

Autocomplete: `ctrl+space` (after a dot operator)

Goto Definition: `ctrl+alt+d` or `ctrl+alt`+`left click`

### Mac OS X:

Autocomplete: `ctrl+space` (after a dot operator)

Goto Definition: `ctrl+alt+d` or `ctrl+alt`+`left click`

Configuration
-------------

CoffeeScript Autocomplete Plus has the following configurable settings:

* Excluded directories -- `coffee_autocomplete_plus_excluded_dirs`
  - Directories to exclude from searching for CoffeeScript classes, functions and variables.
* Aliases for `this` keyword -- `coffee_autocomplete_plus_this_aliases`
  - Due to lexical scoping you sometimes need to assign an alias for `this`, such as `that` or `self`.

To configure these settings, open Preferences -> Package Settings -> CoffeeScript Autocomplete Plus -> Settings.  It is not recommended that you change the Default settings as they will be overwritten by plugin updates. Instead, make your changes in User settings, which will override the Default settings.

Key bindings can be changed by navigating to Preferences -> Package Settings -> CoffeeScript Autocomplete Plus -> Key Bindings. Same spiel as before about where to put your settings.

Limitations and Plans
---------------------

> "Conceal a flaw, and the world will imagine the worst." — Marcus Aurelius, 16th Emperor of the Roman Empire

Autocomplete is smart, but not Mensa smart. Under the hood, we're not building an index or anything. We're using regular expressions and lots of scanning. As I build out functionality, I will try to fix its limitations. 

For now, here is the list of TBDs:

* Check contents of currently open views besides the active one
* Smarter assignment detection
* Better token parsing
* Hinting

License
-------
CoffeeScript Autocomplete Plus is licensed under the MIT license.

Copyright (c) 2013 Justin Mahar <justin.m.mahar@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
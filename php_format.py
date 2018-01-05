#!/usr/bin/python
# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import sys
import string
import random
import subprocess


def random_php_filename():
    return '/tmp/' + ''.join(random.choice(string.ascii_uppercase
                             + string.digits) for _ in range(16)) \
        + '.php'


# dependency : php-cs-fixer
# curl -L http://cs.sensiolabs.org/download/php-cs-fixer-v2.phar -o /tmp/php-cs-fixer
# sudo chmod a+x /tmp/php-cs-fixer
# sudo mv /tmp/php-cs-fixer /usr/local/bin/php-cs-fixer

class PhpFormatCommand(sublime_plugin.TextCommand):

    def selection(self):
        region = self.view.sel()[0]
        return region

    def get_indentation(self, code):
        return min([len(line) - len(line.lstrip()) for line in
                   code.split('\n')[1:] if len(line) > 0])

    def set_indentation(self, code, indentation):
        if self.get_indentation(code) == indentation:
            return code
        return code.replace('\n', '\n' + ' ' * indentation)

    def selected_code(self):
        region = self.selection()
        code = self.view.substr(region)
        code = code.replace('\t', ' ' * 4)
        return code

    def update_selection(self, code, edit):
        region = self.selection()
        self.view.erase(edit, region)
        self.view.insert(edit, region.begin(), code)

    def psr2(self, code):
        indentation = self.get_indentation(code)
        file_name = random_php_filename()
        hasTag = code.startswith('<?php')
        with open(file_name, 'w') as file:
            if not hasTag:
                file.write('<?php\n')
            file.write(code)
        p = subprocess.Popen(['php-cs-fixer', '-n', 'fix', file_name])
        p.communicate()
        formatted_code = code
        file = open(file_name, 'r')
        with open(file_name, 'r') as file:
            lines = file.readlines()
            if not hasTag:
                lines = lines[1:]
            formatted_code = ''.join(lines)
        if formatted_code != code:
            formatted_code = self.set_indentation(formatted_code, indentation)
        return formatted_code

    def run(self, edit):
        code = self.selected_code()
        formatted_code = self.psr2(code)
        self.update_selection(formatted_code, edit)
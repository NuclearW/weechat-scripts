# -*- coding: utf-8 -*-
###
# Copyright (c) 2009-2012 by Elián Hanisch <lambdae2@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###

###
# Search in Weechat buffers and logs (for Weechat 0.3.*)
#
#   Inspired by xt's grep.py
#   Originally I just wanted to add some fixes in grep.py, but then
#   I got carried away and rewrote everything, so new script.
#
#   Commands:
#   * /grep
#     Search in logs or buffers, see /help grep
#   * /logs:
#     Lists logs in ~/.weechat/logs, see /help logs
#
#   Settings:
#   * plugins.var.python.grep.clear_buffer:
#     Clear the results buffer before each search. Valid values: on, off
#
#   * plugins.var.python.grep.go_to_buffer:
#     Automatically go to grep buffer when search is over. Valid values: on, off
#
#   * plugins.var.python.grep.show_summary:
#     Shows summary for each log. Valid values: on, off
#
#   * plugins.var.python.grep.max_lines:
#     Grep will only print the last matched lines that don't surpass the value defined here.
#
#   * plugins.var.python.grep.size_limit:
#     Size limit in KiB, is used for decide whenever grepping should run in background or not. If
#     the logs to grep have a total size bigger than this value then grep run as a new process.
#     It can be used for force or disable background process, using '0' forces to always grep in
#     background, while using '' (empty string) will disable it.
#
#   * plugins.var.python.grep.default_tail_head:
#     Config option for define default number of lines returned when using --head or --tail options.
#     Can be overriden in the command with --number option.
#
#
#   TODO:
#   * try to figure out why hook_process chokes in long outputs (using a tempfile as a
#   workaround now)
#   * possibly add option for defining time intervals
#   * try to reduce memory usage when matching lots of lines
#   * fix using "\" at the end of the regex
#   * fix using "'" in regexs
#
#
#   History:
#   2012-
#   version 0.8:
#   * removed log_filter option, I hardly use it now and slows down the log completer.
#   * removed options --all and --buffer
#   * added command /lastlog
#
#   2011-01-09
#   version 0.7.2: bug fixes
#
#   2010-11-15
#   version 0.7.1:
#   * use TempFile so temporal files are guaranteed to be deleted.
#   * enable Archlinux workaround.
#
#   2010-10-26
#   version 0.7:
#   * added templates.
#   * using --only-match shows only unique strings.
#   * fixed bug that inverted -B -A switches when used with -t
#
#   2010-10-14
#   version 0.6.8: by xt <xt@bash.no>
#   * supress highlights when printing in grep buffer
#
#   2010-10-06
#   version 0.6.7: by xt <xt@bash.no> 
#   * better temporary file:
#    use tempfile.mkstemp. to create a temp file in log dir, 
#    makes it safer with regards to write permission and multi user
#
#   2010-04-08
#   version 0.6.6: bug fixes
#   * use WEECHAT_LIST_POS_END in log file completion, makes completion faster
#   * disable bytecode if using python 2.6
#   * use single quotes in command string
#   * fix bug that could change buffer's title when using /grep stop
#
#   2010-01-24
#   version 0.6.5: disable bytecode is a 2.6 feature, instead, resort to delete the bytecode manually
#
#   2010-01-19
#   version 0.6.4: bug fix
#   version 0.6.3: added options --invert --only-match (replaces --exact, which is still available
#   but removed from help)
#   * use new 'irc_nick_color' info
#   * don't generate bytecode when spawning a new process
#   * show active options in buffer title
#
#   2010-01-17
#   version 0.6.2: removed 2.6-ish code
#   version 0.6.1: fixed bug when grepping in grep's buffer
#
#   2010-01-14
#   version 0.6.0: implemented grep in background
#   * improved context lines presentation.
#   * grepping for big (or many) log files runs in a weechat_process.
#   * added /grep stop.
#   * added 'size_limit' option
#   * fixed a infolist leak when grepping buffers
#   * added 'default_tail_head' option
#   * results are sort by line count
#   * don't die if log is corrupted (has NULL chars in it)
#   * changed presentation of /logs
#   * log path completion doesn't suck anymore
#   * removed all tabs, because I learned how to configure Vim so that spaces aren't annoying
#   anymore. This was the script's original policy.
#
#   2010-01-05
#   version 0.5.5: rename script to 'grep.py' (FlashCode <flashcode@flashtux.org>).
#
#   2010-01-04
#   version 0.5.4.1: fix index error when using --after/before-context options.
#
#   2010-01-03
#   version 0.5.4: new features
#   * added --after-context and --before-context options.
#   * added --context as a shortcut for using both -A -B options.
#
#   2009-11-06
#   version 0.5.3: improvements for long grep output
#   * grep buffer input accepts the same flags as /grep for repeat a search with different
#     options.
#   * tweaks in grep's output.
#   * max_lines option added for limit grep's output.
#   * code in update_buffer() optimized.
#   * time stats in buffer title.
#   * added go_to_buffer config option.
#   * added --buffer for search only in buffers.
#   * refactoring.
#
#   2009-10-12, omero
#   version 0.5.2: made it python-2.4.x compliant
#
#   2009-08-17
#   version 0.5.1: some refactoring, show_summary option added.
#
#   2009-08-13
#   version 0.5: rewritten from xt's grep.py
#   * fixed searching in non weechat logs, for cases like, if you're
#     switching from irssi and rename and copy your irssi logs to %h/logs
#   * fixed "timestamp rainbow" when you /grep in grep's buffer
#   * allow to search in other buffers other than current or in logs
#     of currently closed buffers with cmd 'buffer'
#   * allow to search in any log file in %h/logs with cmd 'log'
#   * added --count for return the number of matched lines
#   * added --matchcase for case sensible search
#   * added --hilight for color matches
#   * added --head and --tail options, and --number
#   * added command /logs for list files in %h/logs
#   * added config option for clear the buffer before a search
#   * added config option for filter logs we don't want to grep
#   * added the posibility to repeat last search with another regexp by writing
#     it in grep's buffer
#   * changed spaces for tabs in the code, which is my preference
#
###

import os
import re
import sys
import time
import getopt
import tempfile
from os import path
from fnmatch import fnmatch

try:
    import weechat
    from weechat import WEECHAT_RC_OK, prnt, prnt_date_tags
    import_ok = True
except ImportError:
    import_ok = False

SCRIPT_NAME    = "grep"
SCRIPT_AUTHOR  = "Elián Hanisch <lambdae2@gmail.com>"
SCRIPT_VERSION = "0.8-dev"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Search in buffers and logs"
SCRIPT_COMMAND = "grep"

### Default Settings ###
settings = {
'clear_buffer'      : 'off',
'go_to_buffer'      : 'on',
'max_lines'         : '4000',
'show_summary'      : 'on',
'size_limit'        : '2048',
'default_tail_head' : '10',
}

# -------------------------------------------------------------------------
# Grep options

def positiveInt(value):
    try:
        value = int(value)
        if value < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError, "%s isn't a positive integer." % value
    return value

class GrepOptions(object):
    _options = {}
    
    def __init__(self):
        self.reset()

    def reset(self):
        self._options = {
                'pattern_tmpl': None,
                'pattern': None,
                'matchcase': False,
                'count': False,
                'exact': False,
                'hilight': '',
                'invert': False,
                'tail': False,
                'head': False,
                'number': None,
                'after_context': 0,
                'before_context': 0,
                }

    def __getattr__(self, name):
        return self._options[name]

    def __setattr__(self, name, value):
        if not hasattr(type(self), name):
            self._options[name] = value
        else:
            object.__setattr__(self, name, value)

    def setNumber(self, value):
        value = positiveInt(value)
        self._options['number'] = value

    def number(self):
        number = self._options['number']
        if number is None:
            return positiveInt(get_config_int('default_tail_head'))
        return number

    number = property(number, setNumber)

    def setAfterContext(self, value):
        if self.count or self.exact:
            value = 0
        value = positiveInt(value)
        self._options['after_context'] = value

    after_context = property(fset=setAfterContext)

    def setBeforeContext(self, value):
        if self.count or self.exact:
            value = 0
        value = positiveInt(value)
        self._options['before_context'] = value

    before_context = property(fset=setBeforeContext)

    def setTail(self, value):
        if self.count:
            value = False
        if value:
            self.head = False
        self._options['tail'] = value

    def tail(self):
        tail = self._options['tail']
        if tail:
            return self.number
        return 0

    tail = property(tail, setTail)

    def setHead(self, value):
        if self.count:
            value = False
        if value:
            self.tail = False
        self._options['head'] = value

    def head(self):
        head = self._options['head']
        if head:
            return self.number
        return 0

    head = property(head, fset=setHead)

    def setCount(self, value):
        if value:
            self._options.update({
                'tail': False,
                'head': False,
                'after_context': 0,
                'before_context': 0,
                'hilight': '',
                })
        self._options['count'] = value

    count = property(fset=setCount)

    def setHilight(self, value):
        if self.count or self.invert or self.exact:
            value = ''
        self._options['hilight'] = value

    hilight = property(fset=setHilight)

    def setExact(self, value):
        if value:
            self._options.update({
                'after_context': 0,
                'before_context': 0,
                'invert': False,
                'hilight': False,
                })
        self._options['exact'] = value

    exact = property(fset=setExact)

    def setInvert(self, value):
        if self.exact:
            value = False
        if value:
            self.hilight = False
        self._options['invert'] = value

    invert = property(fset=setInvert)


options = GrepOptions()

### Class definitions ###
class linesDict(dict):
    """
    Class for handling matched lines in more than one buffer.
    linesDict[buffer_name] = matched_lines_list
    """
    def __setitem__(self, key, value):
        assert isinstance(value, list)
        if key not in self:
            dict.__setitem__(self, key, value)
        else:
            dict.__getitem__(self, key).extend(value)

    def get_matches_count(self):
        """Return the sum of total matches stored."""
        if dict.__len__(self):
            return sum(map(lambda L: L.matches_count, self.itervalues()))
        else:
            return 0

    def __len__(self):
        """Return the sum of total lines stored."""
        if dict.__len__(self):
            return sum(map(len, self.itervalues()))
        else:
            return 0

    def __str__(self):
        """Returns buffer count or buffer name if there's just one stored."""
        n = len(self.keys())
        if n == 1:
            return self.keys()[0]
        elif n > 1:
            return '%s logs' %n
        else:
            return ''

    def items(self):
        """Returns a list of items sorted by line count."""
        items = dict.items(self)
        items.sort(key=lambda i: len(i[1]))
        return items

    def items_count(self):
        """Returns a list of items sorted by match count."""
        items = dict.items(self)
        items.sort(key=lambda i: i[1].matches_count)
        return items

    def strip_separator(self):
        for L in self.itervalues():
            L.strip_separator()

    def get_last_lines(self, n):
        total_lines = len(self)
        #debug('total: %s n: %s' %(total_lines, n))
        if n >= total_lines:
            # nothing to do
            return
        for k, v in reversed(self.items()):
            l = len(v)
            if n > 0:
                if l > n:
                    del v[:l-n]
                    v.stripped_lines = l-n
                n -= l
            else:
                del v[:]
                v.stripped_lines = l

class linesList(list):
    """Class for list of matches, since sometimes I need to add lines that aren't matches, I need an
    independent counter."""
    _sep = '...'
    def __init__(self, *args):
        list.__init__(self, *args)
        self.matches_count = 0
        self.stripped_lines = 0

    def append(self, item):
        """Append lines, can be a string or a list with strings."""
        if isinstance(item, str):
            list.append(self, item)
        else:
            self.extend(item)

    def append_separator(self):
        """adds a separator into the list, makes sure it doen't add two together."""
        s = self._sep
        if (self and self[-1] != s) or not self:
            self.append(s)

    def onlyUniq(self):
        # FIXME set screws up line order.
        s = set(self)
        del self[:]
        self.extend(s)

    def count_match(self, item=None):
        if item is None or isinstance(item, str):
            self.matches_count += 1
        else:
            self.matches_count += len(item)

    def strip_separator(self):
        """removes separators if there are first or/and last in the list."""
        if self:
            s = self._sep
            if self[0] == s:
                del self[0]
            if self[-1] == s:
                del self[-1]

### Misc functions ###
now = time.time
def get_size(f):
    try:
        return os.stat(f).st_size
    except OSError:
        return 0

sizeDict = {0:'b', 1:'KiB', 2:'MiB', 3:'GiB', 4:'TiB'}
def human_readable_size(size):
    power = 0
    while size > 1024:
        power += 1
        size /= 1024.0
    return '%.2f %s' %(size, sizeDict.get(power, ''))

def color_nick(nick):
    """Returns coloured nick, with coloured mode if any."""
    if not nick: return ''
    wcolor = weechat.color
    config_string = lambda s : weechat.config_string(weechat.config_get(s))
    config_int = lambda s : weechat.config_integer(weechat.config_get(s))
    # prefix and suffix
    prefix = config_string('irc.look.nick_prefix')
    suffix = config_string('irc.look.nick_suffix')
    prefix_c = suffix_c = wcolor(config_string('weechat.color.chat_delimiters'))
    if nick[0] == prefix:
        nick = nick[1:]
    else:
        prefix = prefix_c = ''
    if nick[-1] == suffix:
        nick = nick[:-1]
        suffix = wcolor(color_delimiter) + suffix
    else:
        suffix = suffix_c = ''
    # nick mode
    modes = '@!+%'
    if nick[0] in modes:
        mode, nick = nick[0], nick[1:]
        mode_color = wcolor(config_string('weechat.color.nicklist_prefix%d' \
            %(modes.find(mode) + 1)))
    else:
        mode = mode_color = ''
    # nick color
    nick_color = weechat.info_get('irc_nick_color', nick)
    if not nick_color:
        # probably we're in WeeChat 0.3.0
        #debug('no irc_nick_color')
        color_nicks_number = config_int('weechat.look.color_nicks_number')
        idx = (sum(map(ord, nick))%color_nicks_number) + 1
        nick_color = wcolor(config_string('weechat.color.chat_nick_color%02d' %idx))
    return ''.join((prefix_c, prefix, mode_color, mode, nick_color, nick, suffix_c, suffix))

### Config and value validation ###
boolDict = {'on':True, 'off':False}
def get_config_boolean(config):
    value = weechat.config_get_plugin(config)
    try:
        return boolDict[value]
    except KeyError:
        default = settings[config]
        error("Error while fetching config '%s'. Using default value '%s'." %(config, default))
        error("'%s' is invalid, allowed: 'on', 'off'" %value)
        return boolDict[default]

def get_config_int(config, allow_empty_string=False):
    value = weechat.config_get_plugin(config)
    try:
        return int(value)
    except ValueError:
        if value == '' and allow_empty_string:
            return value
        default = settings[config]
        error("Error while fetching config '%s'. Using default value '%s'." %(config, default))
        error("'%s' is not a number." %value)
        return int(default)

def get_home():
    home = weechat.config_string(weechat.config_get('logger.file.path'))
    # this path must end in /, makes other stuff easier.
    home = os.path.join(home, '')
    return home.replace('%h', weechat.info_get('weechat_dir', ''))

def strip_home(s, dir=''):
    """Strips home dir from the begging of the log path, this makes them sorter."""
    if not dir:
        dir = get_home()
    l = len(dir)
    if s[:l] == dir:
        return s[l:]
    return s

### Messages ###
script_nick = SCRIPT_NAME
def error(s, buffer=''):
    """Error msg"""
    prnt(buffer, '%s%s %s' %(weechat.prefix('error'), script_nick, s))
    if weechat.config_get_plugin('debug'):
        import traceback
        if traceback.sys.exc_type:
            trace = traceback.format_exc()
            prnt('', trace)

def say(s, buffer=''):
    """normal msg"""
    prnt_date_tags(buffer, 0, 'no_highlight,no_log,grep', '%s\t%s' % (script_nick, s))


### Log files and buffers ###
cache_dir = {} # note: don't remove, needed for completion if the script was loaded recently
def dir_list(dir, include_dir=False):
    """Returns a list of files in 'dir' and its subdirs."""
    global cache_dir
    #debug('dir_list: listing in %s' %dir)
    key = (dir, include_dir)
    try:
        return cache_dir[key]
    except KeyError:
        pass
    
    file_list = []
    for basedir, subdirs, files in os.walk(dir):
        if include_dir:
            subdirs = map(lambda s: os.path.join(s, ''), subdirs)
            files.extend(subdirs)
        files_path = map(lambda f: os.path.join(basedir, f), files)
        file_list.extend(files_path)

    cache_dir[key] = file_list
    #debug('dir_list: got %s' %str(file_list))
    return file_list

def get_file_by_pattern(pattern):
    """Returns all logs whose path matches <pattern>."""
    if not pattern: return []
    #debug('get_file_by_filename: searching for %s.' %pattern)
    # do envvar expandsion and check file
    file = path.expanduser(pattern)
    file = path.expandvars(file)
    if path.isfile(file):
        return [ file ]
    # lets see if there's a matching log
    files = []
    home_dir = get_home()
    file_list = dir_list(home_dir)
    n = len(home_dir)
    for log in file_list:
        basename = log[n:]
        if fnmatch(basename, pattern):
            files.append(log)
    #debug('get_file_by_filename: got %s.' %file)
    return files

def get_file_by_buffer(buffers):
    """Given a buffer pointer list, find their log's path."""
    #debug('get_file_by_buffer: searching for %s' %buffer)
    result = []
    infolist = weechat.infolist_get('logger_buffer', '', '')
    if not infolist: return result
    try:
        while weechat.infolist_next(infolist):
            pointer = weechat.infolist_pointer(infolist, 'buffer')
            if pointer in buffers:
                file = weechat.infolist_string(infolist, 'log_filename')
                if weechat.infolist_integer(infolist, 'log_enabled'):
                    #debug('get_file_by_buffer: got %s' %file)
                    result.append(file)
    finally:
        weechat.infolist_free(infolist)
    return result

def get_buffer_by_pattern(pattern):
    """Given a buffer name pattern, returns the pointers of matching buffers."""
    #debug('get_buffer_by_name: searching for %s' %buffer_name)
    result = []
    try:
        infolist = weechat.infolist_get('buffer', '', '')
        while weechat.infolist_next(infolist):
            buffer_name = weechat.infolist_string(infolist, 'full_name')
            if fnmatch(buffer_name, pattern):
                #debug('get_buffer_by_name: found %s' %name)
                pointer = weechat.buffer_search(*buffer_name.split('.', 1))
                result.append(pointer)
    finally:
        weechat.infolist_free(infolist)

    # don't search in grep buffer
    grep_buffer = weechat.buffer_search('python', SCRIPT_NAME)
    if grep_buffer and grep_buffer in result:
        # remove it from list
        del result[result.index(grep_buffer)]

    return result

### Grep ###
def make_regexp(pattern, matchcase=False):
    """Returns a compiled regexp."""
    if pattern in ('.', '.*', '.?', '.+'):
        # because I don't need to use a regexp if we're going to match all lines
        return None
    # matching takes a lot more time if pattern starts or ends with .* and it isn't needed.
    if pattern[:2] == '.*':
        pattern = pattern[2:]
    if pattern[-2:] == '.*':
        pattern = pattern[:-2]
    try:
        if not matchcase:
            regexp = re.compile(pattern, re.IGNORECASE)
        else:
            regexp = re.compile(pattern)
    except Exception, e:
        raise Exception, 'Bad pattern, %s' %e
    return regexp

def check_string(s, regexp, hilight='', exact=False):
    """Checks 's' with a regexp and returns it if is a match."""
    if not regexp:
        return s

    elif exact:
        matchlist = regexp.findall(s)
        if matchlist:
            if isinstance(matchlist[0], tuple):
                # join tuples (when there's more than one match group in regexp)
                return [ ' '.join(t) for t in matchlist ]
            return matchlist

    elif hilight:
        matchlist = regexp.findall(s)
        if matchlist:
            if isinstance(matchlist[0], tuple):
                # flatten matchlist
                matchlist = [ item for L in matchlist for item in L if item ]
            matchlist = list(set(matchlist)) # remove duplicates if any
            # apply hilight
            color_hilight, color_reset = hilight.split(',', 1)
            for m in matchlist:
                s = s.replace(m, '%s%s%s' % (color_hilight, m, color_reset))
            return s

    # no need for findall() here
    elif regexp.search(s):
        return s

def grep_file(file, head, tail, after_context, before_context, count, regexp,
              hilight, exact, invert):
    """Return a list of lines that match 'regexp' in 'file', if no regexp returns all lines."""

    lines = linesList()
    # define these locally as it makes the loop run slightly faster
    append = lines.append
    count_match = lines.count_match
    separator = lines.append_separator
    if invert:
        def check(s):
            if check_string(s, regexp, hilight, exact):
                return None
            else:
                return s
    else:
        check = lambda s: check_string(s, regexp, hilight, exact)
    
    try:
        file_object = open(file, 'r')
    except IOError:
        # file doesn't exist
        return lines
    if tail or before_context:
        # for these options, I need to seek in the file, but is slower and uses a good deal of
        # memory if the log is too big, so we do this *only* for these options.
        file_lines = file_object.readlines()

        if tail:
            # instead of searching in the whole file and later pick the last few lines, we
            # reverse the log, search until count reached and reverse it again, that way is a lot
            # faster
            file_lines.reverse()
            # don't invert context switches
            before_context, after_context = after_context, before_context

        if before_context:
            before_context_range = range(1, before_context + 1)
            before_context_range.reverse()

        limit = tail or head

        line_idx = 0
        while line_idx < len(file_lines):
            line = file_lines[line_idx]
            line = check(line)
            if line:
                if before_context:
                    separator()
                    trimmed = False
                    for id in before_context_range:
                        try:
                            context_line = file_lines[line_idx - id]
                            if check(context_line):
                                # match in before context, that means we appended these same lines in a
                                # previous match, so we delete them merging both paragraphs
                                if not trimmed:
                                    del lines[id - before_context - 1:]
                                    trimmed = True
                            else:
                                append(context_line)
                        except IndexError:
                            pass
                append(line)
                count_match(line)
                if after_context:
                    id, offset = 0, 0
                    while id < after_context + offset:
                        id += 1
                        try:
                            context_line = file_lines[line_idx + id]
                            _context_line = check(context_line)
                            if _context_line:
                                offset = id
                                context_line = _context_line # so match is hilighted with --hilight
                                count_match()
                            append(context_line)
                        except IndexError:
                            pass
                    separator()
                    line_idx += id
                if limit and lines.matches_count >= limit:
                    break
            line_idx += 1

        if tail:
            lines.reverse()
    else:
        # do a normal grep
        limit = head

        for line in file_object:
            line = check(line)
            if line:
                count or append(line)
                count_match(line)
                if after_context:
                    id, offset = 0, 0
                    while id < after_context + offset:
                        id += 1
                        try:
                            context_line = file_object.next()
                            _context_line = check(context_line)
                            if _context_line:
                                offset = id
                                context_line = _context_line
                                count_match()
                            count or append(context_line)
                        except StopIteration:
                            pass
                    separator()
                if limit and lines.matches_count >= limit:
                    break

    file_object.close()
    return lines

def grep_buffer(buffer, regexp):
    """Return a list of lines that match 'regexp' in 'buffer', if no regexp returns all lines."""
    lines = linesList()

    # Using /grep in grep's buffer can lead to some funny effects
    # We should take measures if that's the case
    def make_get_line_funcion():
        """Returns a function for get lines from the infolist, depending if the buffer is grep's or
        not."""
        string_remove_color = weechat.string_remove_color
        infolist_string = weechat.infolist_string
        grep_buffer = weechat.buffer_search('python', SCRIPT_NAME)
        if grep_buffer and buffer == grep_buffer:
            def function(infolist):
                tags = infolist_string(infolist, 'tags')
                if 'grep' in tags:
                    return None
                prefix = infolist_string(infolist, 'prefix')
                message = infolist_string(infolist, 'message')
                if prefix: # only our messages have prefix, ignore it
                    return None
                return message
        else:
            infolist_time = weechat.infolist_time
            def function(infolist):
                tags = infolist_string(infolist, 'tags')
                if 'grep' in tags:
                    return None
                prefix = string_remove_color(infolist_string(infolist, 'prefix'), '')
                message = string_remove_color(infolist_string(infolist, 'message'), '')
                date = infolist_time(infolist, 'date')
                return '%s\t%s\t%s' %(date, prefix, message)
        return function
    get_line = make_get_line_funcion()

    infolist = weechat.infolist_get('buffer_lines', buffer, '')
    if options.tail:
        # like with grep_file() if we need the last few matching lines, we move the cursor to
        # the end and search backwards
        infolist_next = weechat.infolist_prev
        infolist_prev = weechat.infolist_next
    else:
        infolist_next = weechat.infolist_next
        infolist_prev = weechat.infolist_prev
    limit = options.head or options.tail

    # define these locally as it makes the loop run slightly faster
    append = lines.append
    count_match = lines.count_match
    separator = lines.append_separator
    if options.invert:
        def check(s):
            if check_string(s, regexp, options.hilight, options.exact):
                return None
            else:
                return s
    else:
        check = lambda s: check_string(s, regexp, options.hilight, options.exact)

    if options.before_context:
        before_context_range = range(1, options.before_context + 1)
        before_context_range.reverse()

    while infolist_next(infolist):
        line = get_line(infolist)
        if line is None: continue
        line = check(line)
        if line:
            if options.before_context:
                separator()
                trimmed = False
                for id in before_context_range:
                    if not infolist_prev(infolist):
                        trimmed = True
                for id in before_context_range:
                    context_line = get_line(infolist)
                    if check(context_line):
                        if not trimmed:
                            del lines[id - before_context - 1:]
                            trimmed = True
                    else:
                        append(context_line)
                    infolist_next(infolist)
            options.count or append(line)
            count_match(line)
            if options.after_context:
                id, offset = 0, 0
                while id < options.after_context + offset:
                    id += 1
                    if infolist_next(infolist):
                        context_line = get_line(infolist)
                        _context_line = check(context_line)
                        if _context_line:
                            context_line = _context_line
                            offset = id
                            count_match()
                        append(context_line)
                    else:
                        # in the main loop infolist_next will start again an cause an infinite loop
                        # this will avoid it
                        infolist_next = lambda x: 0
                separator()
            if limit and lines.matches_count >= limit:
                break
    weechat.infolist_free(infolist)

    if options.tail:
        lines.reverse()
    return lines

### this is our main grep function
hook_file_grep = None
def show_matching_lines():
    """
    Greps buffers in search_in_buffers or files in search_in_files and updates grep buffer with the
    result.
    """
    global search_in_files, search_in_buffers, matched_lines
    global time_start
    matched_lines = linesDict()
    #debug('buffers:%s \nlogs:%s' %(search_in_buffers, search_in_files))
    time_start = now()

    # buffers
    if search_in_buffers:
        regexp = make_regexp(options.pattern, options.matchcase) # XXX move in GrepOptions
        for buffer in search_in_buffers:
            buffer_name = weechat.buffer_get_string(buffer, 'full_name')
            matched_lines[buffer_name] = grep_buffer(buffer, regexp)

    # logs
    if search_in_files:
        size_limit = get_config_int('size_limit', allow_empty_string=True)
        background = False
        if size_limit or size_limit == 0:
            size = sum(map(get_size, search_in_files))
            if size > size_limit * 1024:
                background = True
        elif size_limit == '':
            background = False

        if not background:
            # run grep normally
            regexp = make_regexp(options.pattern, options.matchcase)
            for log in search_in_files:
                log_name = strip_home(log)
                matched_lines[log_name] = grep_file(log, options.head, 
                                                    options.tail, 
                                                    options.after_context,
                                                    options.before_context,
                                                    options.count, 
                                                    regexp, 
                                                    options.hilight, 
                                                    options.exact, 
                                                    options.invert)
            buffer_update()
        else:
            # we hook a process so grepping runs in background.
            #debug('on background')
            global hook_file_grep, script_path, bytecode
            timeout = 1000*60*5 # 5 min

            quotify = lambda s: '"%s"' %s
            files_string = ', '.join(map(quotify, search_in_files))

            global tmpFile
            # we keep the file descriptor as a global var so it isn't deleted until next grep
            tmpFile = tempfile.NamedTemporaryFile(prefix=SCRIPT_NAME,
                    dir=weechat.info_get('weechat_dir', ''))
            args = dict(logs=files_string,
                        home_dir=get_home(),
                        script_path=script_path,
                        bytecode=bytecode,
                        filename=tmpFile.name,
                        python=weechat.info_get('python2_bin', '') or 'python')
            args.update(options._options)
            args['tail'] = options.tail
            args['head'] = options.head
            cmd = grep_process_cmd % args

            debug(args)
            debug(cmd)
            hook_file_grep = weechat.hook_process(cmd, timeout, 'grep_file_callback', tmpFile.name)
            if hook_file_grep:
                buffer_create("Searching for '%s' in %s worth of data..." % (options.pattern_tmpl,
                                                                             human_readable_size(size)))
    else:
        buffer_update()

# defined here for commodity
grep_process_cmd = """%(python)s -%(bytecode)sc '
import sys, cPickle, os
sys.path.append("%(script_path)s") # add WeeChat script dir so we can import grep
from grep import make_regexp, grep_file, strip_home
logs = (%(logs)s, )
try:
    regexp = make_regexp("%(pattern)s", %(matchcase)s)
    d = {}
    for log in logs:
        log_name = strip_home(log, "%(home_dir)s")
        lines = grep_file(log, %(head)s, %(tail)s, %(after_context)s, %(before_context)s,
        %(count)s, regexp, "%(hilight)s", %(exact)s, %(invert)s)
        d[log_name] = lines
    fd = open("%(filename)s", "wb")
    cPickle.dump(d, fd, -1)
    fd.close()
except Exception, e:
    print >> sys.stderr, e'
"""

grep_stdout = grep_stderr = ''
def grep_file_callback(filename, command, rc, stdout, stderr):
    global hook_file_grep, grep_stderr,  grep_stdout
    global matched_lines
    #debug("rc: %s\nstderr: %s\nstdout: %s" %(rc, repr(stderr), repr(stdout)))
    if stdout:
        grep_stdout += stdout
    if stderr:
        grep_stderr += stderr
    if int(rc) >= 0:
  
        def set_buffer_error():
            grep_buffer = buffer_create()
            title = weechat.buffer_get_string(grep_buffer, 'title')
            title = title + ' %serror' %color_title
            weechat.buffer_set(grep_buffer, 'title', title)

        try:
            if grep_stderr:
                error(grep_stderr)
                set_buffer_error()
            #elif grep_stdout:
                #debug(grep_stdout)
            elif path.exists(filename):
                import cPickle
                try:
                    #debug(file)
                    fd = open(filename, 'rb')
                    d = cPickle.load(fd)
                    matched_lines.update(d)
                    fd.close()
                except Exception, e:
                    error(e)
                    set_buffer_error()
                else:
                    buffer_update()
            global tmpFile
            tmpFile = None
        finally:
            grep_stdout = grep_stderr = ''
            hook_file_grep = None
    return WEECHAT_RC_OK

def get_grep_file_status():
    global search_in_files, matched_lines, time_start
    elapsed = now() - time_start
    if len(search_in_files) == 1:
        log = '%s (%s)' %(strip_home(search_in_files[0]),
                human_readable_size(get_size(search_in_files[0])))
    else:
        size = sum(map(get_size, search_in_files))
        log = '%s log files (%s)' %(len(search_in_files), human_readable_size(size))
    return 'Searching in %s, running for %.4f seconds. Interrupt it with "/grep stop" or "stop"' \
        ' in grep buffer.' %(log, elapsed)

### Grep buffer ###
def buffer_update():
    """Updates our buffer with new lines."""
    global matched_lines
    time_grep = now()

    buffer = buffer_create()
    if get_config_boolean('clear_buffer'):
        weechat.buffer_clear(buffer)
    matched_lines.strip_separator() # remove first and last separators of each list
    len_total_lines = len(matched_lines)
    max_lines = get_config_int('max_lines')
    if not options.count and len_total_lines > max_lines:
        weechat.buffer_clear(buffer)

    def _make_summary(log, lines, note):
        return '%s matches "%s%s%s"%s in %s%s%s%s' % (lines.matches_count, 
                                                      color_summary,
                                                      options.pattern_tmpl,
                                                      color_info,
                                                      options.invert and ' (inverted)' or '',
                                                      color_summary,
                                                      log, color_reset, note)

    if options.count:
        make_summary = lambda log, lines : _make_summary(log, lines, ' (not shown)')
    else:
        def make_summary(log, lines):
            if lines.stripped_lines:
                if lines:
                    note = ' (last %s lines shown)' % len(lines)
                else:
                    note = ' (not shown)'
            else:
                note = ''
            return _make_summary(log, lines, note)

    global weechat_format
    if options.hilight:
        # we don't want colors if there's match highlighting
        format_line = lambda s : '%s %s %s' % split_line(s)
    else:
        def format_line(s):
            global nick_dict, weechat_format
            date, nick, msg = split_line(s)
            if weechat_format:
                try:
                    nick = nick_dict[nick]
                except KeyError:
                    # cache nick
                    nick_c = color_nick(nick)
                    nick_dict[nick] = nick_c
                    nick = nick_c
                return '%s%s %s%s %s' % (color_date, date, nick, color_reset, msg)
            else:
                #no formatting
                return msg

    prnt(buffer, '\n')
    print_line('Search for "%s%s%s"%s in %s%s%s.' % (color_summary,
                                                     options.pattern_tmpl,
                                                     color_info,
                                                     options.invert and ' (inverted)' or '',
                                                     color_summary, 
                                                     matched_lines,
                                                     color_reset),
            buffer)
    # print last <max_lines> lines
    if matched_lines.get_matches_count():
        if options.count:
            # with count we sort by matches lines instead of just lines.
            matched_lines_items = matched_lines.items_count()
        else:
            matched_lines_items = matched_lines.items()

        matched_lines.get_last_lines(max_lines)
        for log, lines in matched_lines_items:
            if lines.matches_count:
                # matched lines
                if not options.count:
                    # print lines
                    weechat_format = True
                    if options.exact:
                        lines.onlyUniq()
                    for line in lines:
                        #debug(repr(line))
                        if line == linesList._sep:
                            # separator
                            prnt(buffer, context_sep)
                        else:
                            if '\x00' in line:
                                # log was corrupted
                                error("Found garbage in log '%s', maybe it's corrupted" % log)
                                line = line.replace('\x00', '')
                            prnt_date_tags(buffer, 0, 'no_highlight', format_line(line))

                # summary
                if options.count or get_config_boolean('show_summary'):
                    summary = make_summary(log, lines)
                    print_line(summary, buffer)

            # separator
            if not options.count and lines:
                prnt(buffer, '\n')
    else:
        print_line('No matches found.', buffer)

    # set title
    global time_start
    time_end = now()
    # total time
    time_total = time_end - time_start
    # percent of the total time used for grepping
    time_grep_pct = (time_grep - time_start)/time_total*100
    #debug('time: %.4f seconds (%.2f%%)' %(time_total, time_grep_pct))
    if not options.count and len_total_lines > max_lines:
        note = ' (last %s lines shown)' % len(matched_lines)
    else:
        note = ''
    title = "Search in %s%s%s %s matches%s | pattern \"%s%s%s\"%s %s | %.4f seconds (%.2f%%)" \
                % (color_title, matched_lines, color_reset,
                   matched_lines.get_matches_count(), note,
                   color_title, options.pattern_tmpl, color_reset,
                   options.invert and ' (inverted)' or '',
                   format_options(), time_total, time_grep_pct)
    weechat.buffer_set(buffer, 'title', title)

    if get_config_boolean('go_to_buffer'):
        weechat.buffer_set(buffer, 'display', '1')

    # free matched_lines so it can be removed from memory
    del matched_lines
    
def split_line(s):
    """Splits log's line 's' in 3 parts, date, nick and msg."""
    global weechat_format
    if weechat_format and s.count('\t') >= 2:
        date, nick, msg = s.split('\t', 2) # date, nick, message
    else:
        # looks like log isn't in weechat's format
        weechat_format = False # incoming lines won't be formatted
        date, nick, msg = '', '', s
    # remove tabs
    if '\t' in msg:
        msg = msg.replace('\t', '    ')
    return date, nick, msg

def print_line(s, buffer=None, display=False):
    """Prints 's' in script's buffer as 'script_nick'. For displaying search summaries."""
    if buffer is None:
        buffer = buffer_create()
    say('%s%s' %(color_info, s), buffer)
    if display and get_config_boolean('go_to_buffer'):
        weechat.buffer_set(buffer, 'display', '1')

def format_options():
    opts = []
    append = opts.append
    insert = opts.insert
    chars = 'cHmov'
    for i, flag in enumerate((options.count,
                              options.hilight,
                              options.matchcase,
                              options.exact,
                              options.invert)):
        if flag:
            append(chars[i])

    n = get_config_int('default_tail_head')
    if options.head:
        append('h')
        if options.head != n:
            insert(-1, ' -')
            append('n')
            append(options.head)
    elif options.tail:
        append('t')
        if options.tail != n:
            insert(-1, ' -')
            append('n')
            append(options.tail)

    if options.before_context and options.after_context \
            and (options.before_context == options.after_context):
        append(' -C')
        append(options.before_context)
    else:
        if options.before_context:
            append(' -B')
            append(options.before_context)
        if options.after_context:
            append(' -A')
            append(options.after_context)

    s = ''.join(map(str, opts)).strip()
    if s and s[0] != '-':
        s = '-' + s
    return s

def buffer_create(title=None):
    """Returns our buffer pointer, creates and cleans the buffer if needed."""
    buffer = weechat.buffer_search('python', SCRIPT_NAME)
    if not buffer:
        buffer = weechat.buffer_new(SCRIPT_NAME, 'buffer_input', '', '', '')
        weechat.buffer_set(buffer, 'time_for_each_line', '0')
        weechat.buffer_set(buffer, 'nicklist', '0')
        weechat.buffer_set(buffer, 'title', title or 'grep output buffer')
        weechat.buffer_set(buffer, 'localvar_set_no_log', '1')
    elif title:
        weechat.buffer_set(buffer, 'title', title)
    return buffer

def buffer_input(data, buffer, input_data):
    """Repeats last search with 'input_data' as regexp."""
    try:
        cmd_grep_stop(buffer, input_data)
    except:
        return WEECHAT_RC_OK

    global search_in_buffers, search_in_files
    try:
        if options.pattern and (search_in_files or search_in_buffers):
            # check if the buffer pointers are still valid
            for pointer in search_in_buffers:
                infolist = weechat.infolist_get('buffer', pointer, '')
                if not infolist:
                    del search_in_buffers[search_in_buffers.index(pointer)]
                weechat.infolist_free(infolist)
            try:
                cmd_grep_parsing(input_data)
            except Exception, e:
                error('Argument error, %s' %e, buffer=buffer)
                return WEECHAT_RC_OK
            try:
                show_matching_lines()
            except Exception, e:
                error(e)
    except NameError:
        error("There isn't any previous search to repeat.", buffer=buffer)
    return WEECHAT_RC_OK

### Commands ###
def cmd_init():
    """Resets global vars."""
    global cache_dir, nick_dict
    cache_dir = {} # for avoid walking the dir tree more than once per command
    nick_dict = {} # nick cache for don't calculate nick color every time

def cmd_grep_parsing(args):
    """Parses args for /grep and grep input buffer."""
    global log_name, buffer_name
    opts, args = getopt.gnu_getopt(args.split(), 'cmHehtivn:A:B:C:o',
                                   [ 'count', 'matchcase', 'hilight', 'exact', 'head', 'tail',
                                     'number=', 'after-context=', 'before-context=', 'context=',
                                     'invert', 'only-match'])
    #debug(opts, 'opts: '); debug(args, 'args: ')
    if len(args) >= 2:
        if args[0] == 'log':
            del args[0]
            log_name = args.pop(0)
        elif args[0] == 'buffer':
            del args[0]
            buffer_name = args.pop(0)

    def tmplReplacer(match):
        """This function will replace templates with regexps"""
        s = match.groups()[0]
        tmpl_args = s.split()
        tmpl_key, _, tmpl_args = s.partition(' ')
        try:
            template = templates[tmpl_key]
            if callable(template):
                r = template(tmpl_args)
                if not r:
                    error("Template %s returned empty string "\
                          "(WeeChat doesn't have enough data)." %t)
                return r
            else:
                return template
        except:
            return t

    args = ' '.join(args) # join pattern for keep spaces
    if args:
        options.pattern_tmpl = args  
        options.pattern = _tmplRe.sub(tmplReplacer, args)
        debug('Using regexp: %s', options.pattern)
    if not options.pattern:
        raise Exception, 'No pattern for grep the logs.'

    def toggle(name):
        setattr(options, name, not getattr(options, name))

    for opt, val in opts:
        opt = opt.strip('-')
        if opt in ('c', 'count'):
            toggle('count')
        elif opt in ('m', 'matchcase'):
            toggle('matchcase')
        elif opt in ('H', 'hilight'):
            # hilight must be always a string!
            if options.hilight:
                options.hilight = ''
            else:
                options.hilight = '%s,%s' %(color_hilight, color_reset)
            # we pass the colors in the variable itself because check_string() must not use
            # weechat's module when applying the colors (this is for grep in a hooked process)
        elif opt in ('e', 'exact', 'o', 'only-match'):
            toggle('exact')
        elif opt in ('h', 'head'):
            toggle('head')
        elif opt in ('t', 'tail'):
            toggle('tail')
        elif opt in ('n', 'number'):
            options.number = val
        elif opt in ('C', 'context'):
            options.after_context = val
            options.before_context = val
        elif opt in ('A', 'after-context'):
            options.after_context = val
        elif opt in ('B', 'before-context'):
            options.before_context = val
        elif opt in ('i', 'v', 'invert'):
            toggle('invert')

def cmd_grep_stop(buffer, args):
    global hook_file_grep, matched_lines, tmpFile
    if hook_file_grep:
        if args == 'stop':
            weechat.unhook(hook_file_grep)
            hook_file_grep = None
            s = 'Search for \'%s\' stopped.' % options.pattern
            say(s, buffer)
            grep_buffer = weechat.buffer_search('python', SCRIPT_NAME)
            if grep_buffer:
                weechat.buffer_set(grep_buffer, 'title', s)
            del matched_lines
            tmpFile = None
        else:
            say(get_grep_file_status(), buffer)
        raise Exception

def cmd_grep(data, buffer, args):
    """Search in buffers and logs."""
    try:
        cmd_grep_stop(buffer, args)
    except:
        return WEECHAT_RC_OK

    if not args:
        weechat.command('', '/help %s' %SCRIPT_COMMAND)
        return WEECHAT_RC_OK

    cmd_init()
    options.reset()
    global log_name, buffer_name
    log_name = buffer_name = ''

    # parse
    try:
        cmd_grep_parsing(args)
    except Exception, e:
        error('Argument error, %s' %e)
        return WEECHAT_RC_OK

    # find logs or buffers
    global search_in_files, search_in_buffers
    search_in_files = search_in_buffers = []
    if log_name:
        search_in_files = get_file_by_pattern(log_name)
        if not search_in_files:
            error("Couldn't find any log for %s. Try /logs" % log_name)
            return WEECHAT_RC_OK
    elif buffer_name:
        search_in_buffers = get_buffer_by_pattern(buffer_name)
        if not search_in_buffers:
            error("Couldn't find any buffer for %s." % buffer_name)
            return WEECHAT_RC_OK
    else:
        # search current buffer's log
        search_in_files = get_file_by_buffer([ buffer ])
        if not search_in_files:
            search_in_buffers = [ buffer ]

    # grepping
    try:
        show_matching_lines()
    except Exception, e:
        error(e)
    return WEECHAT_RC_OK

def cmd_logs(data, buffer, args):
    """List files in Weechat's log dir."""
    cmd_init()
    sort_by_size = False
    pattern = None

    try:
        opts, args = getopt.gnu_getopt(args.split(), 's', ['size'])
        if args:
            pattern = args[0]
        for opt, var in opts:
            opt = opt.strip('-')
            if opt in ('size', 's'):
                sort_by_size = True
    except Exception, e:
        error('Argument error, %s' %e)
        return WEECHAT_RC_OK

    home_dir = get_home()
    file_list = dir_list(home_dir)
    if pattern:
        home_len = len(home_dir)
        def match(file):
            file = file[home_len:] # pattern shouldn't match home dir
            if fnmatch(file, pattern):
                return True
            return False
        
        file_list = filter(match, file_list)

    if sort_by_size:
        file_list.sort(key=get_size)
    else:
        file_list.sort()

    file_sizes = map(lambda x: human_readable_size(get_size(x)), file_list)
    # calculate column lenght
    if file_list:
        L = file_list[:]
        L.sort(key=len)
        bigest = L[-1]
        column_len = len(bigest) + 3
    else:
        column_len = ''

    buffer = buffer_create()
    if get_config_boolean('clear_buffer'):
        weechat.buffer_clear(buffer)
    file_list = zip(file_list, file_sizes)
    msg = 'Found %s logs.' %len(file_list)

    print_line(msg, buffer, display=True)
    for file, size in file_list:
        separator = column_len and '.'*(column_len - len(file))
        prnt(buffer, '%s %s %s' %(strip_home(file), separator, size))
    if file_list:
        print_line(msg, buffer)
    return WEECHAT_RC_OK

def cmd_lastlog(data, buffer, args):
    # XXX no pattern templates
    # FIXME no help
    # FIXME lacks features present in /grep, like --hilight --matchcase
    pattern = args
    nick_dict = {}
    # XXX make it configurable.
    max_lines = 100

    def format_line(s):
        date, nick, msg = s.split('\t', 2) # date, nick, message
        if '\t' in msg:
            msg = msg.replace('\t', '    ')
        try:
            nick = nick_dict[nick]
        except KeyError:
            # cache nick
            nick_c = color_nick(nick)
            nick_dict[nick] = nick_c
            nick = nick_c
        return date, '%s%s\t%s' % (nick, color_reset, msg)

    try:
        matched_lines = []
        regexp = make_regexp(pattern)
        infolist = weechat.infolist_get('buffer_lines', buffer, '')
        while weechat.infolist_next(infolist):
            tags = weechat.infolist_string(infolist, 'tags')
            if 'grep' in tags:
                continue

            prefix = weechat.infolist_string(infolist, 'prefix') 
            message = weechat.infolist_string(infolist, 'message')
            line = "%s\t%s" % (prefix, message)
            line_nocolor = weechat.string_remove_color(line, '')
            if check_string(line_nocolor, regexp):
                date = weechat.infolist_time(infolist, 'date')
                date = time.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = int(time.mktime(date))
                matched_lines.append((date, line))
        weechat.infolist_free(infolist)

        if matched_lines:
            if len(matched_lines) > max_lines:
                say("%sMore than %s matches, use /grep instead." % (weechat.color('white'),
                                                                    max_lines),
                                                                    buffer)
                return WEECHAT_RC_OK

            say("%sLastlog for \"%s\":" % (weechat.color('white'), pattern), buffer)
            for date, line in matched_lines:
                prnt_date_tags(buffer, date, 'no_highlight,no_log,grep', line)
            say("%sEnd of Lastlog, %s matches." % (weechat.color('white'),
                                                   len(matched_lines)),
                                                   buffer)
        else:
            say("%sNothing found with \"%s\"." % (weechat.color('white'), pattern), buffer)
    except Exception, e:
        error(e, buffer)
    return WEECHAT_RC_OK

### Completion ###
def completion_log_files(data, completion_item, buffer, completion):
    home_dir = get_home()
    home_dir_len = len(home_dir)
    for log in dir_list(home_dir, include_dir=True):
        log = log[home_dir_len:] # strip home dir
        weechat.hook_completion_list_add(completion, log, 0, weechat.WEECHAT_LIST_POS_END)
    return WEECHAT_RC_OK

def completion_grep_args(data, completion_item, buffer, completion):
    for arg in ('count', 'matchcase', 'hilight', 'exact', 'head', 'tail', 'number',
            'after-context', 'before-context', 'context', 'invert', 'only-match'):
        weechat.hook_completion_list_add(completion, '--' + arg, 0, weechat.WEECHAT_LIST_POS_SORT)
    for tmpl in templates:
        weechat.hook_completion_list_add(completion, '%{' + tmpl, 0, weechat.WEECHAT_LIST_POS_SORT)
    return WEECHAT_RC_OK


### Templates ###
# template placeholder
_tmplRe = re.compile(r'%\{(\w+.*?)(?:\}|$)')
# will match 999.999.999.999 but I don't care
ipAddress = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
domain = r'[\w-]{2,}(?:\.[\w-]{2,})*\.[a-z]{2,}'
url = r'\w+://(?:%s|%s)(?::\d+)?(?:/[^\])>\s]*)?' % (domain, ipAddress)

def make_url_regexp(args):
    #debug('make url: %s', args)
    if args:
        words = r'(?:%s)' %'|'.join(map(re.escape, args.split()))
        return r'(?:\w+://|www\.)[^\s]*%s[^\s]*(?:/[^\])>\s]*)?' %words
    else:
        return url

def make_simple_regexp(pattern):
    s = ''
    for c in pattern:
        if c == '*':
            s += '.*'
        elif c == '?':
            s += '.'
        else:
            s += re.escape(c)
    return s

templates = {
            'ip': ipAddress,
           'url': make_url_regexp,
        'escape': lambda s: re.escape(s),
        'simple': make_simple_regexp,
        'domain': domain,
        }

### Main ###
def delete_bytecode():
    global script_path
    bytecode = path.join(script_path, SCRIPT_NAME + '.pyc')
    if path.isfile(bytecode):
        os.remove(bytecode)
    return WEECHAT_RC_OK

if __name__ == '__main__' and import_ok and \
        weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, \
        SCRIPT_DESC, 'delete_bytecode', ''):

    # for import ourselves
    global script_path
    script_path = path.dirname(__file__)
    sys.path.append(script_path)
    delete_bytecode()

    # check python version
    import sys
    global bytecode
    if sys.version_info > (2, 6):
        bytecode = 'B'
    else:
        bytecode = ''


    weechat.hook_command(SCRIPT_COMMAND, cmd_grep.__doc__,
            "log <pattern> [<options>] <expression> || buffer <pattern> [<options>] <expression> || stop",
# help
"""
Grep by default will search in current buffer's log, you can use
   log: Search in log files. The search will be done in the logs that matches <pattern>. Use '*' and '?' as wildcards.
buffer: Search in buffers. The search will be done in the buffers that matches <pattern>. Use '*' and '?' as wildcards.
  stop: Stops a currently running search.

Grep options:
     -c --count: Just count the number of matched lines instead of showing them.
 -m --matchcase: Don't do case insensible search.
   -H --hilight: Colour exact matches in output buffer.
-o --only-match: Print only the matching part of the line (unique matches).
 -v -i --invert: Print lines that don't match the regular expression.
      -t --tail: Print the last 10 matching lines.
      -h --head: Print the first 10 matching lines.
-n --number <n>: Overrides default number of lines for --tail or --head.
-A --after-context <n>: Shows <n> lines of trailing context after matching lines.
-B --before-context <n>: Shows <n> lines of leading context before matching lines.
-C --context <n>: Same as using both --after-context and --before-context simultaneously.
  <expression>: Expression to search.

Grep buffer:
  Input line accepts most arguemnts of /grep, it'll repeat last search using the new
  arguments provided. You can't search in different logs from the buffer's input.
  Boolean arguments like --count, --tail, --head, --hilight, ... are toggleable

Python regular expression syntax:
  See http://docs.python.org/lib/re-syntax.html

Grep Templates:
     %{url [text]}: Matches anything like an url, or an url with text.
             %{ip}: Matches anything that looks like an ip.
         %{domain}: Matches anything like a domain.
    %{escape text}: Escapes text in pattern.
 %{simple pattern}: Converts a pattern with '*' and '?' wildcards into a regexp.

Examples:
  Search for urls with the word 'weechat' said by 'nick'
    /grep nick\\t.*%{url weechat}
  Search for '*.*' string
    /grep %{escape *.*}
""",
            # completion template
            "buffer %(buffers_plugins_names) %(grep_arguments)|%*"
            "||log %(grep_log_files) %(grep_arguments)|%*"
            "||stop"
            "||%(grep_arguments)|%*",
            'cmd_grep' ,'')
    weechat.hook_command('logs', cmd_logs.__doc__, "[-s|--size] [<pattern>]",
            "-s --size: Sort logs by size.\n"
            " <pattern>: Only show logs that match <pattern>. Use '*' and '?' as wildcards.",
            '--size', 'cmd_logs', '')
    weechat.hook_command('lastlog', "", "", "", "", 'cmd_lastlog', '')

    weechat.hook_completion('grep_log_files', "list of log files",
            'completion_log_files', '')
    weechat.hook_completion('grep_arguments', "list of arguments",
            'completion_grep_args', '')

    # settings
    for opt, val in settings.iteritems():
        if not weechat.config_is_set_plugin(opt):
            weechat.config_set_plugin(opt, val)

    # colors
    color_date        = weechat.color('brown')
    color_info        = weechat.color('cyan')
    color_hilight     = weechat.color('lightred')
    color_reset       = weechat.color('reset')
    color_title       = weechat.color('yellow')
    color_summary     = weechat.color('lightcyan')
    color_delimiter   = weechat.color('chat_delimiters')
    color_script_nick = weechat.color('chat_nick')
    
    # pretty [grep]
    script_nick = '%s[%s%s%s]%s' %(color_delimiter, color_script_nick, SCRIPT_NAME, color_delimiter,
            color_reset)
    script_nick_nocolor = '[%s]' %SCRIPT_NAME
    # paragraph separator when using context options
    context_sep = '%s\t%s--' %(script_nick, color_info)

    # -------------------------------------------------------------------------
    # Debug

    if weechat.config_get_plugin('debug'):
        try:
            # custom debug module I use, allows me to inspect script's objects.
            import pybuffer
            debug = pybuffer.debugBuffer(globals(), '%s_debug' % SCRIPT_NAME)
        except:
            def debug(s, *args):
                if not isinstance(s, basestring):
                    s = str(s)
                if args:
                    s = s %args
                prnt('', '%s\t%s' %(script_nick, s))
    else:
        def debug(*args):
            pass

# vim:set shiftwidth=4 tabstop=4 softtabstop=4 expandtab textwidth=100:

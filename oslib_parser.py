#!/usr/bin/env python
"""
Parse an OSLib definition file, and generate API and module definitions.
"""

import argparse
import datetime
import functools
import math
import os
import re
import sys
import time


# Whether we debug the parser
debug = False


def open_ro(*args):
    try:
        # Python 3 format
        return open(*args, encoding='latin-1')
    except TypeError:
        # Python 2, which will just be bytes
        return open(*args)


class ParseError(Exception):

    def __init__(self, message, lineno=None):
        self.lineno = lineno
        super(ParseError, self).__init__(message)

    def __str__(self):
        if self.lineno:
            return "{} whilst processing line number {}".format(self.args[0], self.lineno)
        return self.args


class Union(object):

    def __init__(self, name=None):
        self.name = name
        self.members = []

    def add_member(self, dtype):
        self.members.append(dtype)

    def __repr__(self):
        return "<{}({}, members: {})>".format(self.__class__.__name__,
                                              self.name,
                                              ', '.join(str(x) for x in self.members))


class Array(object):

    def __init__(self, dtype, elements):
        self.dtype = dtype
        self.nelements = elements

    def __repr__(self):
        return "<{}({} x {})>".format(self.__class__.__name__,
                                      self.nelements,
                                      self.dtype)


class Struct(object):

    def __init__(self, name=None):
        self.name = name
        self.members = []

    def __repr__(self):
        return "<{}({}, members: {})>".format(self.__class__.__name__,
                                              self.name,
                                              ', '.join(str(x) for x in self.members))

    def add_member(self, dtype):
        self.members.append(dtype)


class Member(object):

    def __init__(self, dtype, name, array=None):
        self.dtype = dtype
        self.name = name
        self.array = array

    def __repr__(self):
        return "<{}({} {}, array: {})>".format(self.__class__.__name__,
                                               self.dtype,
                                               self.name,
                                               self.array)


@functools.total_ordering
class Constant(object):

    def __init__(self, name, dtype, value):
        self.name = name
        self.dtype = dtype
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, Constant):
            return NotImplemented
        a = self.value
        b = other.value
        if isinstance(a, list):
            a = a[0]
        if isinstance(b, list):
            b = b[0]
        return a < b


class Register(object):

    def __init__(self, reg, assign, dtype, name, update=False, corrupted=False):
        self.reg = reg
        self.assign = assign
        self.dtype = dtype
        self.name = name
        self.update = update
        self.corrupted = corrupted

    def copy(self):
        return Register(self.reg,
                        self.assign,
                        self.dtype,
                        self.name,
                        self.update,
                        self.corrupted)

    def __repr__(self):
        return "<Register(%s %s %s: %s)>" % (self.reg, self.assign, self.dtype, self.name)


class SWI(object):

    def __init__(self, name):
        self.name = name
        self.number = None
        self.description = None
        self.starred = False
        self.hidden = False
        # When hidden, the entry and exit parameters are not valid
        self.entry = []
        self.exit = []

    def __repr__(self):
        if self.hidden:
            args = 'hidden'
        else:
            args = '%s entry, %s exit' % (len(self.entry), len(self.exit))
        return "<SWI(&%x %s, %s)>" % (0xFFFFFF if self.number is None else self.number,
                                      self.name,
                                      args)

    def add_entry(self, reg):
        self.entry.append(reg)
        # Create a dictionary of the registers as well?

    def add_exit(self, reg):
        self.exit.append(reg)
        # Create a dictionary of the registers as well?

    def inregs(self):
        inregs = {}
        nreg = 0
        lastreg = None
        for reg in self.entry:
            if reg.reg[0] == 'R':
                if reg.assign == '#':
                    # This is a constant, which we can do last
                    if -1 not in inregs:
                        inregs[-1] = []
                    inregs[-1].append(reg)
                else:
                    if reg.assign == '|':
                        if lastreg and lastreg.assign == '#' and lastreg.reg == reg.reg:
                            reg = reg.copy()
                            reg.assign = '='
                            lastreg = lastreg.copy()
                            lastreg.assign = '|'
                            inregs[-1][-1] = lastreg
                    if nreg not in inregs:
                        inregs[nreg] = []
                    inregs[nreg].append(reg)
                    nreg += 1
                lastreg = reg

        if self.name.lower() == 'osmemory_pageop':
            print("%r" % (inregs,))
        return inregs

    def outregs(self):
        outregs = {}
        nreg = len([reg for reg in self.inregs() if reg != -1])
        for reg in self.exit:
            if reg.reg[0] == 'R' and reg.assign != '?':
                outregs[nreg] = reg
                nreg += 1
        return outregs


class DefMod(object):

    def __init__(self, name, modname=None, inctype='required'):
        modname = modname.lower()
        if name.endswith('.Swi') or name.endswith('/Swi'):
            name = name[:-4]
        if modname.endswith('.swi') or modname.endswith('/swi'):
            modname = modname[:-4]
        self.name = name
        self.modname = modname or self.name
        self.inctype = inctype
        self.constants =  {}
        self.title = None
        self.types = {}
        self.needs = []
        self.types = {}
        self.swis = {}
        self.interfaces = {}
        # Special cases of swis (the entries are also in SWIs):
        self.vectors = {}
        self.services = {}
        self.events = {}
        self.upcalls = {}

    def __repr__(self):
        return "<DefMod(%r, %i constants)>" % (self.title, len(self.constants))

    def add_constant(self, const):
        if const.name in self.constants:
            print("Redefinition of constant '%s'" % (const.name,))
        self.constants[const.name] = const

    def add_need(self, need):
        if need in self.needs:
            print("Duplicate requirement of '%s'" % (need,))
        self.needs.append(need)
        # FIXME: Parse another DefMod file?
        # Apparently defmod parser won't actually process any 'Need' directives beyond
        # providing them as includes of types.

    def add_type(self, name, dtype):
        if name in self.types:
            print("Duplicate type of '%s'" % (name,))
        self.types[name] = dtype

    def add_swi(self, swi):
        if swi.name in self.interfaces:
            print("Redefinition of SWI %x : %r / %r" % (swi.number, swi, self.interfaces[swi.name]))
        self.interfaces[swi.name] = swi

        if swi.name.startswith("Service_"):
            swilist = self.services
            swi.name = "OS_ServiceCall_" + swi.name[8:]
        elif swi.name.startswith("Event_"):
            swilist = self.events
            swi.name = "OS_Generate" + swi.name
        elif swi.name.startswith("UpCall_"):
            swi.name = "OS_" + swi.name
            swilist = self.upcalls
        elif swi.name.endswith("V") and "_" not in swi.name:
            swi.name = "OS_CallVector_" + swi.name
            swilist = self.vectors
        else:
            swilist = self.swis

        if swi.number in swilist:
            swilist[swi.number].append(swi)
        else:
            swilist[swi.number] = [swi]
        if swilist is not self.swis:
            swilist = self.swis
            if swi.number in swilist:
                swilist[swi.number].append(swi)
            else:
                swilist[swi.number] = [swi]


class Statement(object):
    token_re = re.compile(r'^(\.?[A-Za-z_][A-Za-z_0-9]*|(?:&|0x)[0-9A-Fa-f]+|\.\.\.|%[01]+|0b[01]+|-?[0-9]+|[!\?:,\(\)=\|\[\]#\*\+]|->|"[^"]*"|\'[^\']*\')')

    def __init__(self, defmod, lines):
        self.lines = lines
        self.defmod = defmod
        if True:
            tok = self.token()
            if debug:
                print("Statement: %s" % (tok,))
            method_name = 'parse_%s' % (tok.lower(),)
            method = getattr(self, method_name, None)
            if method:
                method()
            else:
                if debug:
                    print("  not parseable")

    def list_tokens(self, label='Tokens'):
        print("%s:" % (label,))
        while True:
            tok = self.token()
            if not tok:
                break
            print("  '%s'" % (tok,))

    def token(self):
        while self.lines:
            line = self.lines[0].strip()
            if not line:
                self.lines.pop(0)
            else:
                match = self.token_re.search(line)
                if match:
                    tok = match.group(1)
                    line = line[len(tok):]
                    self.lines[0] = line
                    return tok
                else:
                    if len(self.lines) > 1:
                        line = line + ' ' + self.lines.pop(1).lstrip()
                        self.lines[0] = line
                    else:
                        raise ParseError("Cannot process token from line: %r" % (line,))

        return None

    def push_token(self, tok):
        if tok:
            self.lines.insert(0, tok)

    def token_group(self, terminal):
        """
        Return a list of tokens from the stream up to a terminator.
        """
        toks = []
        #print("Token group: terminal = %r" % (terminal,))
        while True:
            tok = self.token()
            #print(" TG: %s" % (tok,))
            if not tok:
                break
            if tok == terminal:
                break
            toks.append(tok)
        return toks

    def __repr__(self):
        return "<Statement()>"

    def value(self, toks):
        """
        Return a value parsed from a set of tokens.
        """
        stack = []
        #print("  value=%r" % (toks,))
        for tok in toks:
            if tok[0] == '%':
                value = int(tok[1:], 2)
            elif tok[0:2] == '0b':
                value = int(tok[2:], 2)
            elif tok[0] == '&':
                value = int(tok[1:], 16)
            elif tok[0:2] == '0x':
                value = int(tok[2:], 16)
            elif tok.isdigit() or (tok[0] == '-' and tok[1:].isdigit()):
                value = int(tok)
            elif tok[0] == '"' and tok[-1] == '"':
                value = tok[1:-1]
            elif tok[0] == "'" and tok[-1] == "'":
                #value = tok[1:-1]
                # This is a literal for now?
                value = tok
            else:
                # It's a constant string, I assume
                # FIXME: This isn't distinguishable from a regular string.
                value = tok
            stack.append(value)
        if not stack:
            return None
        if len(stack) == 1:
            return stack[0]
        # Eventually we'll include some expression processor
        return stack

    def expect(self, expect):
        tok = self.token()
        if isinstance(expect, tuple):
            if tok in expect or (tok and tok.upper() in expect):
                return tok
        else:
            if tok == expect or (tok and tok.upper() == expect):
                return tok

        raise ParseError("Expected %r, but got %r" % (expect, tok))

    def gettype(self, named=True):
        tok = self.token()
        elements = None
        if tok == '[':
            # This is an array of elements
            elements = self.token_group(']')
            # Recurse, because it could be an array of an array, etc.
            dtype = self.gettype(named=named)
            if len(elements) == 1:
                elements = elements[0]
                try:
                    elements = int(elements)
                except ValueError:
                    pass
            dtype = Array(dtype, elements)
            return dtype

        refs = 0
        while tok == '.Ref':
            refs += 1
            tok = self.token()

        # FIXME: .Ref should be a container type
        if refs:
            dtype = ('&' * refs) + tok
        elif tok.upper() in ('.STRUCT', '.UNION'):
            struct_tok = tok.upper()
            tok = self.expect(('(', ':'))
            name = None
            if tok == ':':
                name = self.token()
                self.expect('(')

            if struct_tok == '.STRUCT':
                obj = Struct(name)
            else:
                obj = Union(name)

            while True:
                # Each member consists of a type and a name
                dtype = self.gettype()
                name = self.token()

                tok = self.token()
                if tok and tok[0] == '"':
                    # This type has a comment.
                    # FIXME: Process it.
                    # (skipped for now)
                    pass
                else:
                    self.push_token(tok)

                tok = self.expect((',', ')', '...'))
                if tok == '...':
                    # This last item is actually an variable array
                    dtype = Array(dtype, '...')

                obj.add_member(Member(dtype, name))

                if tok == ')':
                    break
                if tok == '...':
                    # The next token must be the closing bracket
                    self.expect(')')
                    break

            dtype = obj
        else:
            dtype = tok

        if named:
            self.expect(':')
        return dtype

    def parse_title(self):
        self.defmod.title = self.token()
        if debug:
            print("  Title: %r" % (self.defmod.title,))

    def parse_const(self):
        #self.list_tokens('Constants')
        while True:
            toks = self.token_group(',')
            if not toks:
                break
            name = toks[0]
            if toks[1] != '=':
                raise ParseError("Constant token format unexpected (no =): %r" % (toks,))
            consttype = toks[2]
            if consttype == '.Ref':
                consttype = '&' + toks[3]
                toks.pop(2)
            if toks[3] != ':':
                raise ParseError("Constant token format unexpected (type specifier): %r" % (toks,))
            value = self.value(toks[4:])
            self.defmod.add_constant(Constant(name, consttype, value))
            if debug:
                print("  Constant: '%s' => (%s) %s" % (name, consttype, value))

    def parse_type(self):
        #self.list_tokens('Types')
        while True:
            name = self.token()
            if not name:
                break

            tok = self.token()
            if tok and tok[0] == '"':
                # This type has a comment.
                # FIXME: Process it.
                # (skipped for now)
                pass
            else:
                self.push_token(tok)

            tok = self.expect(("=", ',', None))
            if tok == ',' or tok is None:
                # Not sure what an unnamed type should be, but I'm going to call it a Bits right now.
                dtype = '.Any'
                if tok:
                    self.push_token(tok)
            else:
                dtype = self.gettype(named=False)

                tok = self.token()
                if tok and tok[0] == '"':
                    # This type has a comment.
                    # FIXME: Process it.
                    # (skipped for now)
                    pass
                else:
                    self.push_token(tok)

            self.defmod.add_type(name, dtype)
            if debug:
                print("  Type: %s" % (name,))

            tok = self.expect((',', None))
            if tok is None:
                break

    def parse_needs(self):
        #self.list_tokens('Needs')
        while True:
            need = self.token()
            if not need:
                break
            self.defmod.add_need(need)
            if debug:
                print("  Needs: %s" % (need,))

            tok = self.token()
            if tok is None:
                break
            if tok != ',':
                raise ParseError("Expected a ',' in Needs, but got %r" % (tok,))

    def parse_swi(self):
        # Format looks something like:
        # {Name = (NUMBER number "description",
        #          ENTRY ( {register ->|= type: name,}* )
        #          EXIT ( {register!? = .REF? type: name,}* )
        #          ABSENT
        #         ),?}*
        while True:
            name = self.token()
            if not name:
                break
            tok = self.token()
            self.expect('(')

            swi = SWI(name)

            while True:
                tok = self.expect(('NUMBER', 'ENTRY', 'EXIT', 'ABSENT')).upper()
                if tok == 'NUMBER':
                    tok = self.token()
                    swinumber = self.value([tok])
                    tok = self.token()
                    # The description could be omitted
                    description = None
                    if tok == '*':
                        # Not entirely sure what this means, but there isn't a description if so.
                        swi.starred = True
                    elif tok[0] != '"':
                        self.push_token(tok)
                    else:
                        description = self.value([tok])

                    swi.number = swinumber
                    swi.description = description

                elif tok == 'ABSENT':
                    swi.hidden = True

                elif tok == 'ENTRY':
                    self.expect('(')
                    while True:
                        reg = self.token().upper()
                        if reg[0] != 'R' and reg != 'FLAGS':
                            raise ParseError("Entry register name not understood: %s" % (reg,))
                        if reg == 'FLAGS':
                            dtype = '.flags'
                            name = None
                        else:
                            assign = self.expect(('->', '=', '#', '|', '+'))
                            # | means 'OR with the previous value'
                            # + appears to mean 'store the previous value as the first byte and the
                            #   rest of the structure is this structure' (for OS_Word)
                            if assign == '#':
                                dtype = '.literal'
                                name = self.value([self.token()])
                            else:
                                # In OSSpriteOp, there's a place where a constant is used with
                                # an '=', where here we expect to fetch a type. Because of this
                                # I'm going to fetch two tokens, then put them back and decode
                                # what I really want to do for that case. Probably this is just
                                # an oddity of the syntax, but I just need to get it to parse
                                # really.
                                if assign == '=':
                                    tok1 = self.token()
                                    tok2 = self.token()
                                    if tok2 == ',' or tok2 == ')':
                                        # This was the literal case just discussed.
                                        dtype = '.literal'
                                        name = self.value([tok1])
                                        self.push_token(tok2)
                                    else:
                                        self.push_token(tok2)
                                        self.push_token(tok1)
                                        dtype = self.gettype()
                                        name = self.token()
                                else:
                                    dtype = self.gettype()
                                    name = self.token()

                        # There might be a description on the register.
                        tok = self.token()
                        if tok[0] == '"':
                            # Description field present.
                            # We currently ignore.
                            pass
                        elif tok == '*':
                            # Starred field means that the description for the SWI definition applies to
                            # this constant (assuming it is a constant).
                            # We currently ignore.
                            pass
                        else:
                            self.push_token(tok)

                        swi.add_entry(Register(reg, assign, dtype, name))

                        tok = self.expect((',', ')'))
                        if tok == ')':
                            break

                elif tok == 'EXIT':
                    self.expect('(')
                    while True:
                        reg = self.token()
                        if reg[0] != 'R' and reg != 'FLAGS':
                            raise ParseError("Exit register name not understood: %s" % (reg,))
                        updated = False
                        corrupted = False
                        if reg == 'FLAGS':
                            assign = self.expect(('!',))
                            dtype = '.flags'
                            name = None
                        else:
                            assign = self.expect(('!', '?', '->', '=', '#'))
                            if assign == '!':
                                updated = True
                                assign = self.expect(('?', '->', '=', '#'))
                            if assign == '#':
                                dtype = '.literal'
                                name = self.value([self.token()])
                            elif assign == '?':
                                dtype = '.corrupted'
                                name = None
                                corrupted = True
                            else:
                                dtype = self.gettype()
                                name = self.token()

                        # There might be a comment on the register.
                        tok = self.token()
                        if tok[0] == '"':
                            # Comment field present
                            pass
                        else:
                            self.push_token(tok)

                        swi.add_exit(Register(reg, assign, dtype, name, updated, corrupted))

                        tok = self.expect((',', ')'))
                        if tok == ')':
                            break
                else:
                    raise ParseError("Unparseable SWI token '%s'" % (tok,))

                tok = self.expect((',', ')'))
                if tok == ')':
                    break

            self.defmod.add_swi(swi)
            if debug:
                print("  SWI: %r" % (swi,))

            tok = self.expect((',', None))
            if tok is None:
                break


def parse_file(filename, name=None, inctype='required'):
    if name is None:
        name = os.path.basename(filename).title()

    defmod = DefMod(name, modname=name.lower(), inctype=inctype)

    lineno = 0
    try:
        with open_ro(filename) as fh:
            accumulator = []
            inquotes = False
            for line in fh:
                lineno += 1

                # Replace any hard spaces with regular spaces
                line = line.replace('\xa0', ' ')
                line = line.rstrip('\n')
                if '//' in line:
                    before, after = line.split('//', 1)
                    line = before
                while ';' in line:
                    before, after = line.split(';', 1)
                    quotes_present = len(before.split('"')) - 1
                    if quotes_present & 1:
                        inquotes = not inquotes

                    if inquotes:
                        # This is a ; in a quoted string, so we need to just move it to the accumulator
                        # so that we can skip it nicely.
                        accumulator.append(before)
                        line = after
                        continue

                    line = after
                    accumulator.append(before)
                    Statement(defmod, accumulator)
                    accumulator = []

                if line:
                    accumulator.append(line)

                quotes_present = len(line.split('"')) - 1
                if quotes_present & 1:
                    inquotes = not inquotes

        if accumulator:
            Statement(defmod, accumulator)
    except ParseError as exc:
        exc.lineno = lineno
        raise

    return defmod


def write_all_swi_conditions(defmods, filename):
    with open(filename, 'w') as fh:
        # Header:
        fh.write('''\
"""
Conditions for the entry to SWIs by name.

Hopefully these will be correct.
"""

swi_conditions = {
''')

        defmods = [defmod for defmod in defmods if defmod.swis]
        defmods = sorted(defmods, key=lambda defmod: min(defmod.swis))
        # We now have a list of defmods ordered by their lowest swi number.
        mods = [{'name': defmod.name,
                 'defmod': defmod,
                 'swis': dict(defmod.swis)
                } for defmod in defmods]
        # Now we want to merge the SWIs into the earlier modules if they are duplicates.
        # This applies to definitions of service calls in separate modules.
        swis_known = {}
        for mod in mods:
            for swinum, swilist in sorted(mod['swis'].items()):
                if swinum in swis_known:
                    # Move the SWIs to the earlier module's swi entry and remove from this module
                    swis_known[swinum].extend(swilist)
                    del mod['swis'][swinum]
                else:
                    swis_known[swinum] = swilist

        # Resort mods based on the lowest SWI present (which will now move many modules back to their
        # real location now that the UpCalls, Vecctors, Events and Service Calls have been merged into
        # the OS module.
        mods = sorted(mods, key=lambda mod: min(mod['swis']) if mod['swis'] else 0)

        for mod in mods:
            defmod = mod['defmod']
            if mod['swis']:
                fh.write('    # %s:\n' % (defmod.title,))
                write_swi_conditions(mod['swis'], fh)
                fh.write('\n')

        # Footer:
        fh.write('''\
}
''')


def describe_swi_regsdefs(swidef):
    """
    Describe the register definitions for entry and exit conditions of a SWI.
    """
    regdefs = {
        'entry': {},
        'exit': {},
    }
    for name, regs in (('entry', swidef.entry), ('exit', swidef.exit)):

        regdef = regdefs[name]
        for reg in regs:
            if reg.reg == 'FLAGS':
                continue

            if reg.assign == '#':
                desc = 'constant ' + str(reg.name)
                name = None
            elif reg.assign == '->':
                if reg.dtype == '.Asm':
                    desc = 'pointer to code ' + reg.name
                elif reg.dtype == '.String':
                    desc = 'pointer to string ' + reg.name
                else:
                    desc = 'pointer to ' + reg.name
                name = reg.name
            elif reg.assign == '|':
                desc = "OR " + reg.name
                name = reg.name
            elif reg.assign == '+':
                desc = "in block " + reg.name
                name = reg.name
            elif reg.assign == '?':
                desc = 'corrupted'
                name = None
            elif reg.assign == '!':
                desc = 'updated ' + reg.name
                name = reg.name
            elif reg.assign == '=':
                if isinstance(reg.dtype, str) and reg.dtype[0] == '&':
                    desc = 'pointer to ' + reg.name
                else:
                    desc = reg.name
                name = reg.name
            else:
                desc = "unknown assignment '%s' of %s" % (reg.assign, reg.name)
                name = None

            regnum = int(reg.reg[1:])
            if regnum in regdef:
                regdef[regnum] += ' ' + desc
            else:
                regdef[regnum] = desc
    return regdefs


def write_swi_conditions(swis, fh):
    for swi, swilist in swis.items():
        swidef = swilist[0]

        if '_' not in swidef.name:
            # Skip vectors, events, etc
            continue

        # Decide whether this is a variadic SWI or not.
        if len(swilist) > 1:
            # Variadic SWI definition.
            # In theory there should be a set of SWI defs that have a constant value present on a
            # register. Usually that'll be R0 or R1.
            constant_absent = []
            constant_present = []
            constant_notint = []
            constant_registers = set()
            for swidef in swilist:
                has_constant = None
                has_integer = False
                for reg in swidef.entry:
                    if reg.assign == '#':
                        if has_constant is not None:
                            print("SWI &%06x (%s) has multiple constants" % (swidef.number, swidef.name))
                        has_constant = reg.reg
                        constant_registers |= set([reg.reg])
                        if isinstance(reg.name, int):
                            has_integer = True
                if has_constant:
                    if has_integer:
                        constant_present.append(swidef)
                    else:
                        constant_notint.append(swidef)
                else:
                    constant_absent.append(swidef)
            print("SWI &%06x (%s) has constants in registers: %s"
                    % (swidef.number, swidef.name, ", ".join(sorted(constant_registers))))
            print("          has %s variants with constants" % (len(constant_present),))
            if constant_notint:
                print("          has %s variants with constants that aren't ints" % (len(constant_notint),))
            print("          has %s variants without constants" % (len(constant_absent),))

            if len(constant_notint):
                # The constant that's used isn't an integer - it's probably a reference to a constant
                # which we don't yet support.
                print("          will not be matched, because it has non-int constants")
                continue

            indent = "    0x%06x: [" % (swidef.number,)
            # First list the variants that we know have matchable constants.
            for swidef in constant_present:
                regdefs = describe_swi_regsdefs(swidef)

                # Locate the constant.
                match_regs = {}
                for reg in swidef.entry:
                    if reg.assign == '#' and reg.reg != 'FLAGS':
                        match_reg = int(reg.reg[1:])
                        match_value = reg.name
                        match_regs[match_reg] = match_value

                # Register list at the moment is only ever 1 entry for the match
                match_reglist = ['%i: %s' % (reg, value) for reg, value in sorted(match_regs.items())]

                entry_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['entry'].items())]
                exit_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['exit'].items())]

                fh.write("%s{'label': %r,\n" % (indent, swidef.name,))
                indent = '               '
                fh.write("%s 'match': {%s},\n" % (indent, ', '.join(match_reglist),))
                if swidef.description:
                    fh.write("%s'description': %r,\n" % (indent, swidef.description,))
                fh.write("%s 'entry': {%s},\n" % (indent, ", ".join(entry_reglist),))
                fh.write("%s 'exit': {%s}},\n" % (indent, ", ".join(exit_reglist),))

            # Now list the variants that have no matches.
            for swidef in constant_absent:
                regdefs = describe_swi_regsdefs(swidef)

                entry_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['entry'].items())]
                exit_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['exit'].items())]
                fh.write("%s{'label': %r,\n" % (indent, swidef.name))
                indent = '               '
                fh.write("%s " % (indent,))
                fh.write("'description': %r,\n" % (swidef.description,))
                fh.write("%s 'entry': {%s},\n" % (indent, ", ".join(entry_reglist)))
                fh.write("%s 'exit': {%s}},\n" % (indent, ", ".join(exit_reglist)))
            fh.write("%s],\n" % (indent,))
        else:
            regdefs = describe_swi_regsdefs(swidef)

            entry_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['entry'].items())]
            exit_reglist = ['%i: "%s"' % (num, desc) for num, desc in sorted(regdefs['exit'].items())]
            fh.write("    0x%06x: [{" % (swidef.number,))
            indent = '               '
            fh.write("'label': %r,\n" % (swidef.name,))
            fh.write("%s 'description': %r,\n" % (indent, swidef.description,))
            fh.write("%s 'entry': {%s},\n" % (indent, ", ".join(entry_reglist)))
            fh.write("%s 'exit': {%s}}],\n" % (indent, ", ".join(exit_reglist)))


def now():
    return time.time()


def timestamp(epochtime, time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.fromtimestamp(epochtime).strftime(time_format)


def value_repr(value, name):
    if isinstance(value, (tuple, list)):
        value = value[0]
    if name.startswith(('Error_', 'Message_')) or name.endswith(('_FileType',)):
        # These two are always formatted as Hex
        return '0x%x' % (value,)
    if value & (value - 1) == 0:
        if value == 0:
            return '0'
        else:
            bit = int(math.log(value & ~(value - 1)) / math.log(2))
        return '(1<<%i)' % (bit,)
    else:
        return value


jinja2_functions = {
        'now': now,
        'timestamp': timestamp,
        'value_repr': value_repr,
        'set': set,
    }


class Templates(object):

    def __init__(self, path):
        import jinja2
        template_loader = jinja2.FileSystemLoader(searchpath=path)
        self.environment = jinja2.Environment(loader=template_loader,
                                              extensions=['jinja2.ext.loopcontrols'])

    def render(self, template_name, template_vars=None):
        """
        Render a template, and return it.

        @param: template_name: The name of the template to render
        @param: template_vars A dictionary of variables to process

        @return: generated output
        """
        if template_vars is None:
            template_vars = {}
        temp = self.environment.get_template(template_name)
        return temp.render(template_vars)

    def render_to_file(self, template_name, output, template_vars=None):
        """
        Render a template, and write it to a file.

        @param template_name: The name of the template to render
        @param output:        The output filename
        @param template_vars: A dictionary of variables to process
        """
        jinja2_vars = dict(template_vars)
        jinja2_vars.update(jinja2_functions)
        content = self.render(template_name, jinja2_vars)
        with open(output, 'wb') as f:
            print("Create %s" % (output,))
            f.write(content.encode("utf-8"))


class LocalTemplates(Templates):

    def __init__(self, path=None):
        here = os.path.dirname(__file__)
        if path:
            here = os.path.join(here, path)
        super(LocalTemplates, self).__init__(here)


def create_message_details(defmods, filename):
    template = LocalTemplates('templates')
    template.render_to_file('messages.py.j2', filename,
                            {
                                'defmods': defmods,
                            })


def create_pymodule_template(defmods, filename):
    template = LocalTemplates('templates')
    template.render_to_file('pymodule.py.j2', filename,
                            {
                                'defmods': defmods,
                            })


def create_api_template(defmods, filename):
    template = LocalTemplates('templates')
    template.render_to_file('pyro-api.py.j2', filename,
                            {
                                'defmods': defmods
                            })


def create_python_api_template(defmods, filename):
    template = LocalTemplates('templates')
    template.render_to_file('python-api.py.j2', filename,
                            {
                                'defmods': defmods,
                                'types': defmods.types,
                            })


def create_aarch64_api(defmods, filename):
    def simple_orr_constant(defmod, value):
        if value in defmod.constants:
            value = defmod.constants[value].value
        #print("Simple ORR: %i (&%x)" % (value, value))
        lowest_bit = value & ~(value-1)
        while value and value & lowest_bit:
            # Clear lowest bit
            value = value &~lowest_bit
            lowest_bit = lowest_bit << 1
        #print("  Simple = %r" % (not bool(value),))
        if value:
            # There is a discontinuous run of 1 bits, so not simple
            return False
        return True

    template = LocalTemplates('templates')
    template.render_to_file('aarch64-api.s.j2', filename,
                            {
                                'defmods': defmods,
                                'types': defmods.types,
                                'simple_orr_constant': simple_orr_constant,
                            })


def create_pymodule_constants(defmods, filename):
    template = LocalTemplates('templates')
    template.render_to_file('pymodule_constants.py.j2', filename,
                            {
                                'defmods': defmods
                            })


def create_nvram_constants(defmods, filename):
    # Variable names that aren't useful to us
    ignorable = {
            'RISCIX',
            'RISCIX32',
        }
    template = LocalTemplates('templates')
    # Rather than making the template do all the work, we'll filter the values down to
    # just the constants, so that they can go into the file more easily.
    values = {}
    names = {}
    for defmod in defmods:
        for name, constant in defmod.constants.items():
            if not name.startswith('OSByte_Configure'):
                # Skip non-NVRAM constants
                continue
            if constant.dtype.lower() != '.int':
                # Skip anything that's not a value
                continue
            if name.endswith('Shift'):
                # Skip bitfield shifts
                continue
            if name.endswith('Limit'):
                # Skip field widths
                continue


            # Trim off the leader
            name = name[16:]

            if name in ignorable:
                # Skip the names that we don't care about.
                continue

            value = constant.value
            if isinstance(value, (list, tuple)):
                # Annotated value
                value = value[0]

            if name in names:
                print("Warning: Name {} is defined multiple times".format(name))
            else:
                names[name] = value

            if value in values:
                values[value] = '{} / {}'.format(values[value], name)
            else:
                values[value] = name
            #print("%s => %s" % (name, value))
    template.render_to_file('nvram_constants.py.j2', filename,
                            {
                                'defmods': defmods,
                                'names': names,
                                'values': values,
                            })


class TypeRef(object):
    """
    A reference to a type, used when constructing the DefMods types list.
    """

    def __init__(self, name, dtype, defmod):
        self.name = name
        self.dtype = dtype
        self.defmod = defmod

    def __repr__(self):
        return "<{}({!r} in {}, type={})>".format(self.__class__.__name__,
                                                  self.name, self.defmod, self.dtype)


class DefMods(object):
    sections = [
            'Core',
            'Computer',
            'Toolbox',
            'User',
        ]

    def __init__(self, basedir=None):
        self.basedir = basedir
        self.found_defmods = None
        self.defmods = []
        self.modnames = {}
        self._all_types = None

    def __repr__(self):
        return "<{}({} defmods)>".format(self.__class__.__name__,
                                         len(self.defmods))

    def __len__(self):
        return len(self.defmods)

    def __iter__(self):
        return iter(self.defmods)

    def __getitem__(self, index):
        return self.defmods[index]

    def _collect(self):
        """
        Find all the the the defmod files, which we can import.
        """
        if self.found_defmods is None:
            self.found_defmods = {}
            if self.basedir:
                for section in self.sections:
                    # Modern oslib
                    path = os.path.join(self.basedir, section, 'oslib')
                    if os.path.isdir(path):
                        for leafname in os.listdir(path):
                            filename = os.path.join(path, leafname)
                            if filename.endswith('.swi'):
                                modname = leafname[:-4].lower()
                                self.found_defmods[modname] = filename

                    # Ancient oslib
                    path = os.path.join(self.basedir, section, 'defs')
                    if os.path.isdir(path):
                        for leafname in os.listdir(path):
                            filename = os.path.join(path, leafname)
                            modname = leafname.lower()
                            self.found_defmods[modname] = filename

    def resolve(self, name):
        self._collect()
        return self.found_defmods.get(name, None)

    def add(self, defmodfile, inctype='required'):
        defmod = parse_file(defmodfile, inctype=inctype)
        self.defmods.append(defmod)
        self.modnames[defmod.modname] = defmod

        for need in defmod.needs:
            need = need.lower()
            if need not in self.modnames:
                filename = self.resolve(need)
                if debug:
                    print("Resolve %s gave %s" % (need, filename))
                if filename:
                    self.add(filename, inctype='include')

        # Clear the cache
        self._all_types = None

    @property
    def types(self):
        if self._all_types is None:
            self._all_types = {}
            for defmod in self.defmods:
                types = dict((name, TypeRef(name=name, dtype=dtype, defmod=defmod)) for name, dtype in defmod.types.items())
                self._all_types.update(types)

        return self._all_types


def setup_argparse():
    parser = argparse.ArgumentParser(usage="%s [<options>] <def-mod-file>*" % (os.path.basename(sys.argv[0]),))
    parser.add_argument('--debug', action='store_true', default=False,
                        help="Enable debugging")
    parser.add_argument('files', nargs="+",
                        help="DefMod files to read")
    parser.add_argument('--oslib-dir', action='store', default=None,
                        help="Directory holding OSLib files")
    parser.add_argument('--swi-conditions', action='store',
                        help="File to write the SWI conditions into")
    parser.add_argument('--create-message-details', action='store',
                        help="File to write the Wimp message details into")
    parser.add_argument('--create-pymodule-template', action='store',
                        help="File to write a template for a RISC OS Pyromaniac module")
    parser.add_argument('--create-pymodule-constants', action='store',
                        help="File to write a constants file for RISC OS Pyromaniac")
    parser.add_argument('--create-api-template', action='store',
                        help="File to write a template for an API of the module")
    parser.add_argument('--create-python-api-template', action='store',
                        help="File to write a template for an Python API of the module")
    parser.add_argument('--create-aarch64-api', action='store',
                        help="File to write an AArch64 assembler file for an API of the module")
    parser.add_argument('--create-nvram-constants', action='store',
                        help="File to write a constants file for NVRAM (pass OSByte definition)")

    return parser


def main():
    parser = setup_argparse()

    options = parser.parse_args()

    global debug
    debug = options.debug

    defmods = DefMods(basedir=options.oslib_dir)

    for defmodfile in options.files:
        if not os.path.isfile(defmodfile):
            filename = defmods.resolve(defmodfile.lower())
            if filename:
                defmodfile = filename
        print("Reading %s" % (defmodfile,))
        defmods.add(defmodfile)

        #try:
        #    defmods.add(defmodfile)
        #except ParseError as exc:
        #    raise
        #except Exception as exc:
        #    print("  Failed %s: %s: %s" % (defmodfile, exc.__class__.__name__, exc))

    if options.swi_conditions:
        write_all_swi_conditions(defmods, options.swi_conditions)

    if options.create_message_details:
        create_message_details(defmods, options.create_message_details)

    if options.create_pymodule_template:
        create_pymodule_template(defmods, options.create_pymodule_template)

    if options.create_pymodule_constants:
        create_pymodule_constants(defmods, options.create_pymodule_constants)

    if options.create_api_template:
        create_api_template(defmods, options.create_api_template)

    if options.create_python_api_template:
        create_python_api_template(defmods, options.create_python_api_template)

    if options.create_aarch64_api:
        create_aarch64_api(defmods, options.create_aarch64_api)

    if options.create_nvram_constants:
        create_nvram_constants(defmods, options.create_nvram_constants)


if __name__ == '__main__':
    sys.exit(main())

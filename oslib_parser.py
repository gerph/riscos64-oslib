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

    def __repr__(self):
        return "<{}({} {}, value: {})>".format(self.__class__.__name__,
                                               self.dtype,
                                               self.name,
                                               self.value)

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
        if a == b:
            return self.name < other.name
        return a < b


class Register(object):

    def __init__(self, reg, assign, dtype, name, returned=False, corrupted=False):
        self.reg = reg
        self.assign = assign
        self.dtype = dtype
        self.name = name
        self.returned = returned
        self.corrupted = corrupted

    def copy(self):
        return Register(self.reg,
                        self.assign,
                        self.dtype,
                        self.name,
                        self.returned,
                        self.corrupted)

    def __repr__(self):
        return "<Register(%s %s %s: %s)>" % (self.reg, self.assign, self.dtype, self.name)


class SWI(object):

    def __init__(self, name):
        self.name = name
        self.defname = name     # The defined name (not the modified name)
        self.number = None
        self.description = None
        self.starred = False
        self.hidden = False
        # When hidden, the entry and exit parameters are not valid
        self.entry = []
        self.exit = []
        self.returned = None

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

    def set_return(self, reg):
        self.returned = reg

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

        return inregs

    def outregs(self, x_variant):
        outregs = {}
        nreg = len([reg for reg in self.inregs() if reg != -1])
        for reg in self.exit:
            if reg.returned and not x_variant:
                # In the non-x-variant this output register is absent
                continue
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
        self.swis = {}  # All of the SWI definitions

        # All the interfaces (swis, vectors, service, events, upcalls)
        self.interfaces = {}

        # Special cases of swis (the entries are also in SWIs):
        self.modswis = {}  # Just the SWIs for this module
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
        elif swi.name.split("_")[0].endswith("V"):
            swi.name = "OS_CallVector_" + swi.name
            swilist = self.vectors
        else:
            swilist = self.modswis

        if swi.number in swilist:
            swilist[swi.number].append(swi)
        else:
            swilist[swi.number] = [swi]

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

                        addreg = Register(reg, assign, dtype, name)
                        swi.add_entry(addreg)

                        tok = self.expect((',', ')'))
                        if tok == ')':
                            break

                elif tok == 'EXIT':
                    self.expect('(')
                    return_reg = None
                    while True:
                        reg = self.token().upper()
                        if reg[0] != 'R' and reg != 'FLAGS':
                            raise ParseError("Exit register name not understood: %s" % (reg,))
                        returned = False
                        corrupted = False
                        if reg == 'FLAGS':
                            assign = self.expect(('!',))
                            returned = True
                            dtype = '.flags'
                            name = None
                        else:
                            assign = self.expect(('!', '?', '->', '=', '#'))
                            if assign == '!':
                                returned = True
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

                        addreg = Register(reg, assign, dtype, name, returned, corrupted)
                        swi.add_exit(addreg)
                        if returned:
                            if return_reg is None:
                                swi.set_return(addreg)
                                return_reg = addreg
                            else:
                                raise ParseError("Repeated return register specification for register %s (repeats %s) in %r" % (reg, return_reg, swi))

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


def value_repr(value, name, dtype='unknown'):
    if isinstance(value, (tuple, list)):
        value = value[0]
    if name.startswith(('Error_', 'Message_')) or name.endswith(('_FileType', '_Class', 'Mask')) or value > 0xffff:
        # These are always formatted as Hex
        return '0x%x' % (value,)
    if name.endswith(('Op', 'Reason', 'No', 'Limit', 'Shift')) or dtype == '.Char' or dtype.endswith(('Op', 'Reason', 'Action')):
        # Should always be decimals
        return '%i' % (value,)
    if value & (value - 1) == 0:
        if value == 0:
            return '0'
        else:
            bit = int(math.log(value & ~(value - 1)) / math.log(2))
        return '(1<<%i)' % (bit,)
    else:
        return value


def warning(msg, defmod=None, swi=None):
    print("WARNING: %s" % (msg,))
    if defmod:
        print("  whilst processing module %r" % (defmod,))
    if swi:
        print("  in interface %r" % (swi,))
    return ''


jinja2_functions = {
        'now': now,
        'timestamp': timestamp,
        'value_repr': value_repr,
        'set': set,
        'warning': warning,
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


class TypesUsed(object):

    def __init__(self, mod, all_types):
        self.mod = mod
        self.all_types = all_types
        self.reported = {}
        self.ordered = []

        # Explicitly declared types from this module
        for name, dtype in sorted(mod.types.items()):
            self.use_type(name)

        # Used types in the SWIs
        for swi, swilist in mod.swis.items():
            for swidef in swilist:
                for reg in swidef.entry:
                    #print("SWI entry type: %r" % (reg.dtype,))
                    self.use_type(reg.dtype)
                for reg in swidef.exit:
                    #print("SWI exit type: %r" % (reg.dtype,))
                    self.use_type(reg.dtype)

    def __iter__(self):
        for name in self.ordered:
            dtype = self.all_types.get(name, None)
            if isinstance(dtype, TypeRef):
                dtype = dtype.dtype
            yield (name, dtype)

    def use_type(self, name):
        if isinstance(name, str) and name.startswith('&'):
            name = name[1:]

        if name in self.reported:
            return

        if isinstance(name, str):
            dtype = self.all_types.get(name, None)
            if isinstance(dtype, TypeRef):
                dtype = dtype.dtype
            #print("Use type %s: %r" % (name, dtype))
            if not dtype:
                self.ordered.append(name)
                self.reported[name] = True
                return
        else:
            dtype = name
            name = None
            #print("Use type %r" % (dtype,))

        if isinstance(dtype, str):
            self.use_type(dtype)

        elif isinstance(dtype, Struct):
            # Must include the structure as reported first, in case we have
            # a self-referential structure.
            self.reported[name] = True
            for field in dtype.members:
                field_name = field.name
                field_dtype = field.dtype
                self.use_type(field_dtype)

        elif isinstance(dtype, Union):
            for field in dtype.members:
                field_name = field.name
                field_dtype = field.dtype
                self.use_type(field_dtype)

        elif isinstance(dtype, Array):
            self.use_type(dtype.dtype)

        else:
            print("Do not understand type '%s' in TypesUsed (%r)" % (dtype.__class__.__name__, dtype))

        if name:
            self.ordered.append(name)
            self.reported[name] = True


class ConstantsUsed(object):

    def __init__(self, mod, all_constants, all_types):
        self.mod = mod
        self.all_constants = all_constants
        self.reported = {}
        self.ordered = []

        # Explicitly declared types from this module
        for name, dtype in sorted(mod.constants.items()):
            self.use_constant(name)

        # Used constants in the other things
        for name, dtype in TypesUsed(mod, all_types):
            if dtype:
                self.use_constant(dtype)

    def __iter__(self):
        for name in self.ordered:
            dtype = self.all_constants.get(name, None)
            if isinstance(dtype, ConstantRef):
                dtype = dtype.dtype
            #print("ConstantEnum: %s: %r" % (name, dtype))
            yield (name, dtype)

    def use_constant(self, name):
        if isinstance(name, str) and name.startswith('&'):
            name = name[1:]

        if name in self.reported:
            return

        if isinstance(name, str):
            dtype = self.all_constants.get(name, None)
            if isinstance(dtype, TypeRef):
                dtype = dtype.dtype
            #print("Use constant %s: %r" % (name, dtype))
            if not dtype:
                self.reported[name] = True
                return
        else:
            dtype = name
            name = None
            #print("Use constant type %r" % (dtype,))

        if isinstance(dtype, str):
            self.use_constant(dtype)

        elif isinstance(dtype, Struct):
            for field in dtype.members:
                field_name = field.name
                field_dtype = field.dtype
                self.use_constant(field_dtype)

        elif isinstance(dtype, Union):
            for field in dtype.members:
                field_name = field.name
                field_dtype = field.dtype
                self.use_constant(field_dtype)

        elif isinstance(dtype, Array):
            self.use_constant(dtype.dtype)
            if isinstance(dtype.nelements, str) and not dtype.nelements.isdigit():
                self.use_constant(dtype.nelements)

        elif isinstance(dtype, Constant):
            self.ordered.append(name)

        else:
            print("Do not understand type '%s' in ConstantsUsed (%r)" % (dtype.__class__.__name__, dtype))

        if name:
            self.reported[name] = True


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


def create_module_template(defmods, filename, filetype):
    template = LocalTemplates('templates')
    template.render_to_file('module-{}.j2'.format(filetype), filename,
                            {
                                'defmods': defmods,
                                'types': defmods.types,
                                'used_types': lambda defmod: TypesUsed(defmod, defmods.types),
                                'used_constants': lambda defmod: ConstantsUsed(defmod, defmods.constants, defmods.types),
                                'dtype_width': lambda dtype: dtype_width(dtype, defmods),
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


# Replacements for the function name expansion
oslib_swifunc1_re = re.compile("([^a-z])([A-Z])([A-Z][a-z])")
oslib_swifunc2_re = re.compile("([a-z0-9])([A-Z])(?!$)")

# Special names that aren't subject to the usual transformation
oslib_swifunc_special = {
        'Hourglass_LEDs': 'hourglass_leds',
        'OS_CallAVector': 'os_call_a_vector',
    }

def oslib_swifunc(name):
    """
    Convert a SWI name to a function name.

    The name is given in the form OS_MyOperationHere and should
    be converted to os_my_operation_here.
    Multiple capitalised letters should become a single string,
    eg Portable_ReadBMUVariable should become xportable_read_bmu_variable
    """

    # Handle the special cases
    replacement = oslib_swifunc_special.get(name)
    if replacement:
        return replacement

    if '_' not in name:
        print("Warning: SWI '{}' does not have any underscore".format(name))
        return name.lower()
    (module, name) = name.split('_', 1)
    name = oslib_swifunc1_re.sub(r"\1\2_\3", name)
    name = oslib_swifunc2_re.sub(r"\1_\2", name)
    return ("%s_%s" % (module, name)).lower()


def dtype_width(dtype, defmods):
    """
    Return the bit-width of a given type.
    """
    width = 64;
    if isinstance(dtype, tuple):
        dtype = dtype[0]
    if isinstance(dtype, str):
        dtype = dtype.lower()
        #print("dtype: %s" % (dtype,))

        while isinstance(dtype, str):
            resolved = defmods.lookup_type(dtype)
            if resolved:
                #print("  resolves to %s" % (resolved,))
                dtype = resolved.dtype
            else:
                break

    if not isinstance(dtype, str):
        raise RuntimeError("Cannot determine width of %r" % (dtype,))

    if dtype[0] == '&':
        width = 64
    elif dtype in ('.int', '.bits', '.bool'):
        width = 32
    return width


def create_aarch64_api(defmods, filename):
    def simple_orr_constant(defmod, value):
        if value in defmod.constants:
            value = defmod.constants[value].value
        if isinstance(value, list):
            value = value[0]
        if not isinstance(value, int):
            print("WARNING: Value %r (%s) is not a number" % (value, value.__class__.__name__))
            return True
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
                                'oslib_swifunc': oslib_swifunc,
                                'dtype_width': lambda dtype: dtype_width(dtype, defmods),
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

def create_rust(defmods, dirname):
    os.makedirs(os.path.join(dirname, "oslib", "src"), exist_ok=True)

    with open(os.path.join(dirname, "oslib", "Cargo.toml"), 'w') as fh:
        fh.write('[package]\nname = "oslib"\nedition = "2021"\npublish = false\n')
        with open("VersionNum", 'r') as v:
            for line in v.readlines():
                m = re.match(r'.*Module_MajorVersion\s+"0*([0-9]+)\.0*([0-9]+)".*', line)
                if m:
                    fh.write(f'version = "{m.group(1)}.{m.group(2)}.0"\n')

    with open(os.path.join(dirname, "oslib", "src", "lib.rs"), 'w') as fh:
        fh.write("//! # OSLib for RISC OS\n//!\n//! This provides access to the RISC OS API from Rust.\n//!\n")

        for defmod in defmods:
            # Super is a reserved word in Rust, but the defmod doesn't contain any useful SWIs so we can ignore it
            if defmod.name != 'Super':
                fh.write(f"pub mod {defmod.name.lower()};\n")

    for defmod in defmods:
        template = LocalTemplates('templates')
        template.render_to_file('rust-api.rs.j2', os.path.join(dirname, "oslib", "src", defmod.name.lower() + ".rs"),
                            {
                                'defmod': defmod,
                                'types': defmods.types,
                                'magic_word': magic_word,
                                'regex_match': regex_match,
                                'contains_var_array': lambda dtype, array_only=False: contains_var_array(dtype, array_only, defmods.types),
                                'contains_union': lambda dtype, imm_only=False: contains_union(dtype, 1 if imm_only else 2, defmods.types),
                                'camel_to_snake': camel_to_snake,
                                'snake_to_camel': snake_to_camel,
                            })

def regex_match(regex, text):
    """
    Return True if text matches a regex
    """
    return re.match(regex, str(text)) is not None

def magic_word(text):
    """
    Convert a magic word string to a 32bit int
    """
    return ord(text[1]) | (ord(text[2]) << 8) | (ord(text[3]) << 16) | (ord(text[4]) << 24)

def contains_var_array(dtype, array_only, types):
    """
    Return True if this data type contains a variable length array (possibly in a child struct), or (when array_only False) the last struct member is variable length
    """
    if isinstance(dtype, str):
        if dtype[0] in ['.', '&']:
            return False
        elif dtype == 'Void':
            return False
        elif dtype in types:
            return contains_var_array(types[dtype], array_only, types)
    elif isinstance(dtype, Struct):
        if len(dtype.members) > 0:
            m = dtype.members[-1]
            if isinstance(m.dtype, Array):
                if m.dtype.nelements == '...':
                    return True
            elif contains_var_array(m.dtype, False, types) and not array_only:
                return True
        return False
    elif isinstance(dtype, Union):
        return False
    elif isinstance(dtype, Array):
        if dtype.nelements == '...':
            return True
        return False
    elif isinstance(dtype, TypeRef):
        return contains_var_array(dtype.dtype, array_only, types)

    raise RuntimeError("Cannot determine type of %r" % (dtype,))

def contains_union(dtype, depth, types):
    """
    Return True if this data type or (if depth == 2) a child contains a union
    """
    if isinstance(dtype, str):
        if dtype[0] in ['.', '&']:
            return False
        elif dtype == 'Void':
            return False
        elif dtype in types:
            return contains_union(types[dtype], depth, types)
    elif isinstance(dtype, Struct):
        if depth > 0:
            for m in dtype.members:
                if contains_union(m.dtype, 0 if depth == 1 else depth, types):
                    return True
        return False
    elif isinstance(dtype, Union):
        return True
    elif isinstance(dtype, Array):
        return contains_union(dtype.dtype, depth, types)
    elif isinstance(dtype, TypeRef):
        return contains_union(dtype.dtype, depth, types)

    raise RuntimeError("Cannot determine type of %r" % (dtype,))

def camel_to_snake(name):
    """
    Convert a Camel_CaseName to Snake_Case_Name
    """
    underscore = False
    snake = ''
    for i in range(len(name)):
        if name[i] == '_':
            underscore = True
        elif name[i].isupper():
            if underscore and name[i-1] not in ['_', ':'] and not name[i-1].isupper():
                snake += '_'
        snake += name[i]
    return snake

def snake_to_camel(name):
    """
    Convert a Snake_case_name to CamelCaseName
    """
    new_word = True
    camel = ''
    for i in range(len(name)):
        if name[i] in ['_', ':']:
            new_word = True
        else:
            if new_word:
                camel += name[i].upper()
            else:
                camel += name[i]
            new_word = False
    return camel

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


class ConstantRef(TypeRef):
    pass


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
        self._lookup_types = None
        self._all_constants = None

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

    def lookup_type(self, name):
        name = name.lower()
        return self.lookup_types.get(name, None)

    @property
    def types(self):
        if self._all_types is None:
            self._all_types = {}
            for defmod in self.defmods:
                types = dict((name, TypeRef(name=name, dtype=dtype, defmod=defmod)) for name, dtype in defmod.types.items())
                self._all_types.update(types)

        return self._all_types

    @property
    def lookup_types(self):
        if self._lookup_types is None:
            self._lookup_types = {}
            for defmod in self.defmods:
                types = dict((name, TypeRef(name=name, dtype=dtype, defmod=defmod)) for name, dtype in defmod.types.items())
                for name, tref in types.items():
                    self._lookup_types[name.lower()] = tref

        return self._lookup_types

    @property
    def constants(self):
        if self._all_constants is None:
            self._all_constants = {}
            for defmod in self.defmods:
                types = dict((name, ConstantRef(name=name, dtype=dtype, defmod=defmod)) for name, dtype in defmod.constants.items())
                self._all_constants.update(types)

        return self._all_constants


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
    parser.add_argument('--create-rust', action='store',
                        help="Directory to write the rust into")
    parser.add_argument('--create-module-cmhg-template', action='store',
                        help="File to write a CMHG template for a C module into")
    parser.add_argument('--create-module-c-template', action='store',
                        help="File to write a C source template for a C module into")
    parser.add_argument('--create-module-h-template', action='store',
                        help="File to write a C header template for a C module into")
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

    if options.create_rust:
        create_rust(defmods, options.create_rust)

    if options.swi_conditions:
        write_all_swi_conditions(defmods, options.swi_conditions)

    if options.create_message_details:
        create_message_details(defmods, options.create_message_details)

    if options.create_module_cmhg_template:
        create_module_template(defmods, options.create_module_cmhg_template, 'cmhg')

    if options.create_module_c_template:
        create_module_template(defmods, options.create_module_c_template, 'c')

    if options.create_module_h_template:
        create_module_template(defmods, options.create_module_h_template, 'h')

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

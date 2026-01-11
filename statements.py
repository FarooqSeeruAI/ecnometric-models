# -*- coding: utf-8 -*-
"""
statements.py

Contains classes and helper functions needed to implement equations and formulas

"""

import itertools
import copy
import math
import re

#
#  Helper functions
#


def mergeindexandsets(indexesa, indexesb, setsa, setsb):
    '''
    Merge two pairs of indexes and sets by determining which is the super and returning them

    Parameters
    ----------
    indexesa : TYPE
        DESCRIPTION.
    indexesb : TYPE
        DESCRIPTION.
    setsa : TYPE
        DESCRIPTION.
    setsb : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    if set(indexesa) <= set(indexesb):
        superindex = indexesb
        superset = setsb
        subindex = indexesa
        subset = setsa
    elif set(indexesb) <= set(indexesa):
        superindex = indexesa
        superset = setsa
        subindex = indexesb
        subset = setsb
    else:
        raise ValueError("Error finding supremum set")

    for i in subindex:
        if i not in superindex:
            raise ValueError("Error couldnt align indexes")

        if subset[subindex.index(i)] != superset[superindex.index(i)]:
            raise ValueError("Error indexes dont seem to align")

    return superindex, superset

def strip_outer_parenthesis(instr):
    '''
    Strip outer parenthesis from a string, as long as they are a single
    set - eg, (a+b), not (a) + (b)

    Parameters
    ----------
    instr : String
        The string to strip.

    Returns
    -------
    String: the stripped string

    '''
    outstr = instr.strip()
    if (outstr[0] == "(") and (outstr[-1] == ")"):
        parlvl = 0
        hitzero = False
        for i in outstr[0:-1]:
            if i == "(":
                parlvl = parlvl + 1
            elif i == ")":
                parlvl = parlvl - 1
            if parlvl == 0:
                hitzero = True
        if hitzero == False:
            outstr = instr[1:-1].strip()
    return outstr

def test_square_block(instr):
    '''
    Check to see if a string is wholely contained in a single level
    of square brackets

    Parameters
    ----------
    instr : String
        The string to test.

    Returns
    -------
    Bool - true if it is a wholely contained square bracket block.

    '''

    outbool = False

    outstr = instr.strip()

    if (outstr[0] == "[") and (outstr[-1] == "]"):
        parlvl = 0
        hitzero = False
        for i in outstr[0:-1]:
            if i == "[":
                parlvl = parlvl + 1
            elif i == "]":
                parlvl = parlvl - 1
            if parlvl == 0:
                hitzero = True
        if hitzero == False:
            outbool = True

    return outbool




#
# StatementNode class
#

class StatementNode(object):

    '''
    '''

    def __init__(self, equationstring, sets, indexes, statementname = 'None', statementline = 0, parse=True):
        self.equationstringorig = equationstring
        self.sets = sets
        self.indexes = indexes
        self.statementname = statementname
        self.statementline = statementline

        if parse:
            self._parse()

    def __repr__(self):
        if self.operator == "var":
            retval = f"var({self.var})"
        elif self.operator == "loge":
            retval = f"loge({self.branch})"
        elif self.operator == "num":
            retval = f"( {self.value} )"
        elif self.operator in ['==','!=','<','>','>=','<=']:
            retval = f"( {self.branches[0]} {self.operator} {self.branches[1]} )"
        elif isinstance(self.operator, list):
            retval = ""
            for i in range(len(self.operator)):
                if (i != 0) or (self.operator[i] == '-'):
                    retval = retval + f" {self.operator[i]} "
                retval = retval + f"( {self.branches[i]} )"
        else:
            raise ValueError(f"Unhandled operator {self.operator} in StatementNode.__repr__")
        return retval

    def __mul__(self, other):


        indexes, sets = mergeindexandsets(self.indexes, other.indexes, self.sets, other.sets)

        if isinstance(other, StatementNode):
            if self.operator == "num" and other.operator == "num":
                # both numbers, just do the arithmetic
                retval = StatementNode(self.value * other.value, sets, indexes, statementname = self.statementname, statementline = self.statementline)
            elif (self.operator == 'num' and self.value == 0) or (other.operator == 'num' and other.value == 0):
                # we're multiplying zeros
                retval = StatementNode(0.0, sets, indexes, statementname = self.statementname, statementline = self.statementline)
            elif (self.operator == 'num' and self.value == 1):
                # we're multiplying by 1
                retval = copy.deepcopy(other)
            elif (other.operator == 'num' and other.value == 1):
                # we're multiplying by 1
                retval = copy.deepcopy(self)
            elif isinstance(self.operator, list) and \
                isinstance(other.operator, list) and \
                self.operator[0] in '*/' and \
                other.operator[0] in '*/':
                # check if both sides are */

                retval = StatementNode(None, sets, indexes, parse=False)
                branchestemp = copy.deepcopy(self.branches) + copy.deepcopy(other.branches)
                operatortemp = copy.deepcopy(self.operator) + copy.deepcopy(other.operator)

                # Sweep through - if we are multiplying by a 1 we can ditch it
                retval.branches = []
                retval.operator = []
                for b,o in zip(branchestemp, operatortemp):
                    if not (b.operator == 'num' and b.value == 1):
                        retval.branches.append(b)
                        retval.operator.append(o)


            else:
                retval = StatementNode(None, sets, indexes, parse=False)
                retval.operator = ["*","*"]
                retval.branches = [copy.deepcopy(self), copy.deepcopy(other)]

            return retval
        else:
            raise TypeError("Unsupported operand type for *: 'StatementNode' and '{}'".format(type(other)))

    def __truediv__(self, other):

        indexes, sets = mergeindexandsets(self.indexes, other.indexes, self.sets, other.sets)

        if isinstance(other, StatementNode):
            retval = StatementNode(None, sets, indexes, parse=False)
            retval.operator = ["*","/"]
            retval.branches = [copy.deepcopy(self), copy.deepcopy(other)]
            return retval
        else:
            raise TypeError("Unsupported operand type for /: 'StatementNode' and '{}'".format(type(other)))

    def __add__(self, other):

        indexes, sets = mergeindexandsets(self.indexes, other.indexes, self.sets, other.sets)

        if isinstance(other, StatementNode):
            if self.operator == "num" and other.operator == "num":
                # both numbers, just do the arithmetic
                retval = StatementNode(self.value + other.value, sets, indexes, statementname = self.statementname, statementline = self.statementline)

            elif isinstance(self.operator, list) and \
                isinstance(other.operator, list) and \
                self.operator[0] in '+-' and \
                other.operator[0] in '+-':
                # check if both sides are +-

                retval = StatementNode(None, sets, indexes, parse=False, statementname = self.statementname, statementline = self.statementline)
                branchestemp = copy.deepcopy(self.branches) + copy.deepcopy(other.branches)
                operatortemp = copy.deepcopy(self.operator) + copy.deepcopy(other.operator)

                # Sweep through - if we are adding or subtracting a 0 we can ditch it
                retval.branches = []
                retval.operator = []
                for b,o in zip(branchestemp, operatortemp):
                    if not (b.operator == 'num' and b.value == 0):
                        retval.branches.append(b)
                        retval.operator.append(o)

            elif isinstance(self.operator, list) and \
                self.operator[0] in '+-' and \
                (other.operator == 'num' or other.operator == 'var') :

                retval = copy.deepcopy(self)
                retval.sets = sets
                retval.indexes = indexes
                retval.operator.append('+')
                retval.branches.append(copy.deepcopy(other))

            elif isinstance(other.operator, list) and \
                other.operator[0] in '+-' and \
                (self.operator == 'num' or self.operator == 'var') :

                retval = copy.deepcopy(other)

                retval.sets = sets
                retval.indexes = indexes

                retval.branches = [copy.deepcopy(self)] + retval.branches
                retval.operator = ['+'] + retval.operator


            else:
                retval = StatementNode(None, sets, indexes, parse=False, statementname = self.statementname, statementline = self.statementline)
                retval.operator = ["+","+"]
                retval.branches = [copy.deepcopy(self), copy.deepcopy(other)]

            return retval
        else:
            raise TypeError("Unsupported operand type for -: 'StatementNode' and '{}'".format(type(other)))

    def __sub__(self, other):

        indexes, sets = mergeindexandsets(self.indexes, other.indexes, self.sets, other.sets)

        if isinstance(other, StatementNode):
            if self.operator == "num" and other.operator == "num":
                # both numbers, just do the arithmetic
                retval = StatementNode(self.value - other.value, sets, indexes, statementname = self.statementname, statementline = self.statementline)

            elif isinstance(self.operator, list) and \
                isinstance(other.operator, list) and \
                self.operator[0] in '+-' and \
                other.operator[0] in '+-':
                # check if both sides are +-

                retval = StatementNode(None, sets, indexes, parse=False)
                branchestemp = copy.deepcopy(self.branches) + copy.deepcopy(other.branches)
                operatortemp = copy.deepcopy(self.operator)
                for i in other.operator:
                    if i == '+':
                        operatortemp.append('-')
                    else:
                        operatortemp.append('+')

                # Sweep through - if we are adding or subtracting a 0 we can ditch it
                retval.branches = []
                retval.operator = []
                for b,o in zip(branchestemp, operatortemp):
                    if not (b.operator == 'num' and b.value == 0):
                        retval.branches.append(b)
                        retval.operator.append(o)

            elif isinstance(self.operator, list) and \
                self.operator[0] in '+-' and \
                (other.operator == 'num' or other.operator == 'var') :

                retval = copy.deepcopy(self)
                retval.sets = sets
                retval.indexes = indexes
                retval.operator.append('-')
                retval.branches.append(copy.deepcopy(other))

            elif isinstance(other.operator, list) and \
                other.operator[0] in '+-' and \
                (self.operator == 'num' or self.operator == 'var') :

                retval = copy.deepcopy(other)
                operatortemp = []
                for i in retval.operator:
                    if i == '+':
                        operatortemp.append('-')
                    else:
                        operatortemp.append('+')
                retval.operator = operatortemp

                retval.branches = [copy.deepcopy(self)] + retval.branches
                retval.operator = ['+'] + retval.operator
                retval.sets = sets
                retval.indexes = indexes


            else:
                retval = StatementNode(None, sets, indexes, parse=False)
                retval.operator = ["+","-"]
                retval.branches = [copy.deepcopy(self), copy.deepcopy(other)]

            return retval
        else:
            raise TypeError("Unsupported operand type for -: 'StatementNode' and '{}'".format(type(other)))




    def _parse(self):


        # A number could either be passed as a number, or it could be a string representing a number
        # Try converting so we can just test it
        eqnstr = self.equationstringorig

        if isinstance(self.equationstringorig, str):
            eqnstr = self.equationstringorig.strip()

            eqnstr = eqnstr.replace(":"," : ")
            eqnstr = eqnstr.replace("+"," + ")
            eqnstr = eqnstr.replace("-"," - ")
            eqnstr = eqnstr.replace("/"," / ")
            eqnstr = eqnstr.replace("*"," * ")
            eqnstr = eqnstr.replace("^", " ^ ")
            eqnstr = eqnstr.replace("("," ( ")
            eqnstr = eqnstr.replace(")"," ) ")
            eqnstr = eqnstr.replace("=="," == ")
            eqnstr = eqnstr.replace("!="," != ")
            eqnstr = eqnstr.replace(">"," > ")
            eqnstr = eqnstr.replace("<"," < ")
            eqnstr = eqnstr.replace("> =",">=")
            eqnstr = eqnstr.replace("< =","<=")
            eqnstr = eqnstr.replace(">="," >= ")
            eqnstr = eqnstr.replace("<="," <= ")

            oldeqnstr = eqnstr
            while True:
                eqnstr = oldeqnstr.replace("  "," ")
                if eqnstr == oldeqnstr:
                    break
                oldeqnstr = eqnstr

            # see if we are wholely enclosed by parenthesis. This stripping should be done repeatedly
            # eg to handle (())
            oldeqnstr = eqnstr
            while True:
                eqnstr = strip_outer_parenthesis(oldeqnstr)

                if eqnstr == oldeqnstr:
                    break
                oldeqnstr = eqnstr

        try:
            float(eqnstr)
            numtype = True
        except:
            numtype = False

        # check to see if there are any operators in the remaining expression - we may
        # be down to simply a variable
        # Note that from above, every operator should have a space either side.
        if numtype or (" " not in eqnstr):
            # This could still be a variable or a number. If its a number we want
            # to evaluate it as a numeric type, otherwise hold onto it as a string
            if numtype:
                self.value = float(eqnstr)
                self.operator = "num"
            else:
                # We need to split this at the potential underscores
                # Note that the indexes could also be explicit representations of elements in sets
                # ie, "household", but that gets picked up at evaluation time
                splitstr = eqnstr.split("_")
                self.var = splitstr[0]
                self.myindexes = splitstr[1:]
                self.operator = "var"
            return

        if test_square_block(eqnstr):
            # We are in a square bracket block
            # There is the potential for different types
            eqnparts = eqnstr[1:-1].strip().split(":", maxsplit=2)
            if eqnparts[0].strip().lower() == "sum":
                self.operator = "sum"
                # for a sum the nodes are simply a pair of an index and a set, combined with the actual internal node
                # at parse time we simply augment the sets and indices that get passed to the
                # daughter node with the new index and set
                # At evaluation time each instance of the daughter node will have a modified
                # indextuple passed to it, for each instance of the index
                self.indexandset = eqnparts[1].replace(" ","").split("=") # left is a pair of an index, and a set
                self.branch = StatementNode(eqnparts[2].strip(), self.sets + [self.indexandset[1]], self.indexes + [self.indexandset[0]], self.statementname, self.statementline)
            elif eqnparts[0].strip().lower() == "if":
                self.operator = "if"
                # TODO if documentation
                condition = eqnparts[1].strip().split(maxsplit=3)
                # TODO CHECK THE CONDITION IS GOOD
                self.condlhs = StatementNode(condition[0], self.sets, self.indexes, self.statementname, self.statementline)
                self.condrhs = StatementNode(condition[2], self.sets, self.indexes, self.statementname, self.statementline)
                self.condop = condition[1]
                self.branch = StatementNode(eqnparts[2].strip(), self.sets, self.indexes, self.statementname, self.statementline)
            elif eqnparts[0].strip().lower() == "loge":
                self.operator = "loge"
                # TODO loge documentation
                self.branch = StatementNode(eqnparts[1].strip(), self.sets, self.indexes, self.statementname, self.statementline)
            else:
                self.operator = "unhandled"
            return

        # You can definately do this with a regex - but this is easier to follow
        # iterate from left to right, finding the highest ranked operator
        
        # The point of the logic below is to find the operator with the highest level
        # of precidence - ie, we do * before +, etc etc
        
        highestlevel = 0

        pardepth = 0
        levels = []


        highestlevel = 0
        for i in range(len(eqnstr)):
            # classify the current character. we only care if the depth is zero, ie
            # we arent inside a parenthesis block (noting that we've already stripped
            # outer parenthesis above)
            testchar = eqnstr[i]
            if   testchar in "([":
                pardepth = pardepth + 1
            elif testchar in ")]":
                pardepth = pardepth - 1

            currentlvl = 0
            if pardepth == 0:
                if testchar in '+-':
                    currentlvl = 10
                elif testchar in '*/':
                    currentlvl = 9
                elif testchar in '^':
                    currentlvl = 8
                    
                # Check for operators that will return a bool
                # These may be more than a character long, so there's a bit of logic to
                # see if we've already matched a comparison operator, eg to stop us from
                # first matching '<>' then matching '>'
                
                # We don't want to catch anything that isn't at pardepth > 0 (ie, in an 'if' or similar)
                # remember the 
                
                if testchar in ['=','<','>','!']:
                    if highestlevel != 11: # this makes sure we don't match a second '=' as noted above
                        teststr = testchar
                        if (i < (len(eqnstr) - 1)) and eqnstr[i+1] == '=':
                            teststr = teststr + '='
                        if teststr in ['==','!=','<','>','>=','<=']:
                            currentlvl = 11
                            conditional = teststr
            

            if (currentlvl > highestlevel) and (pardepth == 0):
                highestlevel = currentlvl
            levels.append(currentlvl)


        # now we know the highest level of operator, and a vector of the positions
        # lets bust the equation string into the substrings that will be our
        # daughters and the operators that are applied
        splitpositions = []
        for i in range(len(levels)):
            if levels[i] == highestlevel:
                splitpositions.append(i)
        splitpositions.append(len(levels))


        # Highest level of 8 (ie, '^') should always split in 2
        if highestlevel == 8:
            if len(splitpositions) != 2:
                raise ValueError(f"Error - unexpected number of splits after finding ^ as highest level operator in {eqnstr}, line {self.statementline}.")
            num = eqnstr[0:splitpositions[0]]
            exp = eqnstr[splitpositions[0]+1:]
            self.branches = [StatementNode(num, self.sets, self.indexes, self.statementname, self.statementline), \
                             StatementNode(exp, self.sets, self.indexes, self.statementname, self.statementline)]
            self.operator = '^'

        # These are the conditionals
        elif highestlevel == 11:
            if len(splitpositions) != 2:
                raise ValueError(f"Error - unexpected number of splits after finding conditional as highest level operator in {eqnstr}, line {self.statementline}.")

            lhs = eqnstr[:splitpositions[0]]
            rhs = eqnstr[splitpositions[0]+len(conditional):]
            self.branches = [StatementNode(lhs, self.sets, self.indexes, self.statementname, self.statementline), \
                             StatementNode(rhs, self.sets, self.indexes, self.statementname, self.statementline)]
            self.operator = conditional

        else:

            # The remaining possible operators have arbitrary number of branches, so operator is now a list
            self.branches = []
            self.operator = []
    
            # The first split position can be a special case
            # if we found a split at 0, then it is a '-'
            # If it's not, thats unexpected
            firstneg = False
            if splitpositions[0] == 0:
                if highestlevel != 10:
                    raise ValueError(f"Error - unexpected operator {eqnstr[0]} found at the start of {eqnstr}, line {self.statementline}.")
                if eqnstr[0] == '-':
                    firstneg = True
                    splitpositions = splitpositions[1:]
                else:
                    raise ValueError(f"Error - unexpected operator {eqnstr[0]} found at the start of {eqnstr}, line {self.statementline}.")
    
            for i in range(len(splitpositions)):
                # The highest level tells us something about what we are about to decompose
                # If its 10, we are dealing with addition and subtraction.
                # If its 9, multiplication and division
    
                # The first element carries an implicit + or *, depending on what we are doing
                if i == 0:
                    start = 0
                    if firstneg:
                        operator = '-'
                        start = 1
                    elif highestlevel == 10:
                        operator = '+'
                    else:
                        operator = '*'
                else:
                    start = splitpositions[i-1] + 1
                    operator = eqnstr[splitpositions[i-1]]
                end = splitpositions[i]
    
                spliteqn = eqnstr[start:end]
    
                self.branches.append(StatementNode(spliteqn, self.sets, self.indexes, self.statementname, self.statementline))
                self.operator.append(operator)


    def clean(self):
        '''
        Member to do a filter through and collapse unnecessary structures

        Returns
        -------
        None.

        '''
        # Check to see if we have multiple 'num' vars in an arithmetic branch, which may then be collapsed

        if isinstance(self.operator, list):
            # Check if we have multiple nums
            numcount = 0

            for i in self.branches:
                if i.operator == 'num':
                    numcount = numcount + 1

            if numcount > 0:
                # There are nodes we can collapse
                if self.operator[0] in "+-":
                    collapsed = 0
                else:
                    collapsed = 1

            # easier if we count backwards from the end
            for i in range(len(self.branches)-1, -1, -1):
                if self.branches[i] == 'num':
                    if self.operators[i] == '+':
                        collapsed = collapsed + self.branches.value
                    elif self.operators[i] == '-':
                        collapsed = collapsed + self.branches.value
                    elif self.operators[i] == '*':
                        collapsed = collapsed * self.branches.value
                    elif self.operators[i] == '/':
                        collapsed = collapsed / self.branches.value
                self.branches = self.branches[0:i] + self.branches[i+1:]




    def evaluate(self, dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = None, fillval = None):
        '''
        Parameters
        ----------
        dvarhandler : TYPE
            DESCRIPTION.

        sets: A list of the sets over which the formula is defined
        indexes: A list of the indexes that are used to represent each set
        indextuples: A list of tuples describing the ordering within the sets in which the formula is applied


        Returns
        -------
        A list of the values evaluated, aligned to the ordering of indextuples.

        '''
        if evalvec is not None:
            if isinstance(evalvec, list):
                if len(evalvec) != len(indextuples):
                    raise ValueError(f"Unexpected length for evalvec, got {len(evalvec)}, expecting {len(indextuples)}.")
            else:
                raise ValueError(f"Expecting list type for evalvec, got {type(evalvec)}")


        try:
            if self.operator == "unhandled":
                raise ValueError("Unhandled operator encountered")
            elif self.operator == "num":
                # this needs to be returned as a list of values the same length
                # as expected by the parent
                if evalvec is None:
                    return [self.value] * len(indextuples)
                else:
                    retval = [fillval] * len(indextuples)
                    for i in range(len(indextuples)):
                        if evalvec[i]:
                            retval[i] = self.value
                    return retval

            elif self.operator == "var":
                # this is where we evaluate the variables
                # we have:
                #   self.var - the name of the datavar
                #   self.myindexes - the indexes over which the datavar is ranging (eg X_i_j)
                #   sets - the potential sets over which we might range
                #   indexes - the indexes represnting these sets, which should cover self.myindexes
                #   indextuples - the tuples that describe the order in which the indexes range
                #
                #   We need to merge these as follows (for example)
                #
                #   self.var is X, self.myindexes is [i,j], representing X_i_j
                #   sets is [J,K,I]
                #   indexes is [j,k,i]
                #   tuples is [[0,0,0], [1,2,3], [4,5,6]]
                #
                #   we need to get indexes for X 0 0, X 3 1, X 6 4
                #
                # Finally - an index could have a leading " (and we would expect it to end in ")
                # which is an explicit set element. In that case we need to look up the element
                # in the set over which the var is defined, find the offset, and then augment the
                # tuples that have been passed to suit
                #

                # TODO - we also permit formulae where the


                # We will start by handling explicit elements
                for offset, i in enumerate(self.myindexes):
                    if i[0] == '"':
                        if i[-1] != '"':
                            raise ValueError(f"Error: Expecting closing quote in index {i} for variable {self.var} on {self.statementline}.")

                        # Get the corresponding set and look up the index
                        theset = dvarhandler.sets[self.var][offset]
                        theoff = dvarhandler.setmanager.cge_sets.elements[theset].index(i[1:-1]) # need to strip off the quotes at either end

                        # append the set and the offsets

                        indexes = indexes + [i]
                        sets = sets + [theset]
                        indextuples = [tup + [theoff] for tup in indextuples]

                # Figure out which sets are aligned to each of the indexes I'm defined over

                indexes_of_sets = [indexes.index(idx) for idx in self.myindexes]
                sets_to_fetch = [sets[i] for i in indexes_of_sets]

                # TODO - this could be slow
                tuples_reordered = []
                for tup in indextuples:
                    tuples_reordered.append([tup[i] for i in indexes_of_sets])

                # We could be looking up either a dvar or an svar, depending on if we are doing
                # a classic formula or perhaps an update

                isdvar = False

                if self.var in dvarhandler:
                    isdvar = True
                else:
                    isdvar = False

                if (svarhandler is not None) and (self.var in svarhandler):
                    issvar = True
                else:
                    issvar = False

                if isdvar:
                    idxlist = dvarhandler.get_index_list(self.var, sets_to_fetch, tuples_reordered)
                elif issvar:
                    idxlist = svarhandler.get_index_list(self.var, sets_to_fetch, tuples_reordered)
                else:
                    raise ValueError(f"Could not find the variable {self.var} as either a Datavar nor a Solvar")


                if evalvec is None:
                    if isdvar:
                        return [dvarvals[i] for i in idxlist]
                    else:
                        return [svarvals[i] for i in idxlist]
                else:
                    retval = [fillval] * len(indextuples)
                    for i in range(len(indextuples)):
                        if evalvec[i]:
                            if isdvar:
                                retval[i] = dvarvals[idxlist[i]]
                            else:
                                retval[i] = svarvals[idxlist[i]]
                    return retval




            elif self.operator == "sum":
                # The index and set that we are taking the sum over is contained as a 2 element list in the left node
                thisindex = self.indexandset[0]
                thisset = self.indexandset[1]
                thissetlen = dvarhandler.setmanager.get_size(thisset)

                if evalvec is None:
                    retval = [0] * len(indextuples)

                    for i in range(thissetlen):
                        newtuples = [tuple(list(sublist) + [i]) for sublist in indextuples]
                        retval = [x+y for x,y in zip(retval, self.branch.evaluate(dvarhandler, svarhandler, sets + [thisset], indexes + [thisindex], newtuples, dvarvals, svarvals, fillval = 0))]
                    return retval

                else:
                    raise ValueError("Sums in ifs not currently handled")

            elif self.operator == "if":


                # first, we need to evaluate the self.condlhs, self.condrhs and apply self.condop
                lhs = self.condlhs.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals)
                rhs = self.condrhs.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals)

                # now build a vector of true and false depending on the self.condop
                truefalse = []
                for l, r in zip(lhs,rhs):
                    append = False
                    if self.condop == "==":
                        if l == r:
                            append = True
                    elif self.condop == "!=":
                        if l != r:
                            append = True
                    elif self.condop == "<":
                        if l < r:
                            append = True
                    elif self.condop == ">":
                        if l > r:
                            append = True
                    elif self.condop == "<=":
                        if l <= r:
                            append = True
                    elif self.condop == ">=":
                        if l >= r:
                            append = True
                    truefalse.append(append)

                retval = self.branch.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = truefalse, fillval=fillval)

                return retval

            elif self.operator == "loge":


                retval = [math.log(i) for i in self.branch.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval=fillval)]

                return retval


            elif self.operator == "^":

                if evalvec is None:
                    return [x ** y for x,y in zip (self.left.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.right.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                else:
                    retval = [fillval] * len(indextuples)
                    x = self.left.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                    y = self.right.evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                    for i in range(len(evalvec)):
                        if evalvec[i]:
                            retval[i] = x[i] ** y[i]

            elif self.operator in ['==','!=','<','>','>=','<=']:

                if evalvec is None:
                    if self.operator == '==':
                        return [x == y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                    elif self.operator == '!=':
                        return [x != y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                    elif self.operator == '<':
                        return [x < y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                    elif self.operator == '>':
                        return [x > y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                    elif self.operator == '>=':
                        return [x >= y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                    else: # <=
                        return [x <= y for x,y in zip (self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals),  self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals))]
                else:
                    retval = [fillval] * len(indextuples)
                    x = self.branches[0].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                    y = self.branches[1].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                    for i in range(len(evalvec)):
                        if evalvec[i]:

                            if self.operator == '==':
                                retval[i] = (x[i] == y[i])
                            elif self.operator == '!=':
                                retval[i] = (x[i] != y[i])
                            elif self.operator == '<':
                                retval[i] = (x[i] < y[i])
                            elif self.operator == '>':
                                retval[i] = (x[i] > y[i])
                            elif self.operator == '>=':
                                retval[i] = (x[i] >= y[i])
                            else: # <=
                                retval[i] = (x[i] <= y[i])

            elif isinstance(self.operator, list):

                if self.operator[0] in "+-":
                    initval = 0
                else:
                    initval = 1

                if evalvec is None:
                    vals = [initval] * len(indextuples)
                else:
                    vals = [fillval] * len(indextuples)
                    for i in range(len(evalvec)):
                        if evalvec[i]:
                            vals[i] = initval

                for i in range(len(self.operator)):
                    if self.operator[i] == "+":
                        if evalvec is None:
                            vals = [x + y for x,y in zip (vals, self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, fillval = 0))]
                        else:
                            y = self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 0)
                            for i in range(len(evalvec)):
                                if evalvec[i]:
                                    vals[i] = vals[i] + y[i]

                    elif self.operator[i] == "-":
                        if evalvec is None:
                            vals = [x - y for x,y in zip (vals, self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, fillval = 0))]
                        else:
                            y = self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 0)
                            for i in range(len(evalvec)):
                                if evalvec[i]:
                                    vals[i] = vals[i] - y[i]

                    elif self.operator[i] == "*":
                        if evalvec is None:
                            vals = [x * y for x,y in zip (vals, self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, fillval = 1))]
                        else:
                            y = self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                            for i in range(len(evalvec)):
                                if evalvec[i]:
                                    vals[i] = vals[i] * y[i]

                    elif self.operator[i] == "/":
                        if evalvec is None:
                            vals = [x / y for x,y in zip (vals, self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, fillval = 1))]
                        else:
                            y = self.branches[i].evaluate(dvarhandler, svarhandler, sets, indexes, indextuples, dvarvals, svarvals, evalvec = evalvec, fillval = 1)
                            for i in range(len(evalvec)):
                                if evalvec[i]:
                                    vals[i] = vals[i] / y[i]

                return vals
            else:
                raise ValueError(f"Unknown operator: {self.operator}")
        except Exception as e:
            raise type(e)(str(e) + f" - Evaluating statement name {self.statementname} on line {self.statementline}. {self}\n")



    def differentiate(self, svarmanager, dvarmanager, setsin, indexesin, indextuplesin, dvarvals, deep = 0):

        # For either a + or a - we merge the two lists, looking for collisions in svar
        # offsets (and fail if we find them)

        # For a * we have to merge the lists, using the branch that has an svar as the
        # guide

        # For a sum we have to use the new index/set to expand the indexes and sets
        # and build new trees

        # The structure returned from this is a list of 2-element lists
        # Element 1     - the svar that this differential relates to
        # Element 2     - a list of statementnode structures
        #   Element 2.1 - a list of the sets that the node is defined over
        #   Element 2.2 - the indexes tied to those sets
        #   Element 2.3 - the tuple (in index order) that the statement node is defined over
        #   Element 2.4 - the statement node that is the root of this part of the differential

        # The final differential for each svar is the sum of element 2

        sets = copy.deepcopy(setsin)
        indexes = copy.deepcopy(indexesin)
        indextuples = copy.deepcopy(indextuplesin)

        # basic arithmetic will have an operator variable that is a list
        if isinstance(self.operator, list):
            if self.operator[0] in '+-':
                diffedbranches = []

                # Take the derivative of each branch
                for i in self.branches:
                    tempdiff = i.differentiate(svarmanager, dvarmanager, sets, indexes, indextuples, dvarvals, deep = deep + 1)
                    diffedbranches.append(tempdiff)


                # If this branch is subtracted, replace it with 0 - branch
                for i in range(len(diffedbranches)): # TODO THIS IS CLUNKY - IS IT THOUGH????? A: Yeah, it is
                    if self.operator[i] == "-":
                        temp = []
                        for j in diffedbranches[i]:
                            twigs = []
                            for k in j[1]:
                                # Here we are building out all the potential set/index/tuple twigs
                                twigs.append([k[0], k[1], k[2], StatementNode(0, k[0], k[1]) - k[3]])
                            temp.append([ j[0], twigs ])

                        diffedbranches[i] = temp


                # TODO REDUNDANT
                retdifflist = []
                for i in diffedbranches:
                    retdifflist = retdifflist + i



            elif self.operator[0] in '*/':
                # Rules for the multiplicative operators
                # - There can be only one branch with svars - we arent implementing the product rule
                # - The division operator may only be applied to dvars - we aren't implementing the quotient rule

                # Differentiate each branch
                diffedbranches = []
                for i in self.branches:
                    tempdiff = i.differentiate(svarmanager, dvarmanager, sets, indexes, indextuples, dvarvals, deep = deep + 1)
                    diffedbranches.append(tempdiff)

                # Here we need to take the cartesian product of the twigs
                # This will need each branch to be broken down into a list of twigs

                twiglists = []
                for i in diffedbranches:
                    twiglists.append([]) # Start a new empty set for this branch
                    # Each branch could contain data pertaining to a range of svars, dvars. Want to break them into individual parts.
                    for j in i: # IE - for everything that is differentiated by an svar
                        for k in j[1]: # IE, for every list that gives a S/I/T combination
                            twiglists[-1].append([j[0], [k]])

                cart = list(itertools.product(*twiglists))

                # A real benefit of this approach is that now we can guarantee that every element
                # of the product has only a single S/I/T twig per branch we are multiplying

                retdifflist = []
                for i in cart:

                    # check theres only one svar per product combination, and get the offset
                    # Also double check that we arent doing the quotient nor product rule anywhere

                    svarcount = 0
                    newnode = StatementNode(1.0, self.sets, self.indexes)

                    # have to keep track of the supremum sets and index
                    finalsets = []
                    finalindexes = []
                    finaltuple = []

                    for j in range(len(i)):
                        if self.operator[j] == "*":
                            newnode = newnode * i[j][1][0][3] # 1 - the S/I/T lists, 0 because it is guaranteed to only have a single element, 3 is the node
                        else:
                            if i[j][0] is None: # ie, we will only divide by a dvar or number, not an svar
                                newnode = newnode / i[j][1][0][3]
                            else:
                                raise ValueError(f"Error - encountered quotient rule while differentiating statement {self.statementname} on line {self.statementline}")

                        if i[j][0] is not None:
                            svarcount = svarcount + 1
                            svaroffset = j

                        tempindexes, tempsets = mergeindexandsets(finalindexes, i[j][1][0][1], finalsets, i[j][1][0][0])
                        if tempindexes != finalindexes:
                            finalindexes = tempindexes
                            finalsets = tempsets
                            if len(finaltuple) < len(i[j][1][0][2]):
                                finaltuple = i[j][1][0][2]

                    if svarcount > 1:
                        raise ValueError(f"Error - encountered product rule while differentiating statement {self.statementname} on line {self.statementline}")
                    elif svarcount == 1:
                        svar = i[svaroffset][0]
                    else:
                        svar = None

                    retdifflist = retdifflist + [ [svar, [[finalsets, finalindexes, finaltuple, newnode ]]] ]


            else:
                raise ValueError(f"Unexpected leading operator {self.operator[0]} differentiating {self.equationstringorig} on line {self.statementline}.")

        elif self.operator == 'if':

            # Need to evaluate the condition, and if it is true we return the differential of the branch
            # otherwise return zero

            # first, we need to evaluate the self.condlhs, self.condrhs and apply self.condop
            lhs = self.condlhs.evaluate(dvarmanager, None, sets, indexes, indextuples, dvarvals, None)
            rhs = self.condrhs.evaluate(dvarmanager, None, sets, indexes, indextuples, dvarvals, None)

            # now build a vector of true and false depending on the self.condop
            truefalse = []
            for l, r in zip(lhs,rhs):
                append = False
                if self.condop == "==":
                    if l == r:
                        append = True
                elif self.condop == "!=":
                    if l != r:
                        append = True
                elif self.condop == "<":
                    if l < r:
                        append = True
                elif self.condop == ">":
                    if l > r:
                        append = True
                elif self.condop == "<=":
                    if l <= r:
                        append = True
                elif self.condop == ">=":
                    if l >= r:
                        append = True
                else:
                    raise ValueError(f"Error - encountered unknown operator {self.condop}")
                truefalse.append(append)

            retdifflist = []
            for tf, idx in zip(truefalse, indextuples):
                if tf:
                    retdifflist = retdifflist + self.branch.differentiate(svarmanager,
                                                                          dvarmanager,
                                                                          sets,
                                                                          indexes,
                                                                          [idx], dvarvals,
                                                                          deep = deep + 1)
                else:
                    retdifflist = retdifflist + [[None, [[sets, indexes, idx, StatementNode(0, sets, indexes)]]]]


        elif self.operator == 'sum':

            # When we encounter a sum we need to expand out the sets, indexes, and index tuples, and then
            # differentiate the branch underneath with respect to each of the index tuples
            newindex = self.indexandset[0]
            newset = self.indexandset[1]

            newsetsize = svarmanager.setmanager.get_size(newset)

            newtuples = []
            for i in indextuples:
                for j in range(newsetsize):
                    newtuples.append(i + [j])

            retdifflist = []
            for i in newtuples:
                diffedbranches = self.branch.differentiate(svarmanager,
                                                            dvarmanager,
                                                            sets + [newset],
                                                            indexes + [newindex],
                                                            [i], dvarvals,
                                                            deep = deep + 1)

                retdifflist = retdifflist + diffedbranches

        elif self.operator == 'num':
            # This is the simplest of the cases - we simply return the number as a (new) statementnode
            retdifflist = [[None, [[sets, indexes, i, StatementNode(self.value, sets, indexes)]]] for i in indextuples]

        elif self.operator == 'var':
            # In the case of a var we need to get the solution variable offsets that relate to this var, in the order
            # that they occur given the sets and indexes that we have neen passed.

            # We also need to know if its a solution variable or a data variable

            # Step 1 - figure out which sets are aligned to each of the indexes I'm defined over
            # note also - we could have explicit elements which won't correspond to an index.

            # To handle explicit elements we will alter the indexes and tuples, inserting a dummy
            # index and a fixed new element in the tuples - ie:
            # variable A_r_s, r=REG, s=REG
            # incoming index is r over REG, tuple [0]
            # Equation has A_r_"aus"
            # We'll modifyt the incoming index and tuple and create a shadow copy that look like
            # r,s, tuple [0,0]
            # note! We will have to first find what the second set is for A (ie, the s) and also
            # look up the explicit element in that set.
            # Finally, what is returned is in reference to the original indexes and tuples, not the
            # shadow copies

            issvar = False
            isdvar = False
            if self.var in svarmanager.names:
                issvar = True
                definedsets = svarmanager.sets[self.var]
            elif self.var in dvarmanager.names:
                isdvar = True
                definedsets = dvarmanager.sets[self.var]
            else:
                raise ValueError(f"Error - cannot find {self.var} as either a solution nor a data variable")

            # Get some new dummy indexes to use in place of the explicit element. Ensure we done have a collision with an existing index.
#            dummys = ['a', 'b','c','d','e','f','g','h','i','j','k','l','m']
#            filtereddummys = [item for item in dummys if item not in indexes]


            shadowindexes = indexes
            shadowsets = sets
            shadowtuples = indextuples
            # sweep through and find anything in quotes, add index, set, tuple element as required

            # I don't want to modify the parent
            indextuples = copy.deepcopy(indextuples)


            try:

                indexes_of_sets = []
                for num, idx in enumerate(self.myindexes):
                    # We are going to use the type to differentiate purpose
                    # if indexes_of_sets
                    if idx[0] != '"':
                        indexes_of_sets.append(indexes.index(idx)) # this will be an int
                    else:
                        indexes_of_sets.append(definedsets[num]) # this will be a string


                sets_to_fetch = []
                for i in indexes_of_sets:
                    if isinstance(i, str):
                        sets_to_fetch.append(i)
                    else:
                        sets_to_fetch.append(sets[i])

#                indexes_of_sets = [shadowindexes.index(idx) for idx in self.myindexes]
                #sets_to_fetch = [shadowsets[i] for i in indexes_of_sets]



            except:
                raise ValueError(f"Error aligning sets and indexes when trying to take differential for statement {self.equationstringorig} on line {self.statementline}. Got indexes of {self.myindexes}.")

            # TODO - this could be slow
            tuples_reordered = []
            for tup in indextuples:
                tuples_reordered.append([])
                for num, i in enumerate(indexes_of_sets):
                    if isinstance(i, str):
                        tuples_reordered[-1].append(dvarmanager.setmanager.cge_sets[sets_to_fetch[num]].get_idx(self.myindexes[num][1:-1]))
                    else:
                        tuples_reordered[-1].append(tup[i])

            if issvar:

                # When returning an svar, the lists returned are:
                # - the svar offset
                # - the sets over which we are defined
                # - the index tuple that this pertains to
                # - the root of the tree
                #
                # NOTE - The index and sets in elements 1 and 2 of each of the lists below are the index and sets for the
                #        node, not for the svar! That is, if the equation being evaluated is over i=I, j=J, but the
                #        indexes are swapped for this leave (eg, x_j_i) then this is handled through perturbation of
                #        the index list
                #
                indexlist = svarmanager.get_index_list(self.var, sets_to_fetch, tuples_reordered)
                indexlisttuple = zip(indexlist, indextuples) # This is where the perterbation happens - its the indexes from the reordered tuples
                                                         # against the original indexes for the node
                retdifflist = [[i[0], [[sets, indexes, i[1], StatementNode(1, sets, indexes)]]] for i in indexlisttuple]

            else:
                # When returning a dvar, the lists returned are:
                # - None - this signals there is no svar
                # - the sets over which we are defined
                # - the index tuple that this pertains to
                # - the root of the tree
                #
                # NOTE - Again we need to perterb this - this is achieved by passing the reordered tuples into element 2
                #        of the lists
                #

                # Also - we need to dummy back in the replaced indexes, ie, we can't go using equationstringorig
                eqnstr = self.var
                for i in indexes_of_sets:
                    eqnstr = eqnstr + "_" + self.indexes[i]

                retdifflist = [[None, [[sets, indexes, i, StatementNode(eqnstr, sets, indexes)]]] for i in indextuples]

        elif self.operator == 'loge':
            # We only permit logs of dvars, not svars - ie, they are constants
            retdifflist = [[None, [[sets, indexes, i, StatementNode(self.equationstringorig, sets, indexes)]]] for i in indextuples]

        else:
            raise ValueError(f"Unexpected operator {self.operator} differentiating {self.equationstringorig} on line {self.statementline}.")

        # Now, sweep through the returned value and merge anything where there is the same svar


        # TODO misshapen lists



        # get the list of svars that we're looking at
        svarlist = []
        for i in retdifflist:
            if i[0] not in svarlist:
                # dvars are treated a little different - we hold onto them as values in case they are needed further up the tree
                # The can be identified by having an svar offset that is None (ie, the first element)
                # If we've reached the top of the tree however we don't want to return them, ie, they arent a
                # partial derivative with respect to any of the actual svars
                if not (deep == 0 and i[0] is None):
                    svarlist.append(i[0])

        mergedret = [[i, []] for i in svarlist]


        # For each possible svar (ie, each entry in mergedret), we will iterate
        # through the diff list, see if we match the svar, and then for each match we will
        # find a (potential) corresponding set, index, tuple combination and
        for i in mergedret:

            for j in retdifflist:

                if i[0] == j[0]:
                    # We have an svar match. Now look for a set/index/tuple match.

                    # Need to do a double loop. At the first level we will look through the s/i/t
                    # combinations in the retdifflist - as this is the one where if we don't find a match
                    # in i[1] we need to add it

                    for jtwig in j[1]:
                        matched = False
                        for itwig in i[1]:
                            if (jtwig[0] == itwig[0]) and (jtwig[1] == itwig[1]) and (jtwig[2] == itwig[2]):
                                matched = True
                                itwig[3] = itwig[3] + jtwig[3]
                        if not matched:
                            # Didnt find it, must append
                            i[1].append(jtwig)



        return mergedret














class StatementManager(object):
    '''
    This is the base class for a FormulaManager, an EquationManager, and an AssertManager
    '''
    def __init__(self,setmanager,datavarmanager):

        self.datavarmanager = datavarmanager # datavar manager needed by both derived classes
        self.setmanager = setmanager # set manager needed by both derived classes


        self.names = [] # A lists of the names of the statements that I'm holding

        self.sets = {} # A dictionary of lists of the sets (in order) over which each statement is defined
        self.indexes = {} # A dictionary of lists of the indexes (in order) over which each statement is defined

        self.rootnodes = {} # A dictionary of the root nodes for the statement trees for each statement. Names is the key.

    def add(self,statementname,statementtext,sets,indexes,statementline):

        if not isinstance(statementname, str):
            raise TypeError("add in StatementManager: Expecting string for statementname.")
        if statementname in self.names:
            raise ValueError(f"add in StatementManager: {statementname} is already an existing statement name.")


        self.names.append(statementname)
        self.sets[statementname] = sets
        self.indexes[statementname] = indexes

        self.rootnodes[statementname] = StatementNode(statementtext,sets,indexes, statementname, statementline)

    def __contains__(self, item):
        return item in self.names

class AssertManager(StatementManager):


    def add(self,statementname,statementtext,sets,indexes,statementline):

        # Check that this is actually a condition - ie, a statement that will return a bool

        # Define the possible operators as a regular expression
        operators = r'(==|<=|>=|<>|<|>)'

        matches = re.findall(operators, statementtext)
        
        if len(matches) != 1:
            raise ValueError(f"Error, could not interpret '{statementtext}' as a condition in assertion statement '{statementname}' on line {statementline}")

        # Hand the rest over to the parent class.
        super().add(statementname,statementtext,sets,indexes,statementline)


    # Check a single statement 
    # TODO can I turn this and the FormulaManager one into a helper function
    def check(self, statementname, dvarvals):
        # Get the sizes of the sets over which this assertion is defined
        sizes = [len(self.datavarmanager.setmanager.cge_sets[s]) for s in self.sets[statementname]]

        # Now we need some lists that give the element ranges over which we will vary
        # TODO change this to get_sizes
        sizelists = [list(range(s)) for s in sizes]

        # Now, we need to build the tuples over which we will evaluate
        # We need to use the itertools library for this
        # TODO - each formula really should evaluate this list at instantiation
        indextuples = list(itertools.product(*sizelists))

        # We would also like the indexes into the dvarvals that these correspond to
        # Note - we cannot simply use the indextuples from above!!
        # Because (for example) we may have an assertion defined over x=X, y=Y, with a left hand side
        # data variable that doubles up an index eg DATAVAR_x_x_y
        # The indextuples above however is the correct ordering for evaluation of the statementnode tree
        # We just need to map the indextuples through to a new set of tuples that are permuted by the
        # order of indexes in the lhsdata
        # First, get the

        # Initialise a list of empty lists of the same length as the tuples over which the formula is evaluated
#        indexlist = [() for _ in range(len(indextuples))]
        # For each index on the LHS, pick out the correct element of the tuples
#        for j, i in enumerate(self.lhsindexes[statementname]):
#            if i[0] != '"':
#                # Not an explicitly defined element
#                offset = self.indexes[statementname].index(i)
#                indexlist = [tuple(list(x) + [y[offset]]) for x,y in zip(indexlist, indextuples)]
#            else:
#                # Get the corresponding set and look up the index
#                theset = self.datavarmanager.sets[self.lhsdata[statementname]][j]
#                theoff = self.datavarmanager.setmanager.cge_sets[theset].elements.index(i[1:-1]) # need to strip off the quotes at either end
#                indexlist = [tuple(list(x) + [theoff]) for x in indexlist]

        # Finally, build the list of sets based on the indexes

#        setlist = []
#        for j,i in enumerate(self.lhsindexes[statementname]):
#            if i[0] != '"':
#                setlist.append(self.sets[statementname][self.indexes[statementname].index(i)])
#            else:
#                setlist.append(self.datavarmanager.sets[self.lhsdata[statementname]][j])

#        retindexes = self.datavarmanager.get_index_list(self.lhsdata[statementname], setlist, indexlist)

        # if we are evaluating formulas we should never care about sol vars - hence the Nones
        retvalues = self.rootnodes[statementname].evaluate(self.datavarmanager,
                                                           None,
                                                           self.sets[statementname],
                                                           self.indexes[statementname],
                                                           indextuples,
                                                           dvarvals,
                                                           None)

        # Iterate over the retvals. If we find anything that is false an assertion has failed
        # and we must raise an exception

        for i in range(len(retvalues)):
            if not retvalues[i]:
                
                settext = ""
                if indextuples[i] is not None:
                    for idx, offset in enumerate(indextuples[i]):

                        indextext = self.indexes[statementname][idx]                        
                        elementtext = self.datavarmanager.setmanager.cge_sets[self.sets[statementname][idx]].elements[offset]
                        
                        settext = settext + f"{indextext} = {elementtext}"
                        
                        if idx != len(indextuples[i]) - 1:
                            settext = settext + ", "
                    
#                raise ValueError(f"Assertion {statementname} failed, for index combination {settext}.")
                print(f"Assertion {statementname} failed, for index combination {settext}.")



        
    # Check all statement
    def check_all(self, dvarvals):
        for n in self.names:
            self.check(n, dvarvals)

class FormulaManager(StatementManager):
    '''
    FormulaManager
    '''

    def __init__(self,setmanager,datavarmanager):
        self.lhsdata = {}
        self.lhsindexes = {}
        self.modifiers = {}
        super().__init__(setmanager, datavarmanager)


    def add(self,statementname,lhs,statementtext,sets,indexes,statementline,modifiers=None):

        # Split the LHS into the datavar and the set of indexes
        lhssplit = lhs.strip().split("_")

        self.lhsdata[statementname] = lhssplit[0]
        if len(lhssplit) > 1:
            self.lhsindexes[statementname] = lhssplit[1:]
        else:
            self.lhsindexes[statementname] = []

        # The modifiers will help us determine which formulae to be evaluated when there
        # are bulk evaluations - for example, initial
        # If modifiers is none, then we always evaluate
        self.modifiers[statementname] = modifiers


        # Check consistency of the indexes in the LHS and the indexes over which the formula is applied
        # Note, we need to exclude duplicates in the indexes for the LHS, as there can be repetition
        # in indexes (eg if we are setting up something on a diagonal)
        # Note also that we exclude anything in quotes
        indexcheck = [element for element in self.lhsindexes[statementname] if '"' not in element]
        if sorted(list(set(indexcheck))) != sorted(indexes):
            raise ValueError(f'FormulaManager.add: indexes of LHS and formula definition are not consistent in {statementname}, line number {statementline}.')

        # Hand the rest over to the parent class
        super().add(statementname,statementtext,sets,indexes,statementline)

    def addloop(self, nametxt, iterations, formula_list, linenumber):

        for i in range(iterations-1):
            self.names = self.names + formula_list


    # Evaluate a single formula
    # If inplace is true, we modify the passed dvarvals list. This is the default for a
    # formula
    # If inplace is false, we return the zip of indexes and values to be updated. This will
    # be used when we are doing updates (ie, we are moving to a new vector of dvarvals)
    def evaluate(self, statementname, dvarvals, svarhandler, svarvals, inplace = True):

        # Get the sizes of the sets over which this formula is defined
        sizes = [len(self.datavarmanager.setmanager.cge_sets[s]) for s in self.sets[statementname]]

        # Now we need some lists that give the element ranges over which we will vary
        # TODO change this to get_sizes
        sizelists = [list(range(s)) for s in sizes]

        # Now, we need to build the tuples over which we will evaluate
        # We need to use the itertools library for this
        # TODO - each formula really should evaluate this list at instantiation
        indextuples = list(itertools.product(*sizelists))

        # We would also like the indexes into the dvarvals that these correspond to
        # Note - we cannot simply use the indextuples from above!!
        # Because (for example) we may have a formula defined over x=X, y=Y, with a left hand side
        # data variable that doubles up an index eg DATAVAR_x_x_y
        # The indextuples above however is the correct ordering for evaluation of the statementnode tree
        # We just need to map the indextuples through to a new set of tuples that are permuted by the
        # order of indexes in the lhsdata
        # First, get the

        # Initialise a list of empty lists of the same length as the tuples over which the formula is evaluated
        indexlist = [() for _ in range(len(indextuples))]
        # For each index on the LHS, pick out the correct element of the tuples
        for j, i in enumerate(self.lhsindexes[statementname]):
            if i[0] != '"':
                # Not an explicitly defined element
                offset = self.indexes[statementname].index(i)
                indexlist = [tuple(list(x) + [y[offset]]) for x,y in zip(indexlist, indextuples)]
            else:
                # Get the corresponding set and look up the index
                theset = self.datavarmanager.sets[self.lhsdata[statementname]][j]
                theoff = self.datavarmanager.setmanager.cge_sets[theset].elements.index(i[1:-1]) # need to strip off the quotes at either end
                indexlist = [tuple(list(x) + [theoff]) for x in indexlist]

        # Finally, build the list of sets based on the indexes
        setlist = []
        for j,i in enumerate(self.lhsindexes[statementname]):
            if i[0] != '"':
                setlist.append(self.sets[statementname][self.indexes[statementname].index(i)])
            else:
                setlist.append(self.datavarmanager.sets[self.lhsdata[statementname]][j])

        retindexes = self.datavarmanager.get_index_list(self.lhsdata[statementname], setlist, indexlist)

        # if we are evaluating formulas we should never care about sol vars - hence the Nones
        # TODO IF NOT VALID ANY MORE
        if inplace:
            retvalues = self.rootnodes[statementname].evaluate(self.datavarmanager,
                                                               svarhandler,
                                                               setlist,
                                                               self.lhsindexes[statementname],
                                                               indexlist,
                                                               dvarvals,
                                                               svarvals)
        else:
            retvalues = self.rootnodes[statementname].evaluate(self.datavarmanager,
                                                               svarhandler,
                                                               setlist,
                                                               self.lhsindexes[statementname],
                                                               indexlist,
                                                               dvarvals,
                                                               svarvals)

        if inplace:
            for i,v in zip(retindexes,retvalues):
                dvarvals[i] = v
            return None
        else:
            return list(zip(retindexes,retvalues))

    def evaluate_all_formulae(self, dvarvals, excludedmodifiers=[], asupdates=False, svarhandler=None, svarvals=None):

        # The included and excluded modifiers parameters allow us to either whitelist or blacklist particular modifiers
        # We aren't handling a circumstance where we have both a whitelist and a blacklist

        if asupdates:
            # For updates we will be constructing a new dvarvals vector from scratch based on the updates
            # Note - if we are being called as updates, we are assuming that this instance of the class is
            # storing updates not regular formulae.
            for n in self.names:
                self.evaluate(n, dvarvals, svarhandler, svarvals, inplace=True)
        else:
            for n in self.names:
                if len(set(self.modifiers[n]).intersection(set(excludedmodifiers))) == 0:
                    self.evaluate(n, dvarvals, None, None, inplace=True)


class EquationManager(StatementManager):
    '''
    EquationManager

    This is a lot like a formula manager, except in this case the order of the equations counts
    To that end it shares similarities with solution variables and data variables

    '''
    def __init__(self,setmanager,datavarmanager):


        self.fullnames = [] # A list of the full expanded names that we are holding as strings
        self.fullnamesbycolumn = [] # A list of the full expanded names that we are holding as lists [eqnname, set1, set2, ...]
        self.offsets = {} # A dictionary of offsets into the lists (key is names)
        self.indexoffsets = [] # A list of the index offsets corresponding to the full names by column (eg, numeric not alpha)
        self.sizes = {} # A dictionary of the size of each named eqnation
        self.sets = {} # A dictionary of lists of the set (in order) over which each variable is defined
        self.current_size = 0 # The current maximum extent of the variable list, which becomes the offset for any new variable which is added

        self.derivatives = [] # a list (ordered by self.fullnames) of lists of svar_offset / statement node pairs

        super().__init__(setmanager, datavarmanager)


#    def add(self, name, sets):
    def add(self, statementname,statementtext,sets,indexes,statementline):


        # Calculate the size of this equation based on the size of the sets over which it is defined
        eqnwidth = 1
        setsizes = self.setmanager.get_sizes()

        if sets:
            for i in sets:
                eqnwidth = eqnwidth * setsizes[i]

        self.offsets[statementname] = self.current_size
        self.sizes[statementname] = eqnwidth
        self.current_size = self.current_size + eqnwidth

        if sets is not None:
            setelements = [self.setmanager.cge_sets[s].elements for s in sets]
            indexoffsetelements = [list(range(self.setmanager.get_size(s))) for s in sets]
            indextuples = list(itertools.product(*setelements))
            indexoffsettuples = list(itertools.product(*indexoffsetelements))
            indexoffsettuples = [list(i) for i in list(itertools.product(*indexoffsetelements))]

            expandednames = [statementname + "_" + "_".join(i) for i in indextuples]
            namesbycol = [[statementname] + list(i) for i in indextuples]
            self.fullnames = self.fullnames + expandednames
            self.fullnamesbycolumn = self.fullnamesbycolumn + namesbycol
            self.indexoffsets = self.indexoffsets + indexoffsettuples

        else:
            self.fullnames.append(statementname)
            self.fullnamesbycolumn.append([statementname])

        super().add(statementname,statementtext,sets,indexes,statementline)




    def diffall(self, svarmanager, dvarvals):
        '''
        Evaluate all the differential trees for the set of statementnodes that sit under me
        A full set of new trees will be built that have a 1:1 correspondence to the preexisting statement nodes

        Returns
        -------
        None.

        '''

        # Iterate through each of the statement nodes
        for i in range(len(self.fullnamesbycolumn)):

            eqnname = self.fullnamesbycolumn[i][0]
            indextuple = self.indexoffsets[i]

            self.derivatives = self.derivatives + [self.rootnodes[eqnname].differentiate(svarmanager, self.datavarmanager, self.sets[eqnname], self.indexes[eqnname], [indextuple], dvarvals)]
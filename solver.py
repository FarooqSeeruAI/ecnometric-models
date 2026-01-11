# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 12:49:43 2024

@author: rober
"""
import re
import yaml
import pandas as pd
import sets

import sys
import os
import glob

import copy

import time

import variables
import statements

from scipy.sparse import identity, coo_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

try:
    from pypardiso import PyPardisoSolver
except ImportError:
    PyPardisoSolver = None

import itertools
import numpy as np

import warnings

import traceback

import csv

# A helper function for matix solution
def do_inversion(A, b, rowlabels, doiterative=False, docondense=False, solver=None):
    
    
    # Solve the linear system Ax = b
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        if docondense:
            
            t0 = time.time()
            # In this section we will be doing an automatic condensation of the matrix to solve
            # The procedure will take all rows of the matrix with a single non-zero entry, and will
            # drop the corresponding rows and columns out, as they don't need to be handled by the
            # sparse matrix solver
            
            # We will break the problem into the following:
            # - xtriv and xtriv - the trivial elements of x and b that are defined by the single non-zero entries in A
            # - Astar, bstar, xstar - the non-trivial elements
            # - a suite of mappings
            
            # Step 1 - identify the trivial rows
            
            # Calculate the number of non-zero elements in each row
            row_nz_counts = np.diff(A.indptr)
            # Identify rows with exactly one non-zero entry
            single_nz_rows = np.where(row_nz_counts == 1)[0]            
            # Identify corresponding columns
            single_nz_cols = A.indices[A.indptr[single_nz_rows]]

            # Step 2 - build the required matricies to map from original to current problem
            # These are
            #
            # - Apre - premultiplier for A to remove redundant rows/eqns. Based on I
            # - Apost - postmultiplier for A to remove redundant cols/variables. Based on I
            #         - when used as a premultiplier this will alos return xstar to the ordering of x
            
            # - xtrivpre - premultiplier for b to get xtriv. Based on A
            # - bstarpre - premultiplier for b to get bstar. Based on A
            
            # Apre
            csr_identity = identity(A.shape[0], format='csr')            
            rows_to_keep = np.setdiff1d(np.arange(csr_identity.shape[0]), single_nz_rows)
            Apre = csr_identity[rows_to_keep]
            
            # Apost
            csc_identity = identity(A.shape[1], format='csc')            
            cols_to_keep = np.setdiff1d(np.arange(csc_identity.shape[1]), single_nz_cols)
            Apost = csc_identity[:,cols_to_keep]
            
            # xtrivpre
            new_data = []
            new_row_indices = []
            new_col_indices = []
            
            for row in single_nz_rows:
                # Iterate over the row's non-zero elements
                start, end = A.indptr[row], A.indptr[row + 1]
                new_data.extend([1/x for x in A.data[start:end]])
                new_row_indices.extend([row] * (end - start))
                new_col_indices.extend(A.indices[start:end])
            
            # Create a new sparse matrix with only these rows, inverted values, and transposed
            xtrivpre = csr_matrix((new_data, (new_row_indices, new_col_indices)), shape=A.shape).T
            
            # bstarpre
            new_data = []
            new_row_indices = []
            new_col_indices = []
            
            for row in rows_to_keep:
                # Iterate over the row's non-zero elements
                start, end = A.indptr[row], A.indptr[row + 1]
                new_data.extend(A.data[start:end])
                new_row_indices.extend([row] * (end - start))
                new_col_indices.extend(A.indices[start:end])            

            bstarpre = csr_matrix((new_data, (new_row_indices, new_col_indices)), shape=A.shape)


            Atosolve = Apre @ A @ Apost
            xtriv = xtrivpre @ b
            btosolve = Apre @ (b - bstarpre @ xtriv)

            print(time.time() - t0)

        else:
            Atosolve = A
            btosolve = b
            


        print(Atosolve.shape)
        if Atosolve.shape[0] != Atosolve.shape[1]:
            if Atosolve.shape[0] > Atosolve.shape[1]:
                raise ModelException(f"Cannot solve the proposed system - there are {Atosolve.shape[0] - Atosolve.shape[1]} too many exogenous variables.")
            else:
                raise ModelException(f"Cannot solve the proposed system - there are {Atosolve.shape[1] - Atosolve.shape[0]} too few exogenous variables.")



        if doiterative:
            print("iterative")
            solver.free_memory(everything=True)
            x = solver.solve(Atosolve, btosolve).squeeze()



            
        else:
            print("not iterative")
            x = spsolve(Atosolve, btosolve)

        
        # Handle any warnings raised. We transform these into exceptions as
        # rank errors (etc) only get raised as warnings by spsolve, however for us
        # the should be fatal
        
        warningstring = ""
        if len(w) > 0:
            warningstring = "The following warnings were raised:\n"
            for warning in w:
                warningstring = warningstring + str(warning.message) + "\n"
            
            row_tuples = [tuple(A.getrow(i).toarray()[0]) for i in range(A.shape[0])]
            row_dict = {}
                
            for idx, row in enumerate(row_tuples):
                if row in row_dict:
                    row_dict[row].append(idx)  # Add index to the group of identical rows
                else:
                    row_dict[row] = [idx]  # Create a new group for this row

            identical_groups = [indices for indices in row_dict.values() if len(indices) > 1]

            if identical_groups:
                warningstring = warningstring + "\nIn addition, the following identical rows were detected:\n"
                
                for i in identical_groups:
                    for j in i:
                        warningstring = warningstring + rowlabels[j] + " "
                warningstring = warningstring + "\n"

            raise ModelException(f"Error inverting. {warningstring}")

    # Finally, if we used the condensed version we need to reconstruct the correct x vector

    if docondense:
        return (Apost @ x) + xtriv
    else:
        return x


# Implementing a cleaner exception handler to make the outputs a little more readable
def custom_exception_handler(exc_type, exc_value, exc_tb):
    # Retrieve formatted traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    
    # Remove full directory paths from the traceback
    simplified_tb = []
    for line in tb_lines:
        # Strip the full directory path from filenames using os.path.basename
        if 'File' in line:
            line = line.replace(os.getcwd(), '')  # Strip the current directory path
        simplified_tb.append(line)
    
    # Print the simplified traceback
    for line in simplified_tb:
        print(line, end='')




class ModelException(Exception):
    
    def __init__(self, message="An error occurred."):
        """
        Custom exception class for the model.
        
        Args:
            message (str): Optional. A message describing the error.
        """
        self.message = message
        super().__init__(self.message)







class Model(object):
    '''
    The Model class is a high level wrapper around a CGE model file
    '''
    
    def __init__(self, ymlfile="default.yml"):
        '''
        Initialise the Model class with default parameters, empty strings and such
        Parameters
        ----------
        ymlfile: Optional string to open the model directive yml file.
                 Default is "default.yml"

        Returns
        -------
        None.
        '''
        
        # read the yml file that will resolve 
        with open(ymlfile, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)
            except:
                raise ModelException(f"Model initialisation error: Error reading file '{ymlfile}'.")


        # Mandatory members
        self.files = yaml_data['files'] # A dictionary of filenames
        
        self.basefiles = yaml_data['basefiles'] # TODO temporary
        self.polfiles = yaml_data['polfiles'] # TODO temporary
        
        self.steps = yaml_data['steps']
        self.substeps = yaml_data['substeps']
        
        # Optional members
        
        try:
            self.solve = yaml_data['solve']
        except:
            self.solve = True
            
        try:
            self.longformat = yaml_data['longformat']
        except:
            self.longformat = True
            
        try:
            self.reportingvars = yaml_data['reportingvars']
        except:
            self.reportingvars = None
        
        try:
            self.doiterative = yaml_data['doiterative']
        except:
            self.doiterative = False
        
        self.filedata = {} # A dictionary (symbolic filename level) of dictionaries (sheet name level) of dataframes - input files only
        self.newfiles = {} # A dictionary of strings that give output file names

        self.statements = []
        
        self.set_manager = sets.CgeSetManager()
        
        self.solvarhandler = variables.SolVarHandler(self.set_manager)
        self.solvarvals = []
        
        self.datavarhandler = variables.DataVarHandler(self.set_manager)
        self.datavarvals = []
        
        self.assert_manager = statements.AssertManager(self.set_manager, self.datavarhandler)
        
        self.formula_manager = statements.FormulaManager(self.set_manager, self.datavarhandler)
        
        self.equation_manager = statements.EquationManager(self.set_manager, self.datavarhandler)
        
        self.update_manager = statements.FormulaManager(self.set_manager, self.datavarhandler)
        
        self.writes = {} # A dictionary (keyed by dvars) of file/tab combinations for writes
        
        # lists of lists of the history of dvar and svar vals
        # the highest level index is for the step, the next level is for a substep
        # An n-step solution will leave n+1 stamps for alldvarvals - the first is 
        # pre substep 0, the remainder are post each of the n steps
        # svarvals are only valid post a solution, so there are n of them
        self.allsvarvals = []
        self.alldvarvals = []
        
        
    def model_stats(self):
        
        return {'num_statements': len(self.statements)}
    
        
    def parse_model_file(self, infile_name):
        '''
        Member function to parse a model file. Splits the model up into a list
        of statements, however does very limited checking outside of leading
        keywords and trailing semicolons.
        
        Parameters
        ----------
        infile_name : string
            The name of the file to be parsed.

        Returns
        -------
        None

        '''
        
        # Step 1 - Open and read the .model file into a sequence of statements
        #
        # This step includes some light structural checking around the 'statementkeyword, statement, semicolon' structure
        # but does no syntactic checking for the statements
        
        try:
            with open(infile_name, 'r') as file:
                modellines = file.readlines()
        except FileNotFoundError:
            raise ModelException(f"Parsing error: The file '{infile_name}' was not found.")
        except Exception as e:
            raise ModelException(f"Parsing error: An error occurred: {e}")
            
        # aggregate into a sequence of statements
        # aggregated statement, lines, line numbers
        
        statement = {'line':"", 'linenumberstart': 0}
        instatement = False
        linenumber = 0
        aggregatedline = ""
        
        # Statements commence with a suitable reserved word (not in a comment), and terminate with a semicolon
        # The 'working' string is what we use to bite off the appropriate bits until we have consumed the whole line
        for i in modellines:
        
            linenumber = linenumber + 1
            
            # Comments start with a hash, and go to EOL. Strip so that we can find keywords etc
            commentsearch = re.search(r"#", i)
            if commentsearch:
                working = i[:commentsearch.span()[0]].strip()
            else:
                working = i.strip()
                    
            # We admit the possibility (though it isnt neat) of multiple statements on a single line split by one or more semicolons
            # Also a statement can span multiple lines
            
            # do while we havent finished with the current line
            while len(working) > 0:
                
                # if we are not already in a statement, the first non-whitespace should be a reserved word
                if not instatement:
                    resmatch = re.search('^(equation|formula|update|file|datavar|solvar|set|subset|write|loopformulas|assert)', working, re.IGNORECASE)
                    if not resmatch:
                        # there is something unexpected - die gracefully
                        raise ModelException(f"Parsing error, {infile_name}: Expected statement type on line {str(linenumber)}, instead encountered '{working}'.")
                    # We must now be in a statement (otherwise the previous if would have failed)
                    statement['linenumberstart'] = linenumber
                    instatement = True
                
                # End of statement is via a semicolon (not within a comment - already handled above)
                eossearch = re.search(r";", working)
                if eossearch:
                    # collect the part up to and including the semicolon
                    aggregatedline = aggregatedline + working[:eossearch.span()[0]+1]
                    # append the statement
                    statement['line'] = aggregatedline
                    statement['linenumberend'] = linenumber
                    self.statements.append(statement)
                    # reset
                    aggregatedline = ""
                    statement = {'line':""}
                    instatement = False
                    # hold onto the possible remainder
                    working = working[eossearch.span()[1]+1:]
                else:
                    aggregatedline = aggregatedline + working + " "
                    working = ""
            
        # if we get to here and we still have something in the 'aggregatedline' it means we never hit a trailing semicolon.
        # we will still remember what line that statement started on in the temporary 'statement' dictionary
        if len(aggregatedline) > 0:
            raise ModelException(f"Parsing error, {infile_name}: last statement commencing line {str(statement['linenumberstart'])} was not terminated with a semicolon")
            
            
        # Step 2 - Break the full statement list down by statement types
        
        for i in self.statements:
            # each statement should have a leading keyword, the statement, and a single trailing semicolon
            working = i['line'].strip()
            if working[-1] != ';':
                raise ModelException(f"Parsing error, {infile_name}: statement commencing line {str(i['linenumberstart'])} was not terminated with a semicolon. This exception should never be raised, please contact a developer.")
            
            keyword, statementtext = working[:-1].split(" ", maxsplit = 1)
            keyword = keyword.strip().lower()
            statementtext = statementtext.strip()
            
            # discover the keyword, and handle accordingly.
            if      keyword == 'file':
                self._parse_handle_file(statementtext, i['linenumberstart'])
            elif keyword == 'datavar':
                self._parse_handle_datavar(statementtext, i['linenumberstart'])
            elif keyword == 'solvar':
                self._parse_handle_solvar(statementtext, i['linenumberstart'])
            elif keyword == 'set':
                self._parse_handle_set(statementtext, i['linenumberstart'])
            elif keyword == 'subset':
                self._parse_handle_subset(statementtext, i['linenumberstart'])
            elif keyword == 'assert':
                self._parse_handle_assert(statementtext, i['linenumberstart'])
            elif keyword == 'update':
                self._parse_handle_update(statementtext, i['linenumberstart'])
            elif keyword == 'equation':
                self._parse_handle_equation(statementtext, i['linenumberstart'])
            elif keyword == 'formula':
                self._parse_handle_formula(statementtext, i['linenumberstart'])
            elif keyword == 'loopformulas':
                self._parse_handle_loopformulas(statementtext, i['linenumberstart'])
            elif keyword == 'write':
                self._parse_handle_write(statementtext, i['linenumberstart'])
            else:
                raise ModelException(f"Parsing error, {infile_name}: statement commencing line {str(i['linenumberstart'])} has unknown leading keyword {keyword}. This exception should never be raised, please contact a developer.")
                    
                
    def _parse_handle_file(self, statementtext, linenumber):
        
        # Two options - the file is for input in which case there is no [new] keyword
        # Specify the path to the Excel file
        
        if '[new]' in statementtext.lower():
            
            symbolicname = statementtext.strip().split()[1]
            self.newfiles[symbolicname] = self.files[symbolicname]
        else:

            # now we should be able to pick out the symbolic filename
            # TODO: Better checking of alphanumeric etc
            
            symbolicname = statementtext.strip()
    
            # Read the Excel file into a DataFrame. sheet_name is none so that we pull in all tabs
            self.filedata[symbolicname] = pd.read_excel(self.files[symbolicname], sheet_name=None)


    def _parse_handle_datavar(self, statementtext, linenumber):

        # some quick cleaning 
        text = statementtext
        while True:
            prevtext = text
            text = text.replace("  "," ")
            if prevtext == text:
                break
        text = text.strip()
        
        # TODO this should be more elegant and admit the possibility of future keywords
        # 1 - check to see if this is fixed
        fixed = False
        if "[fixed]" in text.lower():
            fixed = True
            text = text[8:]

        # 1 - check to see if this is to be read from a file
        if " from " in text.lower():
            chunks = text.split()
            vartext = chunks[0]
            filetext, nametext = chunks[2].split(".")
            
        else:
            vartext = text.strip()
            filetext = None
            nametext = None
        
        
        # 2 - split along potential sets
        chunks = vartext.strip().split("_")
        
        varname = chunks[0]
        
        if len(chunks) > 1:
            sets = chunks[1:]
            # check all the sets are defined
            for i in sets:
                if i not in self.set_manager.cge_sets:
                    raise ModelException(f"Data variable definition {statementtext} includes undefined set {i}, line {linenumber}.")
        else:
            sets = None
            
        # Before adding, need to double check that this is not already in solvars
        if varname in self.solvarhandler:
            raise ModelException(f"Data variable {varname} is already defined in solution variables, line {linenumber}.")

        self.datavarhandler.add_var(varname, sets, file=filetext, sheet=nametext,fixed=fixed)

    def _parse_handle_solvar(self, statementtext, linenumber):
        # 1 - check to see if this has a change and/or linear directive
        
        change = False
        linear = False
        
        directivematch = re.search(r"^\[[^\]]+\]", statementtext)
        if directivematch:
            directives = statementtext[1:directivematch.span()[1]-1]
            rest = statementtext[directivematch.span()[1]:]
            
            if "change" in directives.lower():
                change = True
            if "linear" in directives.lower():
                linear = True
        else:
            rest = statementtext
        
        # 2 - split along potential sets
        chunks = rest.strip().split("_")
        
        varname = chunks[0]
        
        if len(chunks) > 1:
            sets = chunks[1:]
            # check all the sets are defined
            for i in sets:
                if i not in self.set_manager.cge_sets:
                    raise ModelException(f"Variable definition {rest} includes undefined set {i}, line {linenumber}.")
        else:
            sets = None
            
        # Before adding, need to double check that this is not already in datavars
        if varname in self.datavarhandler:
            raise ModelException(f"Solution variable {varname} is already defined in data variables, line {linenumber}.")

            
        self.solvarhandler.add_var(varname, sets, change=change, linear=linear)

            
        
        
        

    def _parse_handle_set(self, statementtext, linenumber): # Done pending review

        # note: leading 'Set ' and trailing ';' are already stripped off by this point
        # Some quick tidying up
        text = statementtext.replace("(", " (").replace("="," = ")
        text = statementtext.replace("(", " (")
        while True:
            prevtext = text
            text = text.replace("  "," ")
            if prevtext == text:
                break

        # Reads are straightforward, and should come from already executed file statements
        readsearch = re.search(r" from ", text, re.IGNORECASE)
        if readsearch:
            
            
            # set read: 'Set setnamea From filename.tabname;'
            setname = text[0:readsearch.span()[0]].strip()
            rest = text[readsearch.span()[1]:].strip()
            
            filename, header = rest.split(".")
            
            self.set_manager.new_set([setname, self.filedata[filename][header]['Value'].to_list()])
            return


        # What remains must be an explicit set definition or an equals
        # Regardless - the first word must be the set name. We can strip off the =
        # if it exists, and the remainder we process right to left
        
        left, right = text.replace(" = "," ").split(maxsplit=1)
        
        # There can only be one of +, -, x in the string
        countoperators = 0
        if "+" in right:
            countoperators = countoperators + 1
        if "-" in right:
            countoperators = countoperators + 1
        if " x " in right:
            countoperators = countoperators + 1
        if countoperators > 1:
            raise ModelException("Multiple incompatible operators in set operation {statementtext}, line {linenumber}.")

        
        if re.search(r"\+", statementtext, re.IGNORECASE):
            # Handle one or more sums
            # 1 - split at " + " and tidy up    
            chunks = [i.strip() for i in right.split(" + ")]
            
            # 2 - if there are any explicitly defined sets, make them a temporary set with a temporary name,
            # add them to the data manager (for later deletion), and substitute with the set name
            
            toadd = []
            todelete = []
            index = 0
            for i in chunks:
                if i[0] == "(":
                    name = "tempset" + str(index)
                    elements = i.replace("(","").replace(")","").split(",")
                    self.set_manager.new_set([name,elements])
                    toadd.append(name)
                    todelete.append(name)
                else:
                    toadd.append(i)
                index = index + 1
                
            # 3 - add them all together
            self.set_manager.add_sets(toadd, left)
            
            # 4 - delete the temporary sets
            for i in todelete:
                self.set_manager.del_set(i)
        
            return
        
        elif re.search(r"\-", text, re.IGNORECASE):
            chunks = [i.strip() for i in right.split(" - ")]
            if len(chunks) != 2:
                raise ModelException(f"Expected exactly two sets on the right hand side of set difference {statementtext}, line {linenumber}.")
            self.set_manager.sub_sets(chunks[0], chunks[1], left)
            return
            # Handle a single subtraction
        elif re.search(r" x ", text, re.IGNORECASE):
            chunks = [i.strip() for i in right.split(" x ")]
            if len(chunks) != 2:
                raise ModelException(f"Expected exactly two sets on the right hand side of set cross product {statementtext}, line {linenumber}.")
            self.set_manager.cross_sets(chunks[0], chunks[1], left)
            return
            # Handle a single cross
        else:
            # Handle an explicit definition
            chunks = right.replace(","," ").replace("(","").replace(")","").split()
            tempset = sets.CgeSet([left,chunks])
            self.set_manager.new_set(tempset)
            return
            
        
    def _parse_handle_subset(self, statementtext, linenumber): # Done pending review
        # note: leading 'Set ' and trailing ';' are already stripped off by this point
        # Some quick tidying up
        text = statementtext.replace("(", " (").replace("="," = ")
        text = statementtext.replace("(", " (")
        while True:
            prevtext = text
            text = text.replace("  "," ")
            if prevtext == text:
                break

        chunks = text.split(" of ")
        self.set_manager.is_subset_of(chunks[0], chunks[1])


    def _parse_handle_assert(self, statementtext, linenumber):

        nametxt, setstxt, condition = statementtext.split(":", maxsplit=2)
        
        # The set/index pairs should be separated by commas
        setstxt = setstxt.strip()
        if len(setstxt) > 0:
            setssplit = setstxt.split(',')
            setssplit = [i.strip() for i in setssplit]
            indexes = [i.split("=")[0] for i in setssplit]
            sets = [i.split("=")[1] for i in setssplit]
        else:
            sets = []
            indexes = []
        
        self.assert_manager.add(nametxt, condition, sets, indexes, linenumber)


    def _parse_handle_update(self, statementtext, linenumber):
        nametxt, setstxt, updatevar, formulatxt = statementtext.split(":", maxsplit=3)

        # The set/index pairs should be separated by commas
        setstxt = setstxt.strip()
        if len(setstxt) > 0:
            setssplit = setstxt.split(',')
            setssplit = [i.strip() for i in setssplit]
            indexes = [i.split("=")[0] for i in setssplit]
            sets = [i.split("=")[1] for i in setssplit]
        else:
            sets = []
            indexes = []
        
        self.update_manager.add(nametxt, updatevar, formulatxt, sets, indexes, linenumber)

    def _parse_handle_equation(self, statementtext, linenumber):
        
        nametxt, setstxt, equationtxt = statementtext.split(":", maxsplit=2)
        
        # The set/index pairs should be separated by commas
        setstxt = setstxt.strip()
        if len(setstxt) > 0:
            setssplit = setstxt.split(',')
            setssplit = [i.strip() for i in setssplit]
            indexes = [i.split("=")[0] for i in setssplit]
            sets = [i.split("=")[1] for i in setssplit]
        else:
            sets = []
            indexes = []
        
        # break the lhs off from the rhs at the =, and subtract rhs from lhs
        lhs, rhs = equationtxt.split("=", maxsplit = 1)
        equationtxt = "( " + lhs + " ) - ( " + rhs + " )"

        self.equation_manager.add(nametxt, equationtxt, sets, indexes, linenumber)

    def _parse_handle_formula(self, statementtext, linenumber):
        
        # split off any leading modifiers
        modmatch = re.search(r"^\[[^\]]*\]", statementtext)
        if modmatch:
            modifiers = statementtext[modmatch.span()[0]: modmatch.span()[1]]
            modifiers = [i.strip().lower() for i in modifiers[1:-1].split(",")]
            # Check permitted modifiers
            permitted = ["initial"]
            violations = [i for i in modifiers if i not in permitted]
            if len(violations) != 0:
                raise ModelException(f"Error - found unexpected modifiers {violations} in statement {statementtext} on line {linenumber}.")
            statementtext = statementtext[modmatch.span()[1]:]
        else:
            modifiers = []
        nametxt, setstxt, formulatxt = statementtext.split(":", maxsplit=2)
        
        # The set/index pairs should be separated by commas
        setstxt = setstxt.strip()
        if len(setstxt) > 0:
            setssplit = setstxt.split(',')
            setssplit = [i.strip() for i in setssplit]
            indexes = [i.split("=")[0] for i in setssplit]
            sets = [i.split("=")[1] for i in setssplit]
        else:
            sets = []
            indexes = []
        
        # break the lhs off from the rhs at the =
        lhs, rhs = formulatxt.split("=", maxsplit = 1)
        

        self.formula_manager.add(nametxt, lhs, rhs, sets, indexes, linenumber, modifiers=modifiers)


    def _parse_handle_loopformulas(self, statementtext, linenumber):
        
        nametxt, iterationstxt, listtxt = statementtext.split(":", maxsplit=2)
        
        # Iterations
        try:
            iterations = int(iterationstxt)
        except:
            raise ModelException(f"Error: Could not interpret '{iterationstxt}' as an integer in statement {nametxt} on line {linenumber}.")

        # The list of formula names should be separated by commas
        listtxt = listtxt.strip()
        listsplit = listtxt.split(',')
        listsplit = [i.strip() for i in listsplit]
        
        # Check to see if each of the named formulae are already in the formlua manager
        for i in listsplit:
            if i not in self.formula_manager:
                raise ModelException(f"Error: Formula {i} named in {nametxt} on line {linenumber} is not an already defined formula.")
        self.formula_manager.addloop(nametxt, iterations, listsplit, linenumber)

    def _parse_handle_write(self, statementtext, linenumber):
        
        chunks = statementtext.strip().split()
        filename, tabname = chunks[2].split('.')
        self.writes[chunks[0]] = (filename, tabname)

    def read_datavars(self):
        self.datavarvals = self.datavarhandler.read_from_files(self.filedata)
        
        
    def do_updates(self):
        self.update_manager.evaluate_all_formulae(self.datavarvals, asupdates=True, svarhandler=self.solvarhandler, svarvals=self.solvarvals)
            
    def do_writes(self, aggregate=True, long=True):
        
        # This first section does the writes that are flagged as reporting vars
        
        # The aggregate flag allows us to either aggregate substeps up into a full step (which would be the default behaviour for applied work)
        # or to report each substep for debugging purposes
        
        # The long flag writes svars and dvars out in long format if true (grouped into an svar an a dvar tab as appropriate),
        # or writes out in the same format as the input dataframes if false
        
        
        # We are building a list of offsets here. This is in especially important when we are doing the long format, where we are building a big dataframe
        # that is a subset of the fullnames and the datavalues.
        if self.reportingvars is not None:
            svaroffsets = [index for index, sublist in enumerate(self.solvarhandler.fullnamesbycolumn) if sublist[0] in self.reportingvars]
            dvaroffsets = [index for index, sublist in enumerate(self.datavarhandler.fullnamesbycolumn) if sublist[0] in self.reportingvars]
            missingnames = [name for name in self.reportingvars if name not in list(self.solvarhandler.offsets.keys()) + list(self.datavarhandler.offsets.keys()) ]

            if len(missingnames) > 0:
                print("Warning - the following names have been listed in the reporting variables but do not appear as either a data nor a solution variable:")
                for i in missingnames:
                    print(f" -> {i}")
        else:
            svaroffsets = [index for index, sublist in enumerate(self.solvarhandler.fullnamesbycolumn)]
            dvaroffsets = [index for index, sublist in enumerate(self.datavarhandler.fullnamesbycolumn)]
            
        # We will handle the solve/don't solve by defining two different simlist options
        if self.solve == True:
            simlist = ['base','policy']
        else:
            simlist = ['nosim']

        if not long:
            # We'll be putting dataframes in a dict
            dfdict = {}
            
        for sim in simlist:

            # Here we are taking slices of the full svarvals and dvarvals based on the offsets
            if sim == 'base':
                
                svars = [
                    [
                        [substep[i] for i in svaroffsets]  
                        for substep in step
                        ]
                    for step in self.basesvarvals
                    ]
                
                dvars = [
                    [
                        [substep[i] for i in dvaroffsets]  
                        for substep in step
                        ]
                    for step in self.basedvarvals
                    ]
                
            elif sim == 'policy':
                svars = [
                    [
                        [substep[i] for i in svaroffsets]  
                        for substep in step
                        ]
                    for step in self.allsvarvals
                    ]
                
                dvars = [
                    [
                        [substep[i] for i in dvaroffsets]  
                        for substep in step
                        ]
                    for step in self.alldvarvals
                    ]
            else:
                dvars = [
                    [
                        [self.datavarvals[i] for i in dvaroffsets]  
                        ]
                    ]

            if self.solve == True:
                valheadings = ["SVAR"]
    
                # initialise the data block with the appropriate svar row data
                if long:
                    data = [[i] for i in [self.solvarhandler.fullnames[j] for j in svaroffsets]]
                else:
                    data = [i for i in [self.solvarhandler.fullnamesbycolumn[j] for j in svaroffsets]]
    
                if aggregate:
                    for s in range(len(svars)):
                        valheadings.append(f"S{s}")
                        tempdata = [0] * len(self.solvarhandler.fullnames)
                        for ss in range(len(svars[s])):
                            for i,databit in enumerate(svars[s][ss]):
                                if self.solvarhandler.change[self.solvarhandler.fullnamesbycolumn[i][0]]:
                                    tempdata[i] = tempdata[i] + databit
                                else:
                                    tempdata[i] = ((1 + tempdata[i]/100) * (1 + databit/100)) * 100 - 100
                        data = [i + [j] for i,j in zip(data, tempdata)]
                else:
                    for s in range(len(svars)):
                        for ss in range(len(svars[s])):
                            valheadings.append(f"S{s}SS{ss}")
                            if data is None:
                                data = [[i] for i in svars[s][ss]]
                            else:
                                data = [i + [j] for i,j in zip(data, svars[s][ss])]
                
                if long:
                    svardf = pd.DataFrame(data, columns=valheadings)
                else:
                    # Get the list of svar names that we are reporting
                    svarnames = list(set([i[0] for i in data]))
                    
                    # make the appropriate df and put it in our list to be dropped out
                    for i in svarnames:
                        datasnip = [j[1:] for j in data if j[0] == i]
                        if self.solvarhandler.sets[i] is not None:
                            colheadings = self.solvarhandler.sets[i] + ['Value']
                        else:
                            colheadings = ['Value']
                        dfdict[i] = pd.DataFrame(datasnip, columns=colheadings)


            
            valheadings = ["DVAR"]
            # initialise the data block with the appropriate dvar row titles
            if long:
                data = [[i] for i in [self.datavarhandler.fullnames[j] for j in dvaroffsets]]
            else:
                data = [i for i in [self.datavarhandler.fullnamesbycolumn[j] for j in dvaroffsets]]
            
            if aggregate:
                for s in range(len(dvars)):
                    valheadings.append(f"S{s}")
                    data = [i + [j] for i,j in zip(data, dvars[s][0])]
            else:
                for s in range(len(dvars)):
                    for ss in range(len(dvars[s])):
                        valheadings.append(f"S{s}SS{ss}")
                        if data is None:
                            data = [[i] for i in dvars[s][ss]]
                        else:
                            data = [i + [j] for i,j in zip(data, dvars[s][ss])]
    
            if long:
                dvardf = pd.DataFrame(data, columns=valheadings)
            else:
                # Get the list of svar names that we are reporting
                dvarnames = list(set([i[0] for i in data]))
                
                # make the appropriate df and put it in our list to be dropped out
                for i in dvarnames:
                    datasnip = [j[1:] for j in data if j[0] == i]
                    if self.datavarhandler.sets[i] is not None:
                        colheadings = self.datavarhandler.sets[i] + ['Value']
                    else:
                        colheadings = ['Value']
                    dfdict[i] = pd.DataFrame(datasnip, columns=colheadings)            
            
            with pd.ExcelWriter(sim +".xlsx", engine='openpyxl') as writer:
                if long:
                    if self.solve == True:
                        svardf.to_excel(writer, sheet_name="svars", index=False)
                    dvardf.to_excel(writer, sheet_name="dvars", index=False)        
                else:
                    for sheet_name, df in dfdict.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)


        # This second section does the write statements in the file. Here we have named logical files
        # that need to be resolved back to the physical names and write statements that need to be
        # aligned to the logical file names

        # For the write statements it doesnt make a lot of sense to do a 'long' format, as we
        # explicitly name the tabs in the write statement.

        # self.newfiles = {} # A dictionary of strings that give output file names
        # self.writes = {} # A dictionary (keyed by dvars) of file/tab combinations for writes

        # We will collect up each of the data implied by the write statements into a dictionary
        newfiledata = {}
        for i in self.newfiles.keys():
            newfiledata[i] = []
            

        for item, deets in self.writes.items():
            
            datazip = zip(self.datavarhandler.fullnamesbycolumn, self.datavarvals)
            
            # First lets see if this is a datavar
            if item in self.datavarhandler.names:
                # Build the appropriate dataframe
                if self.datavarhandler.sets[item] is not None:
                    datasnip = [j[0][1:] + [j[1]] for j in datazip if j[0][0] == item]
                    colheadings = self.datavarhandler.sets[item] + ['Value']
                else:
                    datasnip = [[j[1]] for j in datazip if j[0][0] == item]
                    colheadings = ['Value']
                    
                df = pd.DataFrame(datasnip, columns=colheadings)            
            # Second, see if its a set
            elif item in self.set_manager.cge_sets:
                df = pd.DataFrame({item:self.set_manager.cge_sets[item].elements})
                print(f"GOT {item}")
                # Handle it here
            else:
                raise ModelException(f"Error: Cannot find variable name {item} in write statement.")

            # each list entry is [tabname, dataframe]
            newfiledata[deets[0]].append([deets[1], df])


        for name, data in newfiledata.items():
            
            with pd.ExcelWriter(self.newfiles[name], engine='openpyxl') as writer:
                for [sheet_name, df] in data:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        


    def read_closure_shocks(self):
        
        
        self.baseclosures = []
        self.polclosures = []
        
        # Open and process the closures and shocks
        for borp in ['b','p']:
            
            if borp == 'b':
                files = self.basefiles
            else:
                files = self.polfiles
                
            for b in files:
                
                closure = {}
                
                with open(b, 'r') as file:
                    closurelines = file.readlines()
                    
                for c in closurelines:
                    
                    if c.strip() != "":
                        splitline = c.strip().split()
                        
                        # There are some possibilities here
                        # We could be adding a variable, removing a variable, or shocking a variable
                        if len(splitline) < 2:
                            raise ModelException(f"Error: Was expecting at least two keywords on line '{splitline}' in file {b}")
                        
                        
                        # We need to correctly interpret the variable. It could have no sets (in which case it's all elements),
                        # it could have named sets, and it could have named elements
        
                        if '_' in splitline[1]:
        
                            splitbits = splitline[1].split("_")
                            var = splitbits[0]
                            setsetc = splitbits[1:]
        
                            # First, get the sets the variable is defined over
                            variablesets = self.solvarhandler.sets[var]
        
                            # Iterate through the setsetc and pull out either the sets that are named, or the elements
                            tuplebuilder = []
                            for n, s in enumerate(setsetc):
                                if s[0] != "'":
                                    # This should be a named set.
                                    # We need to get the mapping from the elements of the named set back through
                                    # to the elements of the variable set
                                    mapping = self.set_manager.get_mapping(variablesets[n],s)
                                    if mapping is None:
                                        raise ModelException(f"Error parsing shock line '{c.strip()}' in file {b}. Unknown set {s} - did you forget quotes?")
                                    tuplebuilder.append(self.set_manager.get_mapping(variablesets[n],s))
                                else:
                                    # This is an element of the set over which the set was defined. Need to strip the quotes
                                    try:
                                        idx = self.set_manager.cge_sets[variablesets[n]].get_idx(s[1:-1])
                                    except:
                                        raise ModelException(f"Error processing line {c} in closure file {b}.")
                                    tuplebuilder.append([idx])
                                    
                            # now use itertools to build tuples
                            indextuples = list(itertools.product(*tuplebuilder))
                            
                            # Get the offsets
                            offsets = self.solvarhandler.get_index_list(var, variablesets, indextuples)
                        else:
                            var = splitline[1]
                            offsets = list(range(self.solvarhandler.offsets[splitline[1]], self.solvarhandler.offsets[splitline[1]] + self.solvarhandler.sizes[splitline[1]]))
        
            
        
        
                        if splitline[0].lower() == "add":
                            # We will warn for any variables that are repeated, but not throw an error
                            
                            intersection = list(set(closure) & set(offsets))
                            if intersection != []:
                                print(f"Warning - some elements of closure line '{c}' are already in the closure")
                                
                            for o in offsets:
                                closure[o] = [0, self.solvarhandler.ischange(var)]
        
                        elif splitline[0].lower() == "remove":
                            # Make sure that every element being removed is already in the closure
                            if list(set(offsets) - set(closure)) != []:
                                raise ModelException(f"Error - trying to remove elements that are not in the closure in line '{c}'.")
        
                            for o in offsets:
                                del closure[o]
        
                                
                        elif splitline[0].lower() == "shock":
        
                            # Make sure that every element being shocked is already in the closure
                            if list(set(offsets) - set(closure)) != []:
                                raise ModelException(f"Error - trying to shock elements that are not in the closure in line '{c}'.")
        
                            shockval = float(splitline[2])
                            for o in offsets:
                                closure[o][0] = shockval
                            
        
                        else:
                            raise ModelException(f"Error parsing shock line '{c.strip()}' in file {b}.")
                
                if borp == 'b':
                    self.baseclosures.append(closure)
                else:
                    self.polclosures.append(closure)

            




def run_model(model_file="qgem.model", do_policy = True):
    
    # Instantiate the model
    model = Model()
    
    # Read model file
    model.parse_model_file(model_file)



    
    print(f"Equations are of size {len(model.equation_manager.fullnames)}")
    print(f"Svars are of size {len(model.solvarhandler.fullnames)}")
    
    # Read the required vars
    print("Reading data vars")
    model.read_datavars()

    if model.solve == False:
        # Do any start of sim only formulae. This is all we will do before skipping over to the writes
        model.formula_manager.evaluate_all_formulae(model.datavarvals)
        
        model.assert_manager.check_all(model.datavarvals)
    else:
        # Actually solve

        print("Taking differentials")
        # Take the differentials - noting that some may be dependent on datavars (hence why it is after the evaluation of formulae)
        model.equation_manager.diffall(model.solvarhandler, model.datavarvals)
        
        
        # Read in the closure and shock files
        model.read_closure_shocks()
        
        # Solve the model
        
        if model.doiterative:
            # We need to spin up a pardiso solver
            pardisosolver = PyPardisoSolver()
        else:
            pardisosolver = None
            
            
            
        for simtype in ['base', 'policy']:
            # We are going to do 2 passes - a baseline and a policy run.
            # At the end of the baseline we will archive the simluation results (ie, the svars and dvars)
            # and then we will do the policy. The policy will draw on the archived baseline numbers
            # to determine any shocks that need to be brought over for exogenous variables
            
            
            for s in range(model.steps):
                print(f"Doing {simtype}")
                print(f"  Doing step {s}")
                for ss in range(model.substeps):
                    # Evaluate all formulae
                    if ss == 0:
                        excludedmodifiers = []
                    else:
                        excludedmodifiers = ["initial"]
    
    
        #            print("Evaluating start of substep formulae")                
                    model.formula_manager.evaluate_all_formulae(model.datavarvals, excludedmodifiers = excludedmodifiers)
                    model.assert_manager.check_all(model.datavarvals)
        
                    # Store the pre-substep dvarvals vector
                    if len(model.alldvarvals) == s: # Triggered on the first substep
                        model.alldvarvals.append([])
                    model.alldvarvals[s].append(copy.deepcopy(model.datavarvals))
            
            
        #            print("Building solution system")
                    # Build the A matrix
                    # Define row indices, column indices, and data for non-zero elements
                    row_indices = []
                    col_indices = []
                    data = []
        
                    # This is for the partial derivatives
                    for i in range(len(model.equation_manager.derivatives)):
                        for j in range(len(model.equation_manager.derivatives[i])):
                            offset = model.equation_manager.derivatives[i][j][0]
                            val = 0
                            for twig in model.equation_manager.derivatives[i][j][1]:
                                twigval = twig[3].evaluate(model.datavarhandler, None, twig[0], twig[1], [twig[2]], model.datavarvals, None)
                                val = val + twigval[0]
        
                            row_indices.append(i)
                            col_indices.append(offset)
                            data.append(val)
                            
                    # This is the closure and shocks
                    
                    # First, define the right-hand side vector for the equation Ax = b
                    # all the rhs for the equations are zeros
                    if simtype == "base":
                        closure = model.baseclosures[s]
                    else:
                        closure = model.polclosures[s]
                    
                    eqnlen = len(model.equation_manager.derivatives)
                    closurelen = len(closure)
        
#                    b = [0] * eqnlen
                    b = np.zeros(eqnlen + closurelen)
                    
                    # We will need to do 2 things here
                    # The first is that we will need to build the b vector. The ordering in this vector
                    # is determined by the ordering in the closure file
                    # The second is we need to keep hold of a list of if each variable was exogenous
                    # or endogenous in the base (by step, not substep), so that if we do a swap
                    # from baseline to policy we can adopt the baseline value in the policy
                    
                    
                    for i,j in enumerate(closure.keys()):
                        row_indices.append(i + eqnlen)
                        col_indices.append(j)
                        data.append(1)
                        
                        # If we are doing the policy run, we need to get the value that this variable
                        # took on in the base run.
                        if simtype == "policy":
                            baseval = model.basesvarvals[s][ss][j]
                        else:
                            # We'll just dummy in a zero so that we don't have to do two seperate calculations
                            # in the next step
                            baseval = 0
                        
                        
                        
                        if closure[j][1]: # Element 1 is true if the variable is a change variable, false if not
                            b[i + eqnlen] = baseval + (closure[j][0] / model.substeps)
#                            b.append(baseval + (closure[j][0] / model.substeps))
                        else:
                            b[i + eqnlen] = ((1 + baseval / 100) * (1+ closure[j][0] / 100) ** (1 / model.substeps)) * 100 - 100
#                            b.append(((1 + baseval / 100) * (1+ closure[j][0] / 100) ** (1 / model.substeps)) * 100 - 100)
        
        
        
                    # Define the shape of the matrix
                    shape = (len(model.equation_manager.fullnames) + len(closure), len(model.solvarhandler.fullnames))
                    
                    # Create a sparse matrix in COO format
                    sparse_matrix = coo_matrix((data, (row_indices, col_indices)), shape=shape)
                    
                    # Convert the sparse matrix to CSR format
                    csr_matrix = sparse_matrix.tocsr()
                    
        
                    
                    # Define labels and data
                    rowlabels = model.equation_manager.fullnames + [model.solvarhandler.fullnames[i] for i in closure] 
                    collabels = model.solvarhandler.fullnames


                    zero_row_indices = np.where(csr_matrix.getnnz(axis=1) == 0)[0]
                    if len(zero_row_indices) > 0:
                        print("Caught the following equations with no non-zero derivatives:")
                        for i in zero_row_indices:
                            print(f"   {model.rowlabels[i]}")
        
                    zero_row_indices = np.where(csr_matrix.getnnz(axis=0) == 0)[0]
                    if len(zero_row_indices) > 0:
                        print("Caught the following equations with no non-zero derivatives:")
                        for i in zero_row_indices:
                            print(f"   {collabels[i]}")


                    x = do_inversion(csr_matrix, b, rowlabels, doiterative=model.doiterative, docondense=False, solver=pardisosolver)

                    # Solve the linear system Ax = b
                    # with warnings.catch_warnings(record=True) as w:
                    #     warnings.simplefilter("always")

                    #     if model.doiterative:
                    #         print("iterative")
                    #         x = pypardiso.spsolve(csr_matrix, b)
                            
                    #     else:
                    #         print("not iterative")
                    #         x = spsolve(csr_matrix, b)

                    #     warningstring = ""
                        
                    #     if len(w) > 0:
                    #         warningstring = "The following warnings were raised:\n"
                    #         for warning in w:
                    #             warningstring = warningstring + str(warning.message) + "\n"
                            
                    #         row_tuples = [tuple(csr_matrix.getrow(i).toarray()[0]) for i in range(csr_matrix.shape[0])]
                    #         row_dict = {}
                                
                    #         for idx, row in enumerate(row_tuples):
                    #             if row in row_dict:
                    #                 row_dict[row].append(idx)  # Add index to the group of identical rows
                    #             else:
                    #                 row_dict[row] = [idx]  # Create a new group for this row
    
                    #         identical_groups = [indices for indices in row_dict.values() if len(indices) > 1]
    
                    #         if identical_groups:
                    #             warningstring = warningstring + "\nIn addition, the following identical rows were detected:\n"
                                
                    #             for i in identical_groups:
                    #                 for j in i:
                    #                     warningstring = warningstring + rowlabels[j] + " "
                    #             warningstring = warningstring + "\n"
            
                    #         raise ModelException(f"Error inverting. {warningstring}")
                    
                    # Report the residual
                    Ax = csr_matrix.dot(x)
                    res = np.linalg.norm(Ax - b)
                    print(f"Residual norm is {res}")
        
                    model.solvarvals = list(x)
        
                    # Keep history of the svarvals       
                    if len(model.allsvarvals) == s: # Triggered at the end of the first substep
                        model.allsvarvals.append([])
                    model.allsvarvals[s].append(list(x))
                    
                    # Do updates
                    model.do_updates()
                    model.assert_manager.check_all(model.datavarvals)
                    
            if simtype == "base":
                # Archive the svars, dvars, reset the model
                model.basedvarvals = copy.deepcopy(model.alldvarvals)
                model.basesvarvals = copy.deepcopy(model.allsvarvals)
                
                model.alldvarvals = []
                model.allsvarvals = []
                
                model.solvarvals = []
                model.datavarvals = []
                
                model.read_datavars()
            
            
    model.do_writes(long=model.longformat)

    # end of step. Evaluate the final formulae, and do the updates





# =============================================================================
#
# This block of code is here for some temporary testing - writing out the very low
# level A, b
#
#
#             import openpyxl
#             from openpyxl import Workbook
# 
#             # Create a new Excel workbook and select the active worksheet
#             wb = Workbook()
#             ws = wb.active
# 
#             print("a")
#             
#             data = x
#             
#             print("b")
# 
#             # Write labels to the first row
#             for col, label in enumerate(collabels, start=2):
#                 ws.cell(row=1, column=col, value=label)
#             
#             print("c")
# 
#             # Write data to the first col
#             for row, value in enumerate(rowlabels, start=2):
#                 ws.cell(row=row, column=1, value=value)
#             
#             # Write the matrix
#             for row in range(len(model.equation_manager.fullnames) + len(closure)):
#                 for col in range(len(model.equation_manager.fullnames) + len(closure)):
#                     ws.cell(row=row+2, column=col+2, value=csr_matrix[(row,col)])            
# 
#             print("d")
#             # write the x vector
#             for row, value in enumerate(x, start=2):
#                 ws.cell(row=row, column=len(collabels) + 3, value=value)
#             
# 
#             print("e")
#             # write the b vector
#             for row, value in enumerate(b, start=2):
#                 ws.cell(row=row, column=len(collabels) + 6, value=value)
#             
#             print("f")
#             # Save the workbook to a file
#             wb.save('labels_and_data.xlsx')
#             
#             print("g")
# =============================================================================





    
    
    
if __name__ == "__main__":
    
    # Set the custom exception handler
    sys.excepthook = custom_exception_handler    

    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        if not os.path.exists(model_name):
            print(f"Unable to locate model file '{model_name}'.")
            model_name = None
    # Check if 'qgem.model' exists in the current directory
    elif os.path.exists('qgem.model'):
        model_name = 'qgem.model'
    # Check if there is exactly one file with the .model extension in the current directory
    else:
        model_files = glob.glob("*.model")
        if len(model_files) == 1:
            model_name = model_files[0]
        else:
            model_name = None

    if model_name is not None:
        print(f"Running model {model_name}")
        run_model(model_file = model_name)
    else:
        print("Not able to identify a suitable model file. Exiting.")
    


    
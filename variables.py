# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:47:31 2024

@author: rober
"""

import itertools


class VarHandler(object):
    '''
    Class to handle the common elements of variable handling. Used as the base
    class for SolVarHandler and DataVarHandler and not really designed to
    have direct use otherwise
    
    This class doesn't maintain the values that the variables may take on
    '''
    
    def __init__(self, setmanager=None):
        self.setmanager = setmanager
        self.names = [] # A list of the names that we are holding. I'd like to maintain order (hence not just keys of the dicts for the vars that follow)
        self.fullnames = [] # A list of the full expanded names that we are holding as strings
        self.fullnamesbycolumn = [] # A list of the full expanded names that we are holding
        self.offsets = {} # A dictionary of offsets into the values (key is names)
        self.sizes = {} # A dictionary of the size of each named variable
        self.sets = {} # A dictionary of lists of the set (in order) over which each variable is defined
        
        
        self.current_size = 0 # The current maximum extent of the variable list, which becomes the offset for any new variable which is added

    def add_var(self, name, sets):
        if isinstance(sets, list) or sets is None:
            if isinstance(name, str):
                # Check to see if this name is already in, fail if so
                if name in self.names:
                    raise ValueError(f"add_var: Attempt to insert duplicate variable name: '{name}'")
                    
                # Calculate the size of this variable based on the size of the sets over which it is defined
                varwidth = 1
                setsizes = self.setmanager.get_sizes()
                
                if sets:
                    for i in sets:
                        varwidth = varwidth * setsizes[i]

                self.names.append(name)                        
                self.offsets[name] = self.current_size
                self.sizes[name] = varwidth
                self.sets[name] = sets
                self.current_size = self.current_size + varwidth

                if sets is not None:
                    setelements = [self.setmanager.cge_sets[s].elements for s in sets]
                    indextuples = list(itertools.product(*setelements))
                    
                    expandednames = [name + "_" + "_".join(i) for i in indextuples]
                    namesbycol = [[name] + list(i) for i in indextuples]
                    self.fullnames = self.fullnames + expandednames
                    self.fullnamesbycolumn = self.fullnamesbycolumn + namesbycol
                else:
                    self.fullnames.append(name)
                    self.fullnamesbycolumn.append([name])
                        
                        
            else:
                raise TypeError(f"add_var: Unsupported operand type for name, expecting string: '{format(type(name))}'")
        else:
            raise TypeError(f"add_var: Unsupported operand type for sets, expecting list of set strings or None: '{format(type(sets))}'")

    def get_index_list(self, name, sets, instances):
        '''
        This function takes on a variable name, the sets over which the instances of indexes are ranging (noting
        that they may be subsets of the sets over which the variables are actually defined), and the list of instances
        of the index tuples (noting that we have no guarantees about which variable is ranging the fastest)
        and builds them into a list of offsets into the master variable list that refers to each individual offset

        Parameters
        ----------
        name : String
            The name of the variable that we are going to be indexing.
        sets : None or list of strings
            The sets that the variable is being asked to range over.
        instances : None (if there are no sets) or a list of tuples (of the same size as sets)
            The tuples that give the offsets into each set that we are ranging over.

        Returns
        -------
        A list of integers that give the offsets into the variable list.

        '''

        # Some quick type etc checking on the way in
        if not isinstance(name, str):
            raise TypeError(f"get_index_list: Unsupported operand type for name, expecting string: '{format(type(name))}'")
        
        if not (sets is None or isinstance(sets, list)):
            raise TypeError(f"get_index_list: Unsupported operand type for sets, expecting None or list of strings: '{format(type(sets))}'")
            
        if not (instances is None or isinstance(instances, list)):
            raise TypeError(f"get_index_list: Unsupported operand type for instances, expecting None or list of ints: '{format(type(instances))}'")

        if ((sets is None) and (instances is not None)) or ((sets is not None) and (instances is None)):
            raise TypeError(f"get_index_list: Expected sets and instances to either both be None, or neither be None: '{format(type(sets))}', '{format(type(instances))}'")

        if name not in self.names:
            raise ValueError(f"get_index_list: Could not find variable {name}")

        if sets is None:
            insetslen = 0
        else:
            insetslen = len(sets)
            
        if self.sets[name] is None:
            mysetslen = 0
        else:
            mysetslen = len(self.sets[name])
        if insetslen != mysetslen:
            raise ValueError(f"get_index_list: Variable {name} ranging over sets {sets} inconsistent with defined sets {self.sets[name]}\n")
        
        # If its width 1 this is super easy - though remember we need to return a vector as long as the instances passed in
        
        if mysetslen == 0:
            return([self.offsets[name]] * len(instances))

        # First, get the mappings from the sets over which we are expected to range and the sets over which the variable is defined
        setsizes = self.setmanager.get_sizes()
        setpairs = [i[:2] for i in self.setmanager.mappings]


        mymappings = []
        mysizes = []
        for i in range(len(sets)):
            # If its the native set, just a zip over the set size
            if sets[i] == self.sets[name][i]:
                mymappings.append([j for j in range(setsizes[sets[i]])])
            else:
                try:
                    index = setpairs.index([self.sets[name][i], sets[i]])
                except:
                    raise ValueError(f"Error resolving mapping from set {sets[i]} to {self.sets[name][i]} for variable {name}.")
                mymappings.append(self.setmanager.mappings[index][2])
            mysizes.append(setsizes[self.sets[name][i]])


        result = []
        
        # Iterate over each instance in instances ASDF
        for instance in instances:
            temp = []
            
            # Iterate over indices i from 0 to mysetslen-1
            for i in range(mysetslen):
                # Access elements from mymappings using instance[i] as an index for each inner list
                temp.append(mymappings[i][instance[i]])
            
            # Append the temporary list to the result list
            result.append(temp)
        
        # result now contains the expanded list


        
        transformedinstances = [[mymappings[i][instance[i]] for i in range(mysetslen)] for instance in instances]
        baseoffset = self.offsets[name]
        indexoffsets = []
        # These offsets will ensure that the offsets behave a bit like regular
        # representation of numbers
        # eg, hundreds, tens, units
        # So - the leftmost index has the biggest "jumps" in the list, whereas the
        # rightmost index behaves more like units and only moves by 1
        for i in range(mysetslen):
            indexoffset = 1
            for j in range(i+1,mysetslen):
                indexoffset = indexoffset * mysizes[j]
            indexoffsets.append(indexoffset)
        
        indexes = [baseoffset + sum([ti[i] * indexoffsets[i] for i in range(mysetslen)]) for ti in transformedinstances]
        return(indexes)
            
    def __contains__(self,item):
        return item in self.names




class DataVarHandler(VarHandler):
    
    def __init__(self, setmanager=None):
        super().__init__(setmanager)
        self.files_and_sheets = {} # A dictionary of the file and sheet that this should be read from
        self.fixed = {} # A dictionary indicating if this datavar is fixed or not
    
    def add_var(self, name, sets, file=None, sheet=None, fixed=False):
        super().add_var(name,sets)
        if not ((file is None and sheet is None) or (isinstance(file,str) and isinstance(sheet,str))):
            raise TypeError(f"add_var (DataVarHandler): Unsupported operand types for file and/or sheet, expected Nones or strings, got '{format(type(file))}' and '{format(type(sheet))}'")
        if not isinstance(fixed,bool):
            raise TypeError(f"add_var (DataVarHandler): Unsupported operand type for fixed, bool, got '{format(type(fixed))}'")

        self.files_and_sheets[name]=[file,sheet]
        self.fixed[name] = fixed
            
    def read_from_files(self, files):
        
        # This reads all the values from the files and returns a list of all dvars
        # including those that are zeros (ie not read)
        
        if not isinstance(files,dict):
            raise TypeError(f"read from files: Unsupported operand types for files, expected dict, got '{format(type(files))}'.'")
            
        retvect = []

        for i in self.names:
            file, sheet = self.files_and_sheets[i]
            # Not every datavar is read from a file, those that are not will have Nones
            if file:
                # We cannot guarantee that the order in the file will match our needs
                # (in fact no reason to believe it will), nor that every value will be
                # present (which we should warn about).
                # So, we will read, reindex, sort, reset index, and convert NaNs to zeros
                # and warn as required
                
                # TODO implement wanings for missing values
                # TODO check column names are correct
                
                try:
                    workingdf = files[file][sheet]
                except:
                    raise ValueError(f"read_from_files - Could not find data {sheet} in file {file}.")
                
                # If it has no dimension (ie, a single value) then we can just get the value
                
                if self.sets[i]:
                    # build a list of tuples that match our desired order
                    
                    temp = [self.setmanager.cge_sets[j].elements for j in self.sets[i]]
                    
                    # if there is only a single set (ie, temp is len 1) then the product below
                    # will give us a list of single element tuples, but the reindex doesnt like that,
                    # it just wants a list of strings
                    if len(temp) == 1:
                        indexorder = temp[0]
                    else:
                        # Note!!! The * operator below unpacks the unknown number of lists that
                        # are packed up in temp and passes them as individual arguments to the list function
                        indexorder = list(itertools.product(*temp))
                    
                    try:
                        # multiindex, set order to the product above, and reset the index
                        df_multiindex = workingdf.set_index(workingdf.columns[:-1].tolist())
                        df_reordered = df_multiindex.reindex(list(indexorder))
                        df_reordered.reset_index(inplace=True)
                    except:
                        raise ValueError(f"read_from_files - Error reprocessing header {i}. Is there a mismatch between the dimensions defined in the model file and the dimensions in {file}?")
                        
                    if df_reordered['Value'].isna().any():
                        raise ValueError(f"read_from_files - Missing values detected when reading header {i}.")
                    values = df_reordered['Value'].tolist()
                else:
                    values = [workingdf['Value'].loc[0]]
            else:
                values = [0] * self.sizes[i]
                
            # A check - the length of the values list should match our precalculated length
            # If not something has gone badly wrong!!!
            if len(values) != self.sizes[i]:
                raise ValueError(f"read_from_files - read vector length doesnt match predetermined length for variable {i}.")
                            
            retvect = retvect + values    
            
        return retvect
                    
            
class SolVarHandler(VarHandler):
    
    def __init__(self, setmanager=None):
        super().__init__(setmanager)
        self.change = {}
        self.linear = {}
            
    def add_var(self, name, sets, change=False, linear=False):
        super().add_var(name,sets)
        if not (isinstance(change,bool) and isinstance(linear,bool)):
            raise TypeError(f"add_var (SolVarHandler): Unsupported operand types for change and/or linear, expected bools, got change:'{format(type(change))}' and linear:'{format(type(linear))}'")
        self.change[name] = change
        self.linear[name] = linear
        
    def ischange(self, name):
        return self.change[name]
            
            
            
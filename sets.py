# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 09:37:31 2024

@author: rober
"""



class CgeSet(object):
    
    def __init__(self, value = None):
        # Can initialise a few different ways
        if value is None:
            self.name = "EmptySet"
            self.elements = []
        elif isinstance(value, CgeSet):
            self.name = value.name
            self.elements = value.elements
        elif isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and isinstance(value[1], list):
            self.name = value[0]
            self.elements = value[1]
        else:
            raise TypeError("Unsupported operand type for set initialisation: '{}'".format(type(value)))
            
    def __add__(self, other):
        if isinstance(other, CgeSet):
            if len(self.elements + other.elements) == len(set(self.elements + other.elements)):
                return CgeSet(["(" + self.name + ")PLUS(" + other.name + ")", self.elements + other.elements])
            else:
                raise ValueError(f"Duplicate entries detected as a result of set union: '{self.name}'='{self.elements}' and '{other.name}'='{other.elements}'")
        else:
            raise TypeError("Unsupported operand type for +: 'CgeSet' and '{}'".format(type(other)))

    def __sub__(self, other):
        if isinstance(other, CgeSet):
            # check other is a subset of self
            if other < self:
                return CgeSet(["(" + self.name + ")MINUS(" + other.name + ")", [i for i in self.elements if i not in other.elements]])
            else:
                raise ValueError(f"Difference of sets impossible, {other.name} is not a subset of {self.name}: '{self.name}'='{self.elements}' and '{other.name}'='{other.elements}'")
        else:
            raise TypeError("Unsupported operand type for -: 'CgeSet' and '{}'".format(type(other)))

    def __mul__(self, other):
        if isinstance(other, CgeSet):
            retList =  [i + j for i,j in [(i,j) for i in self.elements for j in other.elements]]
            # Check for duplicate entries by converting to a set and comparing lengths
            if len(retList) != len(set(retList)):
                raise ValueError(f"Cross product of sets resulting in duplicate entries: '{self.name}'='{self.elements}' and '{other.name}'='{other.elements}'")
            return CgeSet(["(" + self.name + ")CROSS(" + other.name + ")", retList])
        else:
            raise TypeError("Unsupported operand type for *: 'CgeSet' and '{}'".format(type(other)))

    def __lt__(self, other):
        if isinstance(other, CgeSet):
            return all(i in other.elements for i in self.elements)
        else:
            raise TypeError("Unsupported operand type for <: 'CgeSet' and '{}'".format(type(other)))

    def __gt__(self, other):
        if isinstance(other, CgeSet):
            return all(i in self.elements for i in other.elements)
        else:
            raise TypeError("Unsupported operand type for >: 'CgeSet' and '{}'".format(type(other)))

    def __eq__(self, other):
        if isinstance(other, CgeSet):
            return self.elements == other.elements
        else:
            raise TypeError("Unsupported operand type for ==: 'CgeSet' and '{}'".format(type(other)))

    def __len__(self):
        return(len(self.elements))
    
    def get_map(self, other):
        '''
        Get a mapping by index from the elements of this set into the elements of a superset passed as parameter

        Parameters
        ----------
        other : CgeSet
            The superset that we are mapping into

        Returns
        -------
        List of element offsets.

        '''
        # Check type
        if isinstance(other, CgeSet):
            # First, check that self is a subset of other
            if self < other:
                mapping = []
                for i in self.elements:
                    mapping.append(other.elements.index(i))
                return mapping
            else:
                raise ValueError(f"Cannot map from set {self.name} to set {other.name} unless {self.name} is a subset of {other.name}: '{self.name}'='{self.elements}' and '{other.name}'='{other.elements}'")
        else:
            raise TypeError("Unsupported operand type for get_map: ''{}'".format(type(other)))

    def rename(self, name):
        if isinstance(name, str):
            return CgeSet([name, self.elements])
        else:
            raise TypeError(f"Unsupported operand type for rename: '{format(type(name))}'")
            
    def get_idx(self, element):
        if isinstance(element, str):
            try:
                idx = self.elements.index(element)
                return idx
            except:
                raise ValueError(f"Couldn't get index for element {element} in set {self.name} with elements {self.elements}.")
        else:
            raise TypeError(f"Unsupported operand type for get_idx: '{format(type(element))}'")

    def __repr__(self):
        return f'CgeSet({self.name}={self.elements})'




class CgeSetManager(object):

    def __init__(self):
        self.cge_sets = {} # dictionary of CgeSet objects
        self.mappings = [] # list of set name (super set), set name (sub set), mapping
        
    def new_set(self, inset):
        # Check types
        if isinstance(inset, list) and ((isinstance(inset[0], str) and isinstance(inset[1], list))):
            name = inset[0]
            elements = inset[1]
        elif isinstance(inset, CgeSet):
            name = inset.name
            elements = inset.elements
        else:
            raise TypeError(f"Unsupported operand type for new_set: {format(type(inset))}.")
        # Check we don't already have a set by that name
        if name not in self.cge_sets.keys():
            # Got it
            self.cge_sets[name] = CgeSet([name,elements])
        else:
            raise TypeError(f"Attempting to add a duplicate set name: {name}.")
        
    def del_set(self, inset):
        
        temp = [i for i in self.cge_sets]
        if not inset in temp:
            raise ValueError(f"Error deleting set: {inset} is not a known set.")
    
        # remove the set
        del self.cge_sets[inset]
        
        # remove any mappings that refer to that set
        tempmapping = []
        for i in self.mappings:
            if (not i[0] == inset) and (not i[1] == inset):
                tempmapping.append(i)
        self.mappings = tempmapping
        
    
    def is_subset_of(self, subset, superset):
        if isinstance(subset, str) and isinstance(superset, str):
            # check that we have both those set names
            if subset not in self.cge_sets.keys():
                raise ValueError(f"Cannot create set relationship, unknown set '{subset}'.")

            if superset not in self.cge_sets.keys():
                raise ValueError(f"Cannot create set relationship, unknown set '{superset}'.")
                
            self.mappings = self._combine_relations(self.mappings, [superset, subset, self.cge_sets[subset].get_map(self.cge_sets[superset])])
                
        else:
            raise TypeError(f"Unsupported operand type for is_subset_of: '{format(type(subset))}' and '{format(type(superset))}'")

    def get_size(self, setname):
        if setname in self.cge_sets:
            return(len(self.cge_sets[setname].elements))
        else:
            raise ValueError(f"Error getting size of set {setname}, set not found.")
            
    def get_sizes(self):
        return dict([(name, len(self.cge_sets[name].elements)) for name in self.cge_sets])
            
            
    def _combine_relations(self, masterrelations, newrelation):
        '''
        
    
        Parameters
        ----------
        relationA : TYPE
            DESCRIPTION.
        relationB : TYPE
            DESCRIPTION.
    
        Returns
        -------
        relationC : TYPE
            DESCRIPTION.
    
        '''
        
        # Step 1 - Check to see if this relationship already exists
        # if it does, check the relationship is already the same
        # if it is, return unmodified master
        # if it is not, return fatal error
        
        # strip off the relations, I dont want to check for equality of relations, sets only
        setsonlymaster = [lst[0:2] for lst in masterrelations]
        setsonlynew = newrelation[0:2]
        try:
            inlist = setsonlymaster.index(setsonlynew)
            if masterrelations[inlist] == newrelation:
                # reduntant, return
                return(masterrelations)
            else:
                # fatal error
                raise ValueError(f"{newrelation} does not match current relationship entry {masterrelations[inlist]}")
        except: # TODO: Change to only catch ValueError. Anything else would be unexpected.
            # it must be new, continue
            pass
        
        
        # the new one is the combination of master, new, and the relationships defined by transitivity of the subset relationship
        # eg - B < A and C < B implies that C < A
        
        transitiverelations = []

        for i in masterrelations:
            # Is the superset of our new relationship a subset of an existing relationship?
            if i[1] == newrelation[0]:
                # If it is, then merge the two and append
                transitiverelations.append([i[0], newrelation[1], [i[2][j] for j in newrelation[2]]])
        
        # Now - must iterate through the newly generated transitive relationships, find collisions, and 
        # strip them after ensuring they are consistent
        
        # Collisions are not an error and will happen all the time
        
        collidedrelations = masterrelations + [newrelation] + transitiverelations
        cleanrelations = []
        for i in collidedrelations:
            setsonlyclean = [j[0:2] for j in cleanrelations]
            try: 
                inlist = setsonlyclean.index(i[0:2])
                # found it - make sure they are consistent
                if i != cleanrelations[inlist]:
                    raise ValueError(f"Mapping collision: {i} is inconsistent with relationship entry {cleanrelations[inlist]}")
            except:
                cleanrelations.append(i)


        return cleanrelations


    def add_sets(self, sets, newsetname):
        if isinstance(sets, list) and isinstance(newsetname, str):
            # check that we have those set names
            for i in sets:
                if not i in self.cge_sets.keys():
                    raise ValueError(f"Cannot add sets, unknown set '{i}'.")

            if newsetname in self.cge_sets.keys():
                raise ValueError(f"Cannot add sets, new set name already taken '{newsetname}'.")

                            

            tempset = CgeSet()
            for i in sets:
                tempset = tempset + self.cge_sets[i]
            self.cge_sets[newsetname] = tempset.rename(newsetname)

            for i in sets:
                self.is_subset_of(i, newsetname)
            
                
        else:
            raise TypeError(f"Unsupported operand type for add_sets: '{format(type(sets))}', '{format(type(newsetname))}'")


    def sub_sets(self, superset, subset, newset):
        if isinstance(superset, str) and isinstance(subset, str) and isinstance(newset, str):
            # check that we have both those set names
            if superset not in self.cge_sets.keys():
                raise ValueError(f"Cannot subtract sets, unknown set '{superset}'.")

            if subset not in self.cge_sets.keys():
                raise ValueError(f"Cannot subtract sets, unknown set '{subset}'.")
                
            if newset in self.cge_sets.keys():
                raise ValueError(f"Cannot subtract sets, new set name already taken '{newset}'.")
                
            self.cge_sets[newset] = (self.cge_sets[superset] - self.cge_sets[subset]).rename(newset)

            self.is_subset_of(newset, superset)

                
        else:
            raise TypeError(f"Unsupported operand type for add_sets: '{format(type(superset))}', '{format(type(subset))}, '{format(type(newset))}'")



    def cross_sets(self, seta, setb, newset):
        if isinstance(seta, str) and isinstance(setb, str) and isinstance(newset, str):
            # check that we have both those set names
            if seta not in self.cge_sets.keys():
                raise ValueError(f"Cannot cross sets, unknown set '{seta}'.")

            if setb not in self.cge_sets.keys():
                raise ValueError(f"Cannot cross sets, unknown set '{setb}'.")
                
            if newset in self.cge_sets.keys():
                raise ValueError(f"Cannot cross sets, new set name already taken '{newset}'.")
                
            self.cge_sets[newset] = (self.cge_sets[seta] * self.cge_sets[setb]).rename(newset)

    def get_mapping(self, superset, subset):
        if superset != subset:
            retval = None
            for m in self.mappings:
                if m[0] == superset and m[1] == subset:
                    retval = m[2]
        else:
            retval = list(range(len(self.cge_sets[superset])))
        return retval

    def __repr__(self):
        return f"CgeSetManager(\n\t{self.cge_sets}\n\n\t{self.mappings}\n)"


    def __contains__(self, item):
        return item in self.cge_sets


if __name__ == "__main__":


    # Check assignment operators
    set1 = CgeSet()
    set2 = CgeSet(["name",["Val1", "Val2"]])
    set3 = set2
    set4 = CgeSet(["name2",["Val1"]])    
    set5 = set2 - set4
    print(set5)

    seta = CgeSet(["namea",["Val1"]])    
    setb = CgeSet(["nameb",["Val2"]])    
    setc = CgeSet(["namec",["Val3"]])    


    set_manager = CgeSetManager()
    set_manager.new_set(["SETA", ["A","B","C","D","E"]])
    set_manager.new_set(["SETB", [    "B",    "D"    ]])
    set_manager.new_set(["SETC", [        "C","D"    ]])
    set_manager.new_set(["SETD", [            "D"    ]])
    set_manager.new_set(["SETE", [                "E"]])
    
    
    # B < A
    set_manager.is_subset_of("SETB", "SETA")
    print("B < A - Current state is: " + str(set_manager) + "\n\n")

    # C < A
    set_manager.is_subset_of("SETC", "SETA")
    print("C < A - Current state is: " + str(set_manager) + "\n\n")
    
    # D < B  ---> D < A
    set_manager.is_subset_of("SETD", "SETB")
    print("D < B - Current state is: " + str(set_manager) + "\n\n")
    
    # D < C  ---> D < A collision
    set_manager.is_subset_of("SETD", "SETC")
    print("D < C - Current state is: " + str(set_manager) + "\n\n")
    

    set_manager.add_sets(["SETD", "SETE"], "SETF")
    print("F = D + E - Current state is: " + str(set_manager) + "\n\n")
    
    set_manager.sub_sets("SETC", "SETD", "SETG")
    print("G = C - D - Current state is: " + str(set_manager) + "\n\n")
    
    set_manager.cross_sets("SETD", "SETE", "SETH")
    print("H = D * E - Current state is: " + str(set_manager) + "\n\n")
    
    
    print("SETD" in set_manager)
    print("XXXSETD" in set_manager)
    
    


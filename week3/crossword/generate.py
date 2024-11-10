import sys
from PIL import Image, ImageDraw, ImageFont
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        garbage = {}
        for var, words_list in self.domains.items():
            for word in words_list:
                if len(word)!=var.length:
                    if var not in garbage:
                        garbage[var]=[]
                    garbage[var].append(word)
        for var,words_list in garbage.items():
            for word in words_list:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x,y]==None:
            return False
        
        else:
            conflictArea = self.crossword.overlaps[x,y]
            garbage=set()

            for word_x in self.domains[x]:
                is_garbage = True
                for word_y in self.domains[y]:
                    if word_x[conflictArea[0]]==word_y[conflictArea[1]]:
                        is_garbage=False
                if is_garbage: 
                    garbage.add(word_x)
            
            if len(garbage) == 0:
                return False

            for word in garbage:
                self.domains[x].remove(word)        
            
            return True

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    arcs.append((x,y))
        
        while len(arcs):
            arc = arcs.pop(0)
            x=arc[0]
            y=arc[1]
            if self.revise(x, y):
                if self.domains[x]==0:
                    return False
                
                x_neighbors = self.crossword.neighbors(x)
                for x_neighbor in x_neighbors :
                    if x_neighbor != y:
                        arcs.append((x_neighbor,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Complete if all variables are assigned to a value
        # Assignment dictionary has all variables
        return len(self.domains) == len(assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        value_set = set()
        for var, value in assignment.items():
            if value not in value_set:
                value_set.add(value)
            else:
                return False

            if var.length != len(value):
                return False

            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    (index_x, index_y) = self.crossword.overlaps[var, neighbor]
                    if value[index_x] != assignment[neighbor][index_y]:
                        return False
            
        return True
            
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """


        result = {}
        neighbors = self.crossword.neighbors(var)

        for value in self.domains[var]:
            result[value] = 0
            for other_var in self.domains:
                if other_var == var or other_var in assignment:
                    continue
                if value in self.domains[other_var]:
                    result[value]+=1

            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                else:
                    (i,j)= self.crossword.overlaps[var,neighbor]
                    for word in self.domains[neighbor]:
                        if word[j] != value[i]:
                            result[value]+=1
        
        return sorted(result, key = result.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        result_var= None

        for var in self.domains:
            if var in assignment:
                continue
        
            if result_var is None or len(self.domains[var]) < len(self.domains[result_var]):
                result_var=var
            
            elif len(self.domains[var]) == len(self.domains[result_var]) and \
                len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(result_var)):
                result_var=var
            
        return result_var


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        domain = self.order_domain_values(var,assignment)
        for value in domain:
            assignment[var]=value
            if not self.consistent(assignment):
                assignment.pop(var)
                continue
            else:
                self.ac3()
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                assignment.pop(var)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

import sys
import string
from enum import Enum

# Represents a object responsible for simplifying logical expressions
class Simplifier(object):
    
    def __init__(self):
        pass

    # Simplifies a given expression mainly using the Quine-McCluskey algorithm
    def simplify(self, expression):
        return "LUL"


# Represents a valid in term of logical rules (or not) expression
class Expression(object):

    def __init__(self, user_input):
        self.__content = user_input
        self.__is_valid = self.__check_validity()

    # Indicates the validity of the expression
    def is_valid(self):
        return self.__is_valid

    # Checks whether or not a given logic expression is valid    
    def __check_validity(self):
        # Set the attributes to desired values
        allowed_binary_operators = "^&|/>"
        allowed_constatns = "TF"
        allowed_variables = string.ascii_lowercase
        
        # The number of brackets must not fall below 0 at any time
        brackets_count = 0
        
        # Helper class(enum) used for better readability of this method
        class State(Enum):
            EXPECTING_VAR = 1
            EXPECTING_OP = 2

        # First we expect to see a variable/constant/opening bracket
        state = State.EXPECTING_VAR

        # Go through all characters in the expression
        for token in self.__content:
            # If the next char is expected to be an operator then if it really is
            # an operator then swtich the state else if its a variable indicate 
            # invalidity
            if state == State.EXPECTING_OP:
                if token == '~':
                    return False
                elif token in allowed_binary_operators:
                    state = State.EXPECTING_VAR
                elif token in allowed_variables + allowed_constatns + '(':
                    return False
            # Similarly here, only the other way around
            elif state == State.EXPECTING_VAR:
                if token == '~':
                    continue
                elif token in allowed_variables + allowed_constatns:
                    state = State.EXPECTING_OP
                elif token in ')' + allowed_binary_operators:
                    return False
            # Remark: If we expect an operator we cannot encounter a negation but
            # if we expect a variable we can
            
            # Check if the brackets are still balanced
            if token == '(':
                brackets_count += 1
            if token == ')':
                brackets_count -= 1
            if brackets_count < 0:
                return False
        
        # If the brackets are balanced at the end and we do not expect a variable
        # then the expression is valid
        return brackets_count == 0 and state == State.EXPECTING_OP


# Utility class used to store various useful methods
class Utils(object):

    # Removes all unnecessary whitespaces from an expression
    @staticmethod
    def remove_whitespaces(expression):
        return "".join(expression.split())


def main():
    # Read a single logical expression from the user, then check its validity,
    # if its a proper expression proceed to simplyfing it else signalize an 
    # error an abort the procedure
    user_input = Utils.remove_whitespaces(input("Please provide an expression: "))
    expression = Expression(user_input)
    if(expression.is_valid()):
        print(Simplifier().simplify(expression))
    else:
        print("ERROR")

if __name__ == "__main__":
    main()
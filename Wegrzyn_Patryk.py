# Programowanie w jezyku Python 2018
# Autor: Wegrzyn Patryk

import sys
import string
from enum import Enum

# Represents a object responsible for simplifying logical expressions
class Simplifier(object):
    
    def __init__(self, expression):
        self.__current_exp = expression
        self.__current_raw_exp = expression.get_content()
        self.__allowed_binary_operators = "^&|/>"
        self.__allowed_constatns = "TF"
        self.__allowed_variables = string.ascii_lowercase
        self.__op_prio = \
            {'~': 4, '(': 0, ')': 1, '^': 3, '&': 2, '|': 2, '/': 2, '>': 1 }

    # Generates all the possible values for a given variable set
    def gen_binary(self, n):
        return [bin(i)[2:].rjust(n, "0") for i in range(2**n)]

    # Generates all the minterms for a given expression
    def get_minterms(self, expression):
        raw_exp = expression.get_content()
        vars = "".join(list(expression.get_variables()))
        return [bin for bin in self.gen_binary(len(vars)) \
            if self.eval_rpn(self.map_values(self.to_rpn(raw_exp), vars, bin))]

    # Converts an expression to RPN form (postfix) using the Shunting-Yard algorithm
    def to_rpn(self, raw_exp):
        allowed_terms = self.__allowed_variables + self.__allowed_constatns
        allowed_ops = self.__allowed_binary_operators
        queue = []
        stack = []
        
        # Get ride of the outermost brackets
        expression = self.strip_brackets(raw_exp)
        for token in expression:
            
            # If it'a allowed term (variable or constant) then add it to the queue
            if token in allowed_terms:
                queue.append(token)
            
            # Same with the negation operator since it's unary and behaves like
            # a function
            elif token == "~":
                stack.append(token)
            
            #
            elif token in allowed_ops:
                while stack and self.__op_prio[stack[-1]] >= self.__op_prio[token]:
                    queue.append(stack.pop())
                stack.append(token)
            
            # If left brackets is encountered just add it to the stack
            elif token == "(":
                stack.append(token)
            
            # If a closing bracket is encountered move operators from the top of
            # the stack to the queue as long as you don't encounter an opening
            # bracket, if you eventually do, just pop it of the stack
            elif token == ")":
                while stack and stack[-1] != "(":
                    queue.append(stack.pop())
                stack.pop()
        
        # Move the operators from the stack to the result queue
        while stack:
            if stack[-1] != "(":
                queue.append(stack.pop())
            else:
                stack.pop()
        return "".join(queue)

    # Evaluates a given RPN-formed expression with only 1,0 literals (no vars)
    def eval_rpn(self, rpn_exp):
        def imp(a, b):
            return int((not a) | b)
        def nand(a, b):
            return int(not(a & b))
        stack = []
        for token in rpn_exp:
            if token in "10":
                stack += [int(token)]
            elif token == "|":
                stack += [stack.pop(-1) | stack.pop(-1)]
            elif token == "&":
                stack += [stack.pop(-1) & stack.pop(-1)]
            elif token == "^":
                stack += [stack.pop(-1) ^ stack.pop(-1)]
            elif token == ">":
                b, a = (stack.pop(-1), stack.pop(-1))
                stack += [imp(a, b)]
            elif token == "~":
                stack += [not stack.pop(-1)]
            elif token == "/":
                b, a = (stack.pop(-1), stack.pop(-1))
                stack += [nand(a, b)]
        return stack[0]

    # Maps a given set of variable values to the according variables in an
    # expression, for example map_values("a&b>c&T", "abc", "101") -> "1&0>1&1"
    def map_values(self, raw_exp, vars, vals):
        buffer = list(raw_exp)
        for i in range(len(buffer)):
            for v in enumerate(vars):
                if buffer[i] == v[1]:
                    buffer[i] = vals[v[0]]
            if buffer[i] == "T":
                buffer[i] = "1"
            if buffer[i] == "F":
                buffer[i] = "0"
        return "".join(buffer)

    # Removes all outermost brackets
    def strip_brackets(self, raw_exp):
        while raw_exp[0] == "(" and raw_exp[-1] == ")" and Expression.check_validity(raw_exp[1:-1]):
            raw_exp = raw_exp[1:-1]
        return raw_exp

    # Determines the priority of an operator
    def get_operator_priority(self, op):
        return self.__op_prio[op]

    # Simplifies a given expression mainly using the Quine-McCluskey algorithm
    def simplify(self):
        
        # Initialize the required variables
        expression = self.__current_exp
        expression_raw = self.__current_raw_exp
        variables = "".join(list(expression.get_variables()))
        
        # If there is no variables then the expression consists only of constants
        # and we can evalueate it immidietly
        if not variables:
            imm_res = self.eval_rpn(self.map_values(self.to_rpn(expression_raw), variables, ""))
            if imm_res == 0:
                return "F"
            elif imm_res == 1:
                return "T"
        
        # Get the minterms of the expression
        minterms = self.get_minterms(expression)
        
        # If no minterms could be found the the expression is always False
        if not minterms:
            return "F"
        
        # If the found unique terms cover all the combinations of the variables
        # then the expression is always true
        elif len(minterms) == 2**len(variables):
            return "T"
        return expression_raw


# Represents a valid in term of logical rules (or not) expression
class Expression(object):

    def __init__(self, user_input):
        self.__content = user_input
        self.__is_valid = self.check_validity(user_input)
        self.__variables = self.retrieve_variables(user_input)

    # Retrieves all unique variables from an expression in ascending order
    @staticmethod
    def retrieve_variables(raw_exp):
        return sorted(set([var for var in raw_exp if var in string.ascii_lowercase]))
    
    # Returns the set of unique variables
    def get_variables(self):
        return self.__variables
    
    # Retrieves the actual content
    def get_content(self):
        return self.__content
    
    # Indicates the validity of the expression
    def is_valid(self):
        return self.__is_valid

    # Checks whether or not a given logic expression is valid    
    @staticmethod
    def check_validity(raw_exp):
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
        for token in raw_exp:
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
        print(Simplifier(expression).simplify())
    else:
        print("ERROR")

if __name__ == "__main__":
    main()
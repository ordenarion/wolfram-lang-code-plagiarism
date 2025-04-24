import re

class WolframPreprocessor:
    def __init__(self):
        self.blocks = []
        self.k = 6
        self.element_list = ["ClearAll", "Clear", "Plot", "Plot3D","Import","Export"]
        self.functions_naive = [self.remove_space, self.remove_expressions,
                                self.add_missing_semicolumns, self.remove_brackets, self.remove_long_dashes,
                                self.parse_names, self.get_replace_vars, self.concat_digits, self.proccess_part, self.process_rules, lambda x: self.process_kless(x, self.k)]
        with open("./wolfram_specs/functions.txt", "r") as f:
            self.inner_functions = f.read().split("\n")
        with open("./wolfram_specs/syntax_rules.txt", "r") as f:
            self.rules = f.read().split("\n")
        
        self.rules_params = sorted([[string[0], [item for item in string[1:]], string, len(string) - 1] for string in self.rules], key=lambda x: x[-1], reverse=True)
    #1. Удаление пробелов
    def remove_space(self, input_string):
        return input_string.replace(" ", "")
    #2. Удаление ненужных функций
    def remove_expressions(self, input_string):
        elements_pattern = '|'.join(re.escape(element) for element in self.element_list)
        pattern = r'\b(?:' + elements_pattern + r')\s*\[\S*?\]|Null|\b(?:' + elements_pattern + r')\s*\[\S*?\]\s*;|\b(?:' + elements_pattern + r')\s*,\s*Null\s*,\s*'
        result = re.sub(pattern, '', input_string)
        
        return result.replace("(;)","").replace("(];)","")
    #3. Добавление в конце выражений ;
    def add_missing_semicolumns(self, input_string):
        stack = []
        semicolumn_positions = []
        for id, symb in enumerate(input_string):
            if symb != ")":
                stack.append(symb)
            else:
                searchQ = True
                bracket_position = id
                while len(stack) > 0 and stack[-1] != "(":
                    current = stack.pop(-1)
                    if searchQ:
                        if current == "=" and input_string[bracket_position-1] != ";":
                            semicolumn_positions.append(bracket_position)
                            searchQ = False
                else:
                    if len(stack) > 0:
                        stack.pop(-1)

        if len(semicolumn_positions) > 0:
            idx = [[0, semicolumn_positions[0]]] + [[semicolumn_positions[i], semicolumn_positions[i+1]] 
                                                    for i in range(len(semicolumn_positions) - 1)] + [[semicolumn_positions[-1], len(input_string) - 1]]

            result_txt = ''
            for id in idx:
                [left, right] = id
                result_txt += input_string[left:right] + ";"
            
            return result_txt
        return input_string
    #4. Удаление круглых лишних скобок
    def remove_brackets(self, input_string):
        try:
            input_string.index("(")
            input_string.index(")")
            stack, brackets_position = [], []
            for id, symbol in enumerate(input_string):
                if symbol == '(':
                    stack.append(id)
                if symbol == ')':
                    if input_string[id - 1] == ';':
                        brackets_position.append(stack.pop())
                        brackets_position.append(id)
                    else:
                        stack.pop()
            output = ""
            for id, symb in enumerate(input_string):
                if id not in brackets_position:
                    output += symb
            return output.replace("\n", ";")    
            
        except:
            return input_string.replace("\n", ";").replace(",,", "")
    def remove_long_dashes(self, input_string):
        pattern = re.compile(r'-{4,}')
        return re.sub(pattern, '', input_string).replace(",;", "").replace(",,;","").replace(",,","")  
    #5. Токенизация функций и переменных от синтаксиса и цифр
    def parse_names(self, input_string):
        result = []
        left, right = 0, 0
        while right != len(input_string):
            if left == right:
                if not input_string[right].isalpha():
                    result.append(input_string[left: right + 1])
                    left = left + 1
                    right = right + 1
                else:
                    right = right + 1
            else:
                if input_string[right].isalnum():
                    right = right + 1
                else:
                    result.append(input_string[left : right])
                    left = right
        return result
    
    def get_replace_vars(self, input_parsed_string):  
        vars_list = []
        d = {}
        result = input_parsed_string
        for i in input_parsed_string:
            if i.isalnum() and i[0].isalpha():
                if i not in self.inner_functions:
                    if i not in vars_list:
                        vars_list.append(i)
        for id, var in enumerate(vars_list):
            d[var] = "var" + f"{id}"
        for id, elem in enumerate(input_parsed_string):
            for var, to_replace in d.items():
                if elem  == var:
                    result[id] = to_replace
        return result
    
    def concat_digits(self, array: list) -> list:
        last_value = None
        ls = array.copy()
        for index in range(len(ls)):
            if ls[index].isnumeric():
                if last_value:
                    ls[index] = last_value + ls[index]
                    ls[index - 1] = None
                last_value = ls[index]        
            else:
                last_value = None

        return [item for item in ls if item]
    
    def proccess_part(self, array: list) -> list:
        opened_count = 0
        ls = array.copy()
        
        for index in range(1, len(ls)):
            if ls[index] == '[' and ls[index - 1] == '[':
                opened_count += 1
                ls[index] = '[['
                ls[index - 1] = None
            if opened_count > 0 and ls[index] == ']' and ls[index - 1] == ']':
                opened_count -= 1
                ls[index] = ']]'
                ls[index - 1] = None
        return [item for item in ls if item]
    
    def __process_rules(self, array, index, array_len):
        if not array[index]:
            return array
        for rule in self.rules_params:
            if array[index] == rule[0]:
                if index + rule[-1] <= array_len - 1:
                    if array[index + 1 : index + 1 + rule[-1]] == rule[1]:
                        array[index] = rule[2]
                        for del_index in range(1, 1 + rule[-1]):
                            array[index + del_index] = None
                        return array
        return array

    def process_rules(self, input_array):
        array = input_array.copy()
        array_len = len(array)
        for idx in range(array_len):
            self.__process_rules(array, idx, array_len)
        return [item for item in array if item]
    
    def process_kless(self, input_array: list, k: int) -> list:
        array = input_array.copy()
        sequences = [[itm for itm in item.split(' ') if itm != ''] for item in ' '.join(array).split(';')]
        result = []
        for index in range(len(sequences)):
            seq = sequences[index]
            square_status = 0
            round_status = 0
            if len(seq) <= k:
                for item in seq:
                    if item == '[':
                        square_status += 1
                    if item == ']':
                        square_status -= 1
                    if item == '(':
                        round_status += 1
                    if item == ')':
                        round_status -= 1
                if round_status == 0 and square_status == 0:
                    sequences[index] = []
                    continue
            if index != len(sequences) - 1:
                sequences[index].append(';') 
        return [x for xs in sequences for x in xs]
  

    def preprocessing_composition_naive(self, input_string, tokenize=False):
        result = input_string
        for func in self.functions_naive:
            result = func(result)
        if tokenize:
            return result
        return " ".join(result)
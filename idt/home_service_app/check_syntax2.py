import re

def check_mismatch(text):
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'\'(?:[^\'\\]|\\.)*\'', '""', text)
    text = re.sub(r'\"(?:[^\"\\]|\\.)*\"', '""', text)
    text = re.sub(r'\`(?:[^\`\\]|\\.)*\`', '""', text)

    stack = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char in '{(':
                stack.append((char, i+1))
            elif char in '})':
                if not stack:
                    print(f"Extra closing {char} on line {i+1}")
                    return
                top, line_num = stack.pop()
                if (top == '{' and char != '}') or (top == '(' and char != ')'):
                    print(f"Mismatch: {top} from line {line_num} closed with {char} on line {i+1}")
                    return
    
    if stack:
        for char, line_num in stack:
            print(f"Unclosed {char} from line {line_num}")

text = open('test.js', encoding='utf-8').read()
check_mismatch(text)

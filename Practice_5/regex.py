#1 Write a Python program that matches a string that has an 'a' followed by zero or more 'b''s.
import re
s = input()
if re.fullmatch(r'ab*', s):
    print(s)
else:
    print("ERROR")

#2 Write a Python program that matches a string that has an 'a' followed by two to three 'b'.
import re
s = input()
if re.fullmatch(r'ab{2,3}', s):
    print(s)
else:
    print("ERROR")

#3 Write a Python program to find sequences of lowercase letters joined with a underscore.
import re
s = input()
m = re.findall(r'[a-z]+_[a-z]+', s)
if m:
    print(m)
else:
    print("ERROR")

#4 Write a Python program to find the sequences of one upper case letter followed by lower case letters.
import re
s = input()
m = re.findall(r'[A-Z][a-z]+', s)
if m:
    print(m)
else:
    print("ERROR")

#5 Write a Python program that matches a string that has an 'a' followed by anything, ending in 'b'.
import re
s = input()
if re.fullmatch(r'a.*b', s):
    print(s)
else:
    print("ERROR")

#6 Write a Python program to replace all occurrences of space, comma, or dot with a colon.
import re
s = input()
print(re.sub(r'[ ,.]', ':', s))

#7 Write a python program to convert snake case string to camel case string.
import re
s = input()
print(re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s))

#8 Write a Python program to split a string at uppercase letters.
import re
s = input()
words = re.findall(r'[A-Z][a-z]*', s)
if words:
    print(' '.join(words))
else:
    print("ERROR")

#9 Write a Python program to insert spaces between words starting with capital letters.
import re
s = input()
print(re.sub(r'(?<!^)([A-Z])', r' \1', s)) #before Capital letter not begining of a string

#10 Write a Python program to convert a given camel case string to snake case.
import re
s = input()
print(re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), s).lstrip('_')) #delete the first "_"
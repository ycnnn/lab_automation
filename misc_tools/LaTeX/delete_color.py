import re
import sys

def return_content(filename):
    with open(filename, 'r') as f:
        cs = f.readlines()
    content = ''
    for c in cs:
        content += c
    return content

def find_braket(sample):
    length = len(sample)
    if length == 0:
        print('Warning: empty string.')
        return
    if length == 1:
        if sample == '}':
            res = ''
        else:
            print('Warning: no right braket find.')
            res = sample

    l_indices = []


    for i in range(length):
        if sample[i] == '{':
            l_indices.append(i)
        if sample[i] == '}':
            try:
                l_indices.pop(-1)
            except:
                return sample[:i] + sample[i+1:]
             
    return sample

def delete_color(content):
    contents = re.split('(\\\\textcolor{blue}{)', content)

    if len(contents) %2 != 1:
        print('Warning: incorrect splitting')

    new_contents = '' 

    for i in range(len(contents)):
        if i % 2 == 0:
            new_contents += find_braket(contents[i])
    return new_contents
  

if __name__ == "__main__":
    filename = sys.argv[1]
    content = return_content(filename)
    with open('clean_' + filename, 'w') as f:
            f.write(delete_color(content))

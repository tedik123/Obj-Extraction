# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def read_file(file_path):
    with open(file_path) as f:
        text = f.readlines()
        output = ""
        first = True
        for line in text:
            # print(line)
            edited_text = remove_text_inside_brackets(line)
            # print("edited text", edited_text)
            # replace space with _ (takes into account non " " spaces
            edited_text = "_".join(edited_text.split())
            # print(edited_text)
            edited_text.replace("\n", " ")
            if first:
                output += edited_text
                first = False
            else:
                output += " " + edited_text

        print(output)
        return output

def write_file(output_path, data):
    with open(output_path, mode="w") as w:
        w.writelines(data)
    print("Finished writing")


# https://stackoverflow.com/questions/14596884/remove-text-between-and#:~:text=If%20you%20want%20to%20remove,%5D%22%20%3E%3E%3E%20re.
def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1) ** is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else:  # character is not a [balanced] bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)



output = read_file("text_files/hobbies.txt")

write_file("text_files/hobbies_one_line.txt", output)
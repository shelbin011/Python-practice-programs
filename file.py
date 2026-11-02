try:
    file = open("student.txt", "r")

    content = file.read()
    print(content)

    file.close()

except FileNotFoundError:
    print("File not found!")
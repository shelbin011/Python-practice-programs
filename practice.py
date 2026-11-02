class student:
    def __init__(self,name,mark):
        self.name = name
        self.mark=mark
    def display(self):
        print("name is : ",self.name)
        print("Mark is : ",self.mark)


ibj = student("raju",10)
ibj.display()
#read the exsisting line
with open("server.txt", "r", encoding="utf-8")as file:
	lines = file.readlines()

#write the line back with the replacement
with open("server.txt", "w", encoding="utf-8")as file:
	for i in lines:
		if i.rstrip("\n") == "web-01":
			file.write("web-02\n")
		else:
			file.write(i)
print("updated")

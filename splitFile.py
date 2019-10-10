import os
f = open(r'F:\git_local2\petrarch_chinese\input\1-100000.txt')
fileNameNum = 0;
for i , line in enumerate(f) :
    print(i)
    if i % 1000 == 0 :
        path = "F:\git_local2\petrarch_chinese\\file_" + str(fileNameNum -1 ) + ".txt"
        print(path)
        if os.path.exists(path):
            print("file exist : " + "file_" + str(fileNameNum -1 ) + ".txt")
            wf.close()
        wf = open("file_" + str(fileNameNum) + ".txt", 'a')
        fileNameNum += 1 ;
        wf.write(line)
    else:
        wf.write(line)
f.close()
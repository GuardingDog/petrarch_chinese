import os
f = open(r'F:\git_local2\petrarch_chinese\input\fileFormat.txt')
fileNameNum = 0;
for i , line in enumerate(f) :
    print(i)
    if i % 500 == 0 :
        #path = "F:\git_local2\petrarch_chinese\\input\\inputfiles\\file_" + str(fileNameNum -1 ) + ".txt"
        #print(path)
        # if os.path.exists(path):
        #     print("file exist : " + "file_" + str(fileNameNum -1 ) + ".txt")
        #     wf.close()
        wf = open("F:\git_local2\petrarch_chinese\\input\\inputfiles\\file_" + str(fileNameNum) + ".txt", 'a')
        fileNameNum += 1 ;
        wf.write(line)
    else:
        wf.write(line)
f.close()


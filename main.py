import sys
hex_list=[]
str_list=[] 
try:
    xfile = sys.argv[1]
    x = open(xfile, 'r')
    n =0
    p =0
    c =0
    while True:
        x.seek(n)
        chars = x.read(2).encode('utf-8')
        x.seek(n)
        txt = x.read(2).replace('\n','')
        if not chars:
            break
        hex_list.append(chars.hex())
        str_list.append(txt)
        if len(hex_list) == 8:
            print(format(c,'08x'),' : ',' '.join(hex_list),' ', ''.join(map(str, str_list)))
            hex_list.clear()
            str_list.clear()
            p +=8
            c +=16
        n +=2
    print(format(c,'08x'),' : ',' '.join(hex_list),' ', ''.join(map(str, str_list)))
    x.close()
except IndexError:
  print("usage : program_name [infile] [outfile]")
except FileNotFoundError:
  print(f"No such file : {xfile}")

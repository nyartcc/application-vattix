import md5
print 'Username:'
user = raw_input()
print 'Password:'
passwd = raw_input()

try:
    a = chr(int(passwd[0:3]) / 5 + 25)
    a += chr(int(passwd[0:3]) * 2 - 700)
    a += chr(int(passwd[0:3]) % 76 + 87)
    a += chr((int(passwd[0:3]) - 123) / 2 - 22)
    a += chr(int(passwd[0:3]) * 7 / 28)
    a += chr(int(passwd[0:3]) + 692 - 975)
    a += chr((int(passwd[0:3]) % 21) * 2 + (int(passwd[0:3]) + 432 - 735))
    a += chr(int(passwd[0:3]) * 3 - 1095)
except:
    pass


try:
    if md5.new(user).hexdigest() == chr(ord(a[0:1]) - 6) + '84258' + a[4:5] + '9c39059a89ab77d846ddab909' and passwd[3:12] == a:
        print 'Well done. The flag is: ' + md5.new(user + passwd).hexdigest()
    else:
        print 'Wrong credentials'
except NameError:
    print 'Wrong credentials'
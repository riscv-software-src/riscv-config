import re
import os
import yaml

class warl_interpreter():
    global val
    global bitsum 
    def __init__(self,warl):
        ''' the warl_description in the yaml is given as input to the constructor '''
        #print(warl)
        self.val=warl
        
    def prevsum(self,i,k):
        sump=0
        for j in range(i+1):
              sump=sump+k[j]
        return sump      
    def dependencies(self):
        #print("dependencies accessed successfully")
        dp=[]
        for i in self.val['dependency_fields']:
                dp.append(i)
        return dp
    def islegal(self,value,dependency_vals=[]):
        '''The function takes a range(defined as a 2 tuple list) and an optional(optional incase there are no dependencies) list containing the
        values of the corresponding dependency fields and checks whether the range of 
        values is legal. Returns true if its a legal range and false otherwise.
        '''
        #inp0 = "[0] -> base[29:0] in [0x20000000, 0x20004000]"
        #inp1 = "[1] -> base[29:10] in [0x00000:0xF0000] base[9:6] in [0xB] base[5:0] in [0x00,0x0F,0xF0,0xFF]"
        #inp2 = " base[29:0] in [0x00000000:0xF0000000]"
        flag=0
        hexa="0x"
        xf=[]
        x=[]
        ch=[]
        r1=[]
        r2=[]
        z=[]
        l1=[]
        ch2=[]
        k=[]
        cha=[]
        flag1=0
        v=""
        j=0
        #print("dependency vals is",dependency_vals)
        for i in range(len(self.val['legal'])):
                mode = re.findall('\[(\d)\]\s*->\s*',self.val['legal'][i])
                for i1 in range(len(dependency_vals)):
                        if dependency_vals[i1] == int(mode[i1]):
                                j=i
                                flag1=1
                                break
                        #print(mode)
        if flag1==0:
                print("Dependency vals do not match")
                exit()
        inp1=self.val['legal'][j]
        #print("input is " ,inp1)
        nodename = re.findall(r'(?:\[.+?\] -> )*\s*(.+?)\[.+?\]\s*in\s*\[.+?\]',inp1)
        nodename = list(dict.fromkeys(nodename))
        if( len(nodename) != 1):
                print('Wrong Syntax: Node name is different')
                exit()
        #print(nodename[0])
        splits = re.findall(r'(?:{0}\[(\d.?)+:(\d.?)\])\s*in\s*\[(.+?)\]'.format(nodename[0]),inp1)
        #print(splits)
        for i in range(len(splits)):
                a=int(splits[i][0])
                b=int(splits[i][1])
                ch.append(list(range(b,a+1)))
                z.append(a-b+1)
                if ":" in splits[i][2]:
                        y=re.split("\:",splits[i][2])
                        r1.append(int(y[0],16))         #starting ranges
                        r2.append(int(y[1],16))         #ending ranges
                elif "," in splits[i][2]:
                        y=re.split("\,",splits[i][2])
                        for a in y:
                                l1.append(int(a,16))
                        r1.append(l1)
                        r2.append(l1)
                else:
                        r1.append(int(splits[i][2],16))
                        r2.append(int(splits[i][2],16))
        #print(ch)
        for i in range(len(splits)):
                ch2.append(int(splits[i][0]))
                ch2.append(int(splits[i][1]))
        
        #print(ch2)
        for i in range(len(ch)):
                cha=cha+ch[i]  
        for i in range(min(ch2),max(ch2)+1):
                if i not in cha:
                        print("Bits missing error ")
                        exit()
        for i in range(len(ch)):
                for j in range(i+1,len(ch)):
                        a_set=set(ch[i])    
                        b_set=set(ch[j])      
                        if(a_set & b_set):
                                print("Overlapping error")
                                #break
                                exit()
                        
        #print(r1," ",r2)
        #print(z)
        #print(ch)
        for i in z:
                if(i%4==0):
                        k.append(int(i/4))
                else:
                        k.append(int(i/4)+1)
        #print(k)

        #print(hex(r1[2][0]),hex(r1[2][1]),hex(r1[2][2]),hex(r1[2][3]))
        #invalid input value check
        for i in range(0,len(k)):
                if ":" in splits[i][2]:
                        check=re.split(":",splits[i][2])
                        if len(check[0])-2>k[i] or len(check[1])-2>k[i]:
                                print ("invalid range (given range exceeds)")
                                #break
                                exit()
                elif isinstance(r1[i], list) == True:
                        for p in range(len(r1[i])):
                                if len(hex(r1[i][p]))-2>k[i]:
                                        print("invalid comma seperated (exceeding)")
                                        #break
                                        exit()
                else:
                        if len(splits[i][2])-2>k[i]:
                                print("invalid fixed value (exceeding)")
                                #break
                                exit()


        #value=str(input(" Enter hexadecimal input "))
        sum=0
        for i in range(len(k)):
                sum=sum+k[i]
                
        self.bitsum=sum
        #print(sum)
        if(len(value)>sum):
                print("Invalid entry")
                print("false")
                exit()
        elif len(value)<sum:
                #value[0:sum-len(value)]="0"
                for i in range(sum-len(value)):
                        v=v+"0"
        value=v+value
        #print(v)   
        #print(self.val['legal'][1])
        for i in range(len(k)):
                if i==0:
                        x.append(value[0:k[i]])
                else:
                        x.append(value[self.prevsum(i-1,k):self.prevsum(i,k)])
        #print(x)


        #checking if the given input is legal or illegal
        for i in range(len(r1)):
                if isinstance(r1[i], list) == False: 
                        if(int(x[i],16) in range(r1[i],r2[i]+1)):
                                flag=1
                        else:
                                flag=0
                                break
                else:
                        if int(x[i],16) in r1[i]:
                                flag=1
                        else:
                                flag=0
                                break                
        if flag==1:
                #print("True")
                return True
        else:
                #print("False")
                return False
        
        
        
       # print("islegal accessed successfully")
    def update(self, curr_val,wr_val,dependency_vals=[]):
        ''' The function takes the current value, write value and an optional list(optional incase there are no dependencies) containing the
        values of the corresponding dependency fields and models the updation of 
        the register i.e if the supplied value is legal then the value is returned, else the new value of 
        the register is calculated and returned.
        '''
        flag1=0
        flag2=0
        j=0
        #print(dependency_vals)
        for i in range(len(self.val['wr_illegal'])):
                mode = re.findall('\[(\d)\]\s*.*->\s*',self.val['wr_illegal'][i])
                op=re.findall(r'in\s*\[(.*?)\]',self.val['wr_illegal'][i])
                #print(op)
                if op !=[]:
                        z=re.split("\:",op[0])
                for i1 in range(len(dependency_vals)):
                        #print(dependency_vals[i1]," ",int(mode[i1]))
                        if dependency_vals[i1] ==int(mode[i1]):
                                if op!=[]:
                                        if int(wr_val,16) in range(int(z[0],16),int(z[1],16)):
                                                j=i
                                                flag1=1
                                                break
                                else:
                                        j=i
                                        flag1=1
                                        break
                if flag1==1:
                        break
        if flag1==0 and dependency_vals !=[]:
                print("Dependency vals do not match")
                exit()
        inp=self.val['wr_illegal'][j]
        #print("input is ",inp)
        #print(dependency_vals)
        if(self.islegal(curr_val,dependency_vals) == False):
                print("Current value should be legal")
                return "error"
        if(self.islegal(wr_val,dependency_vals)):
                return wr_val
        else:
                if "->" in inp:
                        op2=re.split(r'\->',inp)
                        wr=op2[1]
                else:
                        wr=inp.strip()
                #print(wr)
                if "0x" in wr:
                        return wr.strip()
                elif wr.lower().strip() == "unchanged":
                        return curr_val
                        
                        
                elif wr.lower().strip() == "nearup":
                        print("nearup")
                        a=[]
                        flag2=0
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                if len(l[i])==1:
                                        a.append(abs(int(wr_val,16)-int(l[i][0],16)))
                        print(min(a))
                        for i in range(len(a)-1,-1,-1):
                                if a[i]==min(a):
                                        j=i
                                        flag2=1
                                        break
                        if flag2==1:
                                return l[j][0]
                                 
                                 
                                 
                                        
                elif wr.lower().strip() == "neardown":
                        print("neardown")
                        a=[]
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                if len(l[i])==1:
                                        a.append(abs(int(wr_val,16)-int(l[i][0],16)))
                        print(min(a))
                        for i in range(len(a)):
                                if a[i]==min(a):
                                        j=i
                                        flag2=1
                                        break
                        if flag2==1:
                                return l[j][0]
                                
                                
                                
                elif wr.lower().strip() == "nextup":
                        print("nextup")
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                #print(l[i][0])
                                if int(l[i][0],16)>int(wr_val,16) and len(l[i])==1:
                                        j=i
                                        flag2=1
                                        break
                        if flag2==1:
                                return l[j][0]
                        else:
                                return max(l)
                                
                                
                elif wr.lower().strip() == "nextdown":
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                #print(l[i][0])
                                if int(l[i][0],16)>int(wr_val,16) and len(l[i])==1:
                                        j=i
                                        flag2=1
                                        break
                        if flag2==1 and j!=0:
                                return l[j-1][0]
                        else:
                                return min(l)
                                
                                
                elif wr.lower().strip() == "max":
                        flag3=0
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                if "," in l[i][0]:
                                        flag3=1
                                        j=i
                                else:
                                        flag3=0
                        if flag3==0:
                                return max(l)
                        else:
                                y=re.split(",",l[j][0])
                                return y[1]
                                              
                elif wr.lower().strip() == "min":
                        flag3=0
                        l=self.legal(dependency_vals)
                        for i in range(len(l)):
                                if "," in l[i][0]:
                                        flag3=1
                                        j=i
                                else:
                                        flag3=0 
                        if flag3==0:
                                return min(l)
                        else:
                                y=re.split(",",l[j][0])
                                return y[0]
                               
                      
                elif wr.lower().strip() == "addr":
                        wr=format(int(wr_val,16),'#0{}b'.format(4*self.bitsum+2))
                        wr=wr[2:]
                        #print(wr)
                        if wr[0:1] =='0':
                                wr_final='1'+wr[1:]
                        elif wr[0:1] =='1':
                                wr_final='0'+wr[1:]
                        else:
                                print("Invalid binary bit")
                        return hex(int(wr_final,2))
 
                else:
                        return "Invalid update mode"               
        #print("update accessed successfully")
    def legal(self,dependency_vals=[]):
        '''The function takes a range(defined as a 2 tuple list) and an optional(optional incase there are no dependencies) list containing the
        values of the corresponding dependency fields and returns the set of legal values as a list of two tuple lists.
        '''
        flag1=0
        j=0
        for i in range(len(self.val['legal'])):
                mode = re.findall('\[(\d)\]\s*->\s*',self.val['legal'][i])
                for i1 in range(len(dependency_vals)):
                        if dependency_vals[i1] == int(mode[i1]):
                                j=i
                                flag1=1
                                break
                if flag1 ==1:
                        break
                        #print(mode)
        if flag1==0 and dependency_vals !=[]:
                print("Dependency vals do not match")
                exit()
        inp=self.val['legal'][j]
        s=re.findall(r'in\s*\[(.*?)\]',inp)
        a=[]
        b=[]
        tup=[]
        for i in range(len(s)):
                tup=[]
                if ":" in s[i]:
                        a.append(s[i].replace(":",",").split())
                elif ',' in s[i]:
                        y=re.split(",",s[i])
                        for j in range(len(y)):
                                tup=[]
                                tup.append(y[j])
                                a.append(y[j].split())

                else:
                        tup=[]
                        tup.append(s[i].split())
                        a.append(s[i].split())
        #print("the range of values are",a)
        return a
        #print(inp)
        #print("legal accessed successfully")
with open(r'rv64i_isa.yaml') as file:        
        mtvec_base = warl_interpreter(yaml.load(file, Loader=yaml.FullLoader)['mtvec']['rv64']['base']['type']['WARL'])
        print(mtvec_base.dependencies(), " (dependency fields)")
        print(mtvec_base.islegal("a00",[1])," (islegal)")
        print(mtvec_base.islegal("a10",[1])," (islegal)")
        print(mtvec_base.legal([0])," (legal)")
        print(mtvec_base.update("20004000","20008000",[0])," (update)")

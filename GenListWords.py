import os

listLemmas = []
listAF = []
listRules = []
listFlected = []
generateDictionary()

def readAffixes():
    #opening dictionary.aff
    file = open(os.getcwd()+'\\dictionary.aff', encoding = 'utf8')
    content = file.read()
    #get the list of lines of the file
    lines = []
    ind = 0
    while (ind<len(content)):
        k=ind
        while (k<len(content) and content[k]!='\n'):
            k+=1
        line = content[ind:k]
        lines.append(line)
        ind = k+1
    #We go through the lines to locate the one beginning with AF
    ind = 0
    while (ind < len(lines) and (len(lines[ind])<2 or lines[ind][0:2]!="AF")):
        ind+=1
    ind+=1
    while (ind < len(lines) and len(lines[ind])>=2 and lines[ind][0:2]=="AF"):
        listAF.append(lines[ind][3:len(lines[ind])])
        ind+=1
    if ind >= len(lines):
        ind=0
    #We then go through the lines to locate the one beginning with PFX or SFX
    while (ind < len(lines)):
        k=ind
        while (k<len(lines) and (len(lines[k])<3 or (lines[k][0:3]!="PFX" and lines[k][0:3]!="SFX"))):
            k+=1
        #We are now at the beginning of a rule.
        if (k<len(lines)):
            l=4
            while (lines[k][l]!=' '):
                l+=1
            #Name of the rule
            flex = [lines[k][4:l]]
            #Is the rule a prefix or suffix rule?
            if (lines[k][0:3]=="PFX"):
                flex.append(0)
            else:
                flex.append(1)
            #Can the rule be combined with a suffix or prefix (the one different from the rule)?
            if (lines[k][l+1]=="Y"):
                flex.append(0)
            else:
                flex.append(1)
            k+=1
            #We then read the following lines with the same name as the rule (flex[0])
            while (k<len(lines) and len(lines[k])>=5 and lines[k][4:l]==flex[0]):
                affix = []
                j = l+1
                i = l+1
                #for each of these lines, we keep the thre interesting parts and forget what comes after.
                for t in range(1,4):
                    j=i
                    while j<len(lines[k]) and lines[k][j]!=" ":
                        j+=1
                    affix.append(lines[k][i:j])
                    i=j+1
                flex.append(affix)
                k+=1
            #We then add our complete rule to the list
            listRules.append(flex)
        ind=k
    file.close()

def validWord(word):
    #if we want to exclude some words. I removed the words beginning with a capital letter for example.
    return(word[0:1].islower())

def readLemmas():
    #Opening the file
    file = open(os.getcwd()+'\\dictionary.dic', encoding = 'utf8')
    content = file.read()
    #Reading the lines and keeping the words
    ind = 0
    while (ind<len(content)):
        k=ind
        while (k<len(content) and content[k]!='\n'):
            k+=1
        line = content[ind:k]
        ind = k+1
        k=0
        #There can be some uninteresting stuff after tab so we don't keep it.
        while (k<len(line) and line[k]!='\t'):
            k+=1
        word = line[0:k]
        if (validWord(word)):
            listLemmas.append(word)
    file.close()

def respectRuleSuffix(word,rule):
    #Check if the end of the word respect the rule 
    k=len(rule)-1
    i=len(word)-1
    respect = True
    while respect and k>=0 and i>=0:
        if (rule[k]!="]" and rule[k]!="."):
            #Condition given by a specific letter
            if (word[i]!=rule[k]):
                respect = False
        elif rule[k]=="]":
            #Set of letter to have or to avoid
            listLetters=[]
            k-=1
            while rule[k]!="[":
                if (rule[k]!="^"):
                    listLetters.append(rule[k])
                k-=1
            #ListLetters contains the letter to have or to avoid
            if rule[k+1]=="^" and word[i] in listLetters:
                respect = False
            elif rule[k+1]!="^" and not word[i] in listLetters:
                respect=False
        i-=1;
        k-=1;
    return respect and (i>=0 or (i==-1 and k==-1))

def respectRulePrefix(word,rule):
    #Check if the beginning of the word respect the rule 
    k=0
    i=0
    respect = True
    while respect and k<len(rule) and i<len(word):
        if (rule[k]!="[" and rule[k]!="."):
            #Condition given by a specific letter
            if (word[i]!=rule[k]):
                respect = False
        elif rule[k]=="[":
            #Set of letter to have or to avoid
            listLetters=[]
            k+=1
            cond = (rule[k]=="^")
            while rule[k]!="]":
                if (rule[k]!="^"):
                    listLetters.append(rule[k])
                k+=1
            #ListLetters contains the letter to have or to avoid
            if cond and word[i] in listLetters:
                respect = False
            elif not cond and not word[i] in listLetters:
                respect=False
        i+=1;
        k+=1;
    return respect and (i<len(word) or (i==len(word) and k==len(rule)))

def applyAffix(word,affix,pfx):
    #Apply the rule given in the list affix on the word.
    if (pfx and respectRulePrefix(word,affix[2])):
        #If we have a rule on a prefix, and if the condition is satisfied,
        #we replace the beginning of the word in affix[0] by affix[1].
        add = affix[1]
        if add[0]=="0":
            add=add[1:len(add)]
        i=0
        #After a /, there can be another set of rules to apply so we isolate them for now.
        while (i<len(add) and add[i]!="/"):
            i+=1
        end = add[i:len(add)]
        add = add[0:i]
        if (affix[0]=="0"):
            return add+word+end
        else:
            return (add+word[len(affix[0]):len(word)]+end)
    elif (not pfx and respectRuleSuffix(word,affix[2])):
        #If we have a rule on a suffix, and if the condition is satisfied,
        #we replace the end of the word in affix[0] by affix[1].
        add = affix[1]
        if add[0]=="0":
            add=add[1:len(add)]
        if (affix[0]=="0"):
            return word+add
        else:
            return (word[0:len(word)-len(affix[0])]+add)

def applyRule(word,rule):
    #Apply the set of rules in the string rule on the word.
    #First the string rule could have comments in it (preceded by #)
    i = 0
    while (i<len(rule) and rule[i]!='#'):
        i+=1
    rule = rule[0:i]
    #We then extract the list of Rules from the string rule.
    rules = []
    #First we check if the rules are represented by integers or strings
    num = False
    try:
        t = int(listRules[0][0])
        num = True
    except ValueError:
        num = False
    if num:
        #If the rules are represented by integers, they are seperated by comas in the string rule
        k=0
        while k<len(rule):
            l = k
            while (rule[l]!=',' and rule[l]!=' '):
                l+=1
            rules.append(rule[k:l])
            k=l+1
    else:
        #If the rules are represented by strings, we check there length
        lg = len(listRules[0][0])
        k=0
        while k<len(rule):
            rules.append(rule[k:k+lg])
            k+=lg
   #Now we apply all the rules in rules.
    result = [word]
    for k in range(0,len(rules)):
        i=0
        while (i<len(listRules) and listRules[i][0]!=rules[k]):
            i+=1
        if (i!=len(listRules)):
            pfx = listRules[i][1]==0
            for u in range(3,len(listRules[i])):
                test = applyAffix(word,listRules[i][u],pfx)
                if test:
                    result.append(test)
    return(result)

def generateDictionary():
    print("Reading lemmas");
    readLemmas();
    print("Reading affixes");
    readAffixes();
    print("Generate flexed forms");
    list1 = []
    for k in range(0,len(listLemmas)):
        i=0
        word = listLemmas[k]
        while (i<len(word) and word[i]!='/'):
            i+=1
        if (i<len(word)):
            if len(listAF)!=0:
                try:
                    num = int(word[i+1:len(word)])
                    rule = listAF[num-1]
                except ValueError:
                    rule = word[i+1:len(word)]
            else:
                rule = word[i+1:len(word)]
            list1+=applyRule(word[0:i],rule)
        else:
            list1.append(word)
    print("Generate second degree flexe forms")
    list2 = []
    for k in range(0,len(list1)):
        i=0
        word = list1[k]
        while (i<len(word) and word[i]!='/'):
            i+=1
        if (i<len(word)):
            if len(listAF)!=0:
                try:
                    num = int(word[i+1:len(word)])
                    rule = listAF[num-1]
                except ValueError:
                    rule = word[i+1:len(word)]
            else:
                rule = word[i+1:len(word)]
            list2+=applyRule(word[0:i],rule)
        else:
            list2.append(word)
    print("Sorting")
    list2.sort()
    print("Deleting repeating words")
    list3 = []
    for k in range(0,len(list2)):
        if (k==0 or list2[k]!=list3[len(list3)-1]):
            list3.append(list2[k])
    print("Save")
    file = open(os.getcwd()+'\\listWords.txt', 'w', encoding = 'utf8')
    for k in range(0,len(list3)):
        file.write(list3[k]+'\n')
    file.close()


import json 


class Wizzard(object): 
    

    def __init__(self,prompts):
        self.prompts = prompts
        self.errors = []
        #{"name",(prompt, type, multi, default)}

    def _single(self,prompt): 
        inpt = input(prompt)
        return inpt if len(inpt) > 0 else None

    def _multi(self,prompt):
        print(prompt)
        lines = []
        while True:
            line = input()
            if len(line) == 0:
                ret = "\n".join(lines)
                return ret if len(ret.replace("\n","")) > 0 else None
            else: 
                lines.append(line)

    def Launch(self):
        for k,v in self.prompts.items(): 
            inpt = self._multi(v[0]) if v[2] else self._single(v[0])
            print("\n")
            if not inpt:  
                self.__setattr__(k,v[3])
            else: 
                try: 
                    if v[1] == dict:
                        self.__setattr__(k,json.loads(inpt))
                    if v[1] == list: 
                        self.__setattr__(k,inpt.split("\n"))
                    if v[1] in (str,int): 
                        self.__setattr__(k,v[1](inpt))
                except Exception as ex: 
                    self.errors.append("Error parsing {0}: {1}".format(k,ex))
                    self.__setattr__(k,v[3])


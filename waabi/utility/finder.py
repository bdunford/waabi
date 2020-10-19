
class Finder(object):


    @staticmethod
    def LineNumbers(content,values):
        values = values if isinstance(values,list) else [values]
        lines = []
        line_map = [(1,0)]
        for line, indx in enumerate([i for i in range(len(content)) if content[i] == "\n"]):
            line_map.append((line + 2,indx))

        for v in values:
            indx=0
            ln=1
            inc=0
            while indx > -1:
                indx = content.find(v,indx+inc)
                if indx > -1:
                    for lm in line_map:    
                        if indx < lm[1]:
                            break
                        else: 
                            ln = lm[0]
                    lines.append(ln)
                inc = 1

        return list(sorted(set(lines)))

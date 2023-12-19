class List(list):
    def __init__(self,_l):
        super().__init__(_l)
        self._i=0
    def prev(self):
        self._i-=1
        return self[self._i%len(self)]
    def nxt(self):
        self._i+=1
        return self[self._i%len(self)]
def similarity(str1, str2,threshhold):
    """Calculates the similarity between two strings.
    Based on the Levenshtein distance.
    Uses a threshhold to regulate the results returned"""
    str1,str2=str1.lower(),str2.lower()
    str2=str2[:len(str1)]
    len_str1 = len(str1) + 1
    len_str2 = len(str2) + 1
    matrix = [[0 for _ in range(len_str2)] for _ in range(len_str1)]
    for i in range(len_str1):
        matrix[i][0] = i
    for j in range(len_str2):
        matrix[0][j] = j
    for i in range(1, len_str1):
        for j in range(1, len_str2):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,         
                matrix[i][j - 1] + 1,          
                matrix[i - 1][j - 1] + cost    
            )
    t=(1-matrix[-1][-1]/max([len_str1,len_str2]))*100
    return t if t>threshhold else None
def close_matches(_str: str,_opts: list[str],threshhold: int=0):
    """Returns a sorted array of strings based on their similarity using a threshhold."""
    if _str=="":
        return []
    o=[(i,similarity(_str,i,threshhold)) for i in _opts]
    o=list(filter(lambda i:i[1]!=None,o))
    o.sort(key=lambda s: s[1],reverse=True)
    return (
        [i[0] for i in o]
    )
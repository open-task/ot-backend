from testModel import *

solutions = Solution().select().where(Solution.solver=="0x1c635f4756ED1dD9Ed615dD0A0Ff10E3015cFa7b")
print(len(solutions))
for x in solutions:
	print(x)

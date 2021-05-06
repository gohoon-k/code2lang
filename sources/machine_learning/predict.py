from sources.code2lang import Code2Lang

import sys
import json


# 예측을 수행한다. 자세한 사항은 code2lang.py를 참고
result = json.dumps(Code2Lang(data=[sys.argv[1]]).exec())

# 예측결과를 node 스크립트로 넘겨주고 실행을 종료
print(result)
sys.stdout.flush()

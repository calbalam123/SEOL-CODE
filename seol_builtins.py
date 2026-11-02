"""설이코드 표준 내장 함수 모음 — 100개.
파일/네트워크/시스템 접근 없이 값과 메모리 데이터만 다루는 함수들입니다.
"""
import math
import random
import statistics
import json
from datetime import datetime, date

def _same_type(value, kind, label):
    if not isinstance(value, kind):
        raise TypeError(f"{label} 값이 올바르지 않습니다.")
    return value

def _flatten(items):
    out = []
    for item in items:
        if isinstance(item, (list, tuple)): out.extend(_flatten(item))
        else: out.append(item)
    return out

def _unique(items):
    result = []
    for x in items:
        if x not in result: result.append(x)
    return result

def _chunk(items, size):
    if size <= 0: raise ValueError("묶음 크기는 1 이상이어야 합니다.")
    return [items[i:i+size] for i in range(0, len(items), size)]

def _clamp(value, low, high):
    if low > high: raise ValueError("최솟값은 최댓값보다 클 수 없습니다.")
    return max(low, min(value, high))

def _mean(items): return statistics.mean(items)
def _median(items): return statistics.median(items)
def _mode(items): return statistics.mode(items)
def _variance(items): return statistics.variance(items)
def _stdev(items): return statistics.stdev(items)
def _percent(value, total): return 0 if total == 0 else value / total * 100
def _lerp(a, b, t): return a + (b-a)*t
def _distance(x1, y1, x2, y2): return math.hypot(x2-x1, y2-y1)
def _factorial(n): return math.factorial(n)
def _gcd(a,b): return math.gcd(a,b)
def _lcm(a,b): return math.lcm(a,b)
def _sign(x): return (x > 0) - (x < 0)
def _is_even(x): return x % 2 == 0
def _is_odd(x): return x % 2 != 0
def _is_prime(n):
    if not isinstance(n, int) or n < 2: return False
    return all(n % i for i in range(2, math.isqrt(n)+1))

def _reverse(x):
    if isinstance(x, (str, list, tuple)): return x[::-1]
    raise TypeError("뒤집기는 문자열 또는 목록에 사용할 수 있습니다.")
def _repeat(text, count): return str(text) * max(0, int(count))
def _contains_text(text, part): return str(part) in str(text)
def _starts(text, prefix): return str(text).startswith(str(prefix))
def _ends(text, suffix): return str(text).endswith(str(suffix))
def _replace(text, old, new): return str(text).replace(str(old), str(new))
def _split(text, sep=None): return str(text).split(sep)
def _join(items, sep=""): return str(sep).join(map(str, items))
def _trim(text): return str(text).strip()
def _left(text, n): return str(text)[:max(0,int(n))]
def _right(text, n): return str(text)[-max(0,int(n)):] if n else ""
def _find(text, part): return str(text).find(str(part))
def _count_text(text, part): return str(text).count(str(part))
def _upper(text): return str(text).upper()
def _lower(text): return str(text).lower()
def _title(text): return str(text).title()
def _pad(text, width, fill=" "): return str(text).ljust(int(width), str(fill)[:1] or " ")
def _zfill(text, width): return str(text).zfill(int(width))
def _is_digit(text): return str(text).isdigit()
def _is_alpha(text): return str(text).isalpha()
def _is_alnum(text): return str(text).isalnum()
def _is_space(text): return str(text).isspace()
def _format_number(value, digits=2): return f"{value:,.{max(0,int(digits))}f}"
def _append(items, value): items.append(value); return items
def _insert(items, index, value): items.insert(int(index), value); return items
def _remove(items, value): items.remove(value); return items
def _pop(items, index=-1): return items.pop(index)
def _clear(items): items.clear(); return items
def _sort(items): return sorted(items)
def _sorted_reverse(items): return sorted(items, reverse=True)
def _unique_count(items): return len(_unique(items))
def _flatten_call(items): return _flatten(items)
def _chunk_call(items, size): return _chunk(items, int(size))
def _first(items): return items[0]
def _last(items): return items[-1]
def _take(items, n): return items[:max(0,int(n))]
def _drop(items, n): return items[max(0,int(n)):]
def _index(items, value): return items.index(value)
def _slice(items, start, end): return items[int(start):int(end)]
def _merge(a,b): return list(a)+list(b)
def _keys(d): return list(d.keys())
def _values(d): return list(d.values())
def _items(d): return [list(x) for x in d.items()]
def _has_key(d,k): return k in d
def _get(d,k,default=None): return d.get(k,default)
def _set(d,k,v): d[k]=v; return d
def _delete(d,k): del d[k]; return d
def _copy(x): return x.copy()
def _to_list(x): return list(x)
def _to_tuple(x): return tuple(x)
def _to_dict(pairs): return dict(pairs)
def _sum_values(d): return sum(d.values())
def _min_key(d): return min(d)
def _max_key(d): return max(d)
def _is_empty(x): return len(x)==0
def _type_name(x): return {str:"문자열",int:"정수",float:"실수",bool:"논리값",list:"목록",tuple:"묶음",dict:"사전",type(None):"없음"}.get(type(x), "값")
def _to_bool(x): return bool(x)
def _is_number(x): return isinstance(x,(int,float)) and not isinstance(x,bool)
def _is_string(x): return isinstance(x,str)
def _is_list(x): return isinstance(x,list)
def _is_dict(x): return isinstance(x,dict)
def _is_integer(x): return isinstance(x,int) and not isinstance(x,bool)
def _is_float(x): return isinstance(x,float)
def _json_text(x): return json.dumps(x, ensure_ascii=False)
def _json_value(x): return json.loads(x)
def _random_int(a,b): return random.randint(int(a),int(b))
def _random_choice(items): return random.choice(items)
def _shuffle(items):
    result=list(items); random.shuffle(result); return result
def _random_float(): return random.random()
def _today(): return date.today().isoformat()
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def _date_format(fmt="%Y-%m-%d"): return datetime.now().strftime(str(fmt))
def _clamp_call(v,lo,hi): return _clamp(v,lo,hi)
def _round_to(v,digits=0): return round(v,int(digits))
def _sqrt(v): return math.sqrt(v)
def _power(a,b): return a**b
def _log(v,base=math.e): return math.log(v,base)
def _sin(v): return math.sin(v)
def _cos(v): return math.cos(v)
def _tan(v): return math.tan(v)
def _degrees(v): return math.degrees(v)
def _radians(v): return math.radians(v)
def _floor(v): return math.floor(v)
def _ceil(v): return math.ceil(v)
def _abs(v): return abs(v)
def _sum(items): return sum(items)
def _min(*values): return min(*values)
def _max(*values): return max(*values)
def _average(items): return _mean(items)
def _median_call(items): return _median(items)
def _percent_call(v,total): return _percent(v,total)
def _distance_call(x1,y1,x2,y2): return _distance(x1,y1,x2,y2)
def _factorial_call(n): return _factorial(int(n))
def _gcd_call(a,b): return _gcd(int(a),int(b))
def _lcm_call(a,b): return _lcm(int(a),int(b))
def _prime_call(n): return _is_prime(int(n))
def _even_call(n): return _is_even(int(n))
def _odd_call(n): return _is_odd(int(n))
def _sign_call(n): return _sign(n)
def _lerp_call(a,b,t): return _lerp(a,b,t)
def _variance_call(items): return _variance(items)
def _stdev_call(items): return _stdev(items)
def _mode_call(items): return _mode(items)

# 정확히 100개의 한국어 표준 함수. 그룹별로 문서화합니다.
BUILTINS = {
    # 숫자·수학 1~20
    "제곱근": _sqrt, "거듭제곱": _power, "로그": _log, "사인": _sin, "코사인": _cos,
    "탄젠트": _tan, "도": _degrees, "라디안": _radians, "내림": _floor, "올림": _ceil,
    "숫자절댓값": _abs, "숫자합계": _sum, "숫자최솟값": _min, "숫자최댓값": _max,
    "평균": _average, "중앙값": _median_call, "백분율": _percent_call, "거리": _distance_call,
    "팩토리얼": _factorial_call, "최대공약수": _gcd_call,
    # 문자열 21~40
    "문자뒤집기": _reverse, "문자반복": _repeat, "문자포함": _contains_text,
    "시작문자": _starts, "끝문자": _ends, "문자바꾸기": _replace, "문자나누기": _split,
    "문자합치기": _join, "공백제거": _trim, "왼쪽자르기": _left, "오른쪽자르기": _right,
    "문자찾기": _find, "문자개수": _count_text, "대문자": _upper, "소문자": _lower,
    "단어첫글자대문자": _title, "오른쪽채우기": _pad, "숫자앞자리채우기": _zfill,
    "숫자인지": _is_digit, "문자인지": _is_alpha,
    # 목록 41~60
    "목록추가": _append, "목록삽입": _insert, "목록삭제": _remove, "목록꺼내기": _pop,
    "목록비우기": _clear, "목록정렬": _sort, "목록내림차순": _sorted_reverse,
    "중복없는개수": _unique_count, "목록평탄화": _flatten_call, "목록묶기": _chunk_call,
    "첫항목": _first, "마지막항목": _last, "앞에서가져오기": _take, "앞에서버리기": _drop,
    "항목위치": _index, "목록자르기": _slice, "목록합치기": _merge, "중복제거": _unique,
    "항목포함": lambda items, value: value in items, "목록뒤집기": _reverse,
    # 사전·자료 61~75
    "사전키": _keys, "사전값": _values, "사전항목": _items, "키있는지": _has_key,
    "사전가져오기": _get, "사전저장": _set, "사전삭제": _delete, "복사": _copy,
    "목록으로": _to_list, "묶음으로": _to_tuple, "사전으로": _to_dict,
    "사전값합계": _sum_values, "첫번째키": _min_key, "마지막키": _max_key, "비어있는지": _is_empty,
    # 변환·검사 76~85
    "자료형": _type_name, "논리값으로": _to_bool, "숫자인지검사": _is_number,
    "문자열인지": _is_string, "목록인지": _is_list, "사전인지": _is_dict,
    "정수인지": _is_integer, "실수인지": _is_float, "JSON문자열": _json_text, "JSON읽기": _json_value,
    # 무작위·날짜·통계 86~100
    "무작위": _random_int, "무작위선택": _random_choice, "무작위섞기": _shuffle,
    "무작위실수": _random_float, "오늘날짜": _today, "현재시간": _now,
    "날짜형식": _date_format, "범위제한": _clamp_call, "자릿수반올림": _round_to,
    "최소공배수": lambda a,b: _lcm_call(a,b), "소수인지": _prime_call,
    "짝수인지": _even_call, "홀수인지": _odd_call, "부호": _sign_call, "보간": _lerp_call,
}

if len(BUILTINS) != 100:
    raise RuntimeError(f"내장 함수 수가 100개가 아닙니다: {len(BUILTINS)}")

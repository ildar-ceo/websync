# -*- coding: utf-8 -*- 
# Author : Bikmamatov Ildar
# Description : Библиотека для работы с массивами и словарями

from urllib.parse import *
import types, copy, json, inspect, re, time, datetime, random, string, os, sys
import collections

# https://docs.python.org/2/library/types.html
TypeInt = [int]
TypeLong = [int]
TypeReal = [float]
TypeBool = [bool]
TypeBoolean = [bool]
TypeString = [str]
TypeArray = [tuple, list]
TypeObject = [dict]
TypeDict = [dict]
TypeArrayOrObject = [dict, tuple, list]
TypeClass = [type]
TypeDatetime = [datetime.datetime]
TypeDate = [datetime.date]
TypeTime = [datetime.time]
TypeObjectID = []

TypeNames = {
	"TypeInt" : TypeInt,
	"TypeLong" : TypeLong,
	"TypeReal" : TypeReal,
	"TypeBool" : TypeBool,
	"TypeBoolean" : TypeBoolean,
	"TypeString" : TypeString,
	"TypeArray" : TypeArray,
	"TypeObject" : TypeObject,
	"TypeDict" : TypeObject,
	"TypeArrayOrObject" : TypeArrayOrObject,
	"TypeClass" : TypeClass,
	"TypeDatetime" : TypeDatetime,
	"TypeDate" : TypeDate,
	"TypeTime" : TypeTime,
	"TypeObjectID" : TypeObjectID,
}

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class FieldType(object):
	UNKNOWN = 0
	STRING = 1
	NUMBER = 2
	REAL = 3
	BOOLEAN = 4
	DATE = 5
	TIME = 6
	DATETIME = 7
	TAGS = 9
	LIST_TAGS = 10
	TEXT = 11
	EMAIL = 12
	PHONE = 13
	
	DICT = 14
	
	TYPES = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,"0","1","2","3","4","5","6","7","8","9","10","11","12","13"]

class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
	
def getTypeByName(name):
	return xarr(TypeNames, name, None)

def getTypeByDjangoModelName(name):
	return xarr(DjangoModelsNames, name, None)
	
def clone(var):
	if (type(var) in TypeArrayOrObject):
		return copy.deepcopy(var)
	return var

def isFloat(value):
	try:
		float(value)
		return True
	except:
		return False

def isfloat(value):
	return isFloat(value)
		
def isLong(value):
	try:
		int(value)
		return True
	except:
		return False

def isAnsii(word):
	res = True
	for v in word:
		if ord(v) > 127:
			res = False
			break
	return res		
	
def convertType(value, t, default=None):
	try:
		if not (type(t) in TypeArray):
			return default
			
		tv = type(value)
		if tv in t:
			return value
		
		# любое число является строкой. Все будем конвертировать сразу в юникод
		if t == TypeString:
			if (tv in TypeInt + TypeReal + TypeBool + TypeObjectID):
				return str(value)
			if (tv in TypeDatetime + TypeDate + TypeTime):
				if tv in TypeDate:
					return value.strftime(DATE_FORMAT)
				elif tv in TypeTime:
					return value.strftime(TIME_FORMAT)
				elif tv in TypeDatetime:
					return value.strftime(DATETIME_FORMAT)
				return None
			
		elif ((t == TypeInt) or (t == TypeReal)):
		
			# любое число целочисленное число является действительным
			if (t == TypeReal) and (tv in TypeInt + TypeBool):
				return float(value)
			elif (t == TypeReal) and (tv in TypeString) and (value.isdigit() or isfloat(value)):
				return float(value)
			
			# любое число булевское значение, является целочисленным
			elif (t == TypeInt) and (tv in TypeBool):
				return int(value)
			elif (t == TypeInt) and (tv in TypeString) and (value.isdigit()):
				return int(value)		
		
			elif tv in TypeDatetime:
				return value.timestamp()
			elif tv in TypeDate:
				return int(time.mktime(value.timetuple()))
			elif tv in TypeTime:
				return int((value.hour * 60 + value.minute)*60 + value.second)
			
		elif t == TypeBool:
			# Обработка типа bool
			if (t == TypeBool) and (tv in TypeInt + TypeReal):
				if value == 0:
					return False
				else:
					return True
			if (t == TypeBool) and (tv in TypeString):
				if value == "False":
					return False
				elif value == "True":
					return True
				elif value == "false":
					return False
				elif value == "true":
					return True
				elif value == "0":
					return False
				elif value == "":
					return False	
				elif value == False:
					return False			
				else:
					return True
		
		elif t == TypeTime:
			# ------------ Работа со временем и датой ------------
			if (t == TypeTime) and (tv in TypeString):
				res = None
				t = None
				try: t = datetime.datetime.strptime(value, '%H:%M:%S')
				except: res = None	
				if t == None:
					try: t = datetime.datetime.strptime(value, '%H:%M')
					except: t = None
				if t == None:
					try: t = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
					except: t = None
				if t == None:
					try: t = datetime.datetime.strptime(value, '%d-%m-%Y %H:%M:%S')
					except: t = None			
				if t != None: res = datetime.time(t.hour, t.minute, t.second, t.microsecond)
				return res
			if (t == TypeTime) and (tv in TypeInt + TypeReal):
				t = datetime.datetime.fromtimestamp(value)	
				res = datetime.time(t.hour, t.minute, t.second, t.microsecond)
				return res
			if (t == TypeTime) and (tv in TypeDatetime):
				res = datetime.time(value.hour, value.minute, value.second, value.microsecond)
				return res	
		
		elif t == TypeDate:
			if (t == TypeDate) and (tv in TypeString):
				res = None
				t = None
				try: t = datetime.datetime.strptime(value, '%Y-%m-%d')
				except: t = None		
				if t == None:
					try: t = datetime.datetime.strptime(value, '%d-%m-%Y')
					except: t = None
				if t == None:
					try: t = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
					except: t = None
				if t == None:
					try: t = datetime.datetime.strptime(value, '%d-%m-%Y %H:%M:%S')
					except: t = None			
				if t != None: res = datetime.date(t.year, t.month, t.day)
				return res		
			if (t == TypeDate) and (tv in TypeInt + TypeReal):
				t = datetime.datetime.fromtimestamp(value)	
				res = datetime.date(t.year, t.month, t.day)
				return res
			if (t == TypeDate) and (tv in TypeDatetime):
				res = datetime.date(value.year, value.month, value.day)
				return res
		
		elif t == TypeDatetime:
			if (t == TypeDatetime) and (tv in TypeString):
				res = None
				try: res = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
				except: res = None
				if res == None:
					try: res = datetime.datetime.strptime(value, '%d-%m-%Y %H:%M:%S')
					except: res = None
				if res == None:
					try: res = datetime.datetime.strptime(value, '%Y-%m-%d')
					except: res = None			
				if res == None:
					try: res = datetime.datetime.strptime(value, '%d-%m-%Y')
					except: res = None
				if res == None:
					try: res = datetime.datetime.strptime(value, '%H:%M:%S')
					except: res = None
				if res == None:
					try: res = datetime.datetime.strptime(value, '%H:%M')
					except: res = None
				if (res == None) and (value.isdigit() or isfloat(value)):
					res = datetime.datetime.fromtimestamp(float(value))
				return res
			
			if (t == TypeDatetime) and (tv in TypeInt + TypeReal):
				return datetime.datetime.fromtimestamp(value)
			if (t == TypeDatetime) and (tv in TypeTime):
				res = datetime.datetime(1970,1,1,value.hour, value.minute, value.second, value.microsecond)
				return res	
			if (t == TypeDatetime) and (tv in TypeDate):
				res = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
				return res			

		elif t == TypeObjectID:	
			if isinstance(value, bson.objectid.ObjectId):
				return value
			else:
				try:
					return bson.objectid.ObjectId(str(value))
				except Exception as e:
					#print ('Convertype ObjectId error: value=' + str(value) + ', error=' + str(e))
					return default
				
	except Exception as e:
		print ('Convertype error: value=' + str(value) + ', error=' + str(e))
		pass
	
	return default

def getType(value):
	return type(value)
	
def isType(value, t):
	if type(value) in t:
		return True
	return False
	
def checkType(value, t, default=None):
	res = convertType(value, t)
	if res == None:
		if default != None:
			res = convertType(default, t)
	return res
	
def getArray(values):
	tp = type(values)
	
	if tp in TypeArray:
		return values
		
	elif tp in TypeObject:
		res=[]
		i=0
		sz = len(values)
		while i<sz:
			val = values.get(i)
			if val == None:
				val = values.get(str(i))
			if val != None:
				res.append(val)
			i=i+1
		return res
		
	return None
	
def xarr(arr, key, val=None, t=None):
	val = clone(val)
	res = val
	try:
		if type(arr) in TypeArray:
			key = convertType(key, TypeInt)
			if key == None:
				return None		
			res = clone(arr[key])
		elif type(arr) in TypeObject:
			key = convertType(key, TypeString)
			if key == None:
				return None				
			res = clone(arr[key])			
		else:
			res = getattr(arr, key)
			pass
	except:
		res = val
	if (t != None) and (type(t) in TypeArray):
		res = convertType(res, t)
		if res == None:
			res = convertType(val, t)
	del val		
	return res

def xarrj(arr, key, default=None, t=None):
	"""
		Данная функция получает значение по ключу
		Суффик j означает, что используется обращение к подмассивам через точки
		Пример:
			val = xarrj(res, 'name.ru', '') что означает val = res['name']['ru']
	"""
	arr = clone(arr)
	default = clone(default)
	res = default
	keys = (key).split(".")
	try:
		for i in keys:
			arr = xarr(arr, i)
		if arr == None:
			res = default
		else:
			res = arr
		if t != None:
			res = convertType(res, t, default)
	except:
		res = default
	del arr
	del default
	return res
	
def has_key(arr, key):
	res = False
	try:
		if type(arr) in TypeArray + TypeObject:
			val = arr[key]
			res = True
	except:
		res = False
	return res
	
def getDict(arr, fields):
	new_arr = {}
	for field in iter(fields):
		new_arr[field] = xarr(arr,field,None)
		pass
	return new_arr

def getIndex(data):
	index={}
	i=0
	for obj in data:
		id = xarr(obj,'id', None, TypeString)
		if id != None:
			index[id]=i
		i=i+1
	return index

def getCursor(cursor):
	res=[]
	for obj in cursor:
		res.append(obj)
	return res
	
def getCursorIndex(data):
	res=[]
	index={}
	i=0
	for obj in data:
		res.append(obj)
		id = xarr(obj,'_id', None, TypeString)
		if (id == None): id = xarr(obj,'id', None, TypeString)
		index[id]=i
		i=i+1
	return (res,index)
	
def xindex(arr, index, id):
	id = str(id)
	res = None
	i = xarr(index, id)
	if i != None: res = xarr(arr, i)	
	return res
	
def toString(s):
	return checkType(str(s), TypeString, "")
	
def xfirst(res):
	first = None
	cursor = xarr(res, 'cursor')
	try:
		if cursor != None: first = cursor.get(0)
	except Exception as e:
		pass
	return first	
	
def xaddj(res, key, val):
	"""
		Данная функция добавляет значение по ключу в массив res
		Суффик j означает, что используется обращение к подмассивам через точки
		Пример
			xaddj(res, 'name.ru', 'Название') означает res['name']['ru'] = 'Название'
	"""
	key = checkType(key, TypeString, "")
	
	# разобъем весь key на точки, а затем пробежимся по всему массиву
	keys = (key).split(".")
	go=res
	sz=len(keys)
	i=0
	
	for v in iter(keys):
		if i+1 == sz: # Если последний элемент
		
			# проверка, если ключ v оканчивается на []
			pattern = r'\[\]$'
			if re.search(pattern, v):
				v = v[:-2]
				if not go.get(v):
					go[v]={}
				go[v][len(go[v])]=val
			
			else:
				# в противном случае просто добавляем его и все
				if not go.get(v):
					go[v]={}
				go[v]=val
		else:
			if not go.get(v):
				go[v]={}
			go=go[v]
		i=i+1
	
	return res
	
def xadd(res, key, val):
	"""
		Данная функция добавляет значение по ключу в массив res
		означает res[key] = val
	"""
	if (key==None):
		if (isType(res, TypeArray)):
			res.append(val)
	else:
		key = checkType(key, TypeString+TypeInt, 0)
		res[key] = val
	return res	

def mergeDicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
	
def mergeOrderedDict(*args):
	f_data = collections.OrderedDict()
	for o in args:
		for key in o.keys():
			f_data[key] = o[key]
	return f_data
	
def parseFilterField(key,value):
	"""
		Парсит key И value фильтра
	"""
	f = False
	op = None
	field = None		
	ch1 = None
	ch2 = None
	if len(key) >= 1: ch1 = key[0:1]; 
	if len(key) >= 2: ch2 = key[0:2];
	
	if (len(key) >= 3) and (key[0:3] == '$or'):
		op='$or'
		f = True
	elif (len(key) >= 4) and (key[0:4] == '$and'):
		op='$and'
		f = True
	elif (len(key) >= 3) and (key[0:3] == '$in'):
		op='$in'
		f = True
		field=key[3:]
	elif (len(key) >= 4) and (key[0:4] == '$nin'):
		op='$nin'
		f = True	
		field=key[4:]
	# Обычные операции =, >, <, !=
	elif ch1 == "=":
		f=True
		op="="
		field=key[1:]
	elif ch2 == ">=":
		f=True
		op=">="
		field=key[2:]
	elif ch2 == "<=":
		f=True
		op="<="
		field=key[2:]
	elif ch1 == ">":
		f=True
		op=">"
		field=key[1:]
	elif ch1 == "<":
		f=True
		op="<"
		field=key[1:]	
	elif ch2 == "!=": # Не равно
		f=True
		op='!='
		field=key[2:]
	# Работа со строками
	elif ch1 == "%": # Регистро-независимая проверка на вхождение.
		f=True
		op='%'
		field=key[1:]
	elif ch2 == "!%": # Регистро-независимая проверка на вхождение.
		f=True
		op='!%'
		field=key[2:]		
	elif (len(key) >= 7) and (key[0:7] == '$isnull'):
		op='isnull'
		f = True
		field=key[7:]
	elif (len(key) >= 10) and (key[0:10] == '$isnotnull'):
		op='isnotnull'
		f = True	
		field=key[10:]		
	else:
		f=True
		op='='
		field=key
	
	if (isType(value, TypeArray + TypeObject) and op != '$and' and op != '$or'):
		f=True
		if op=='!=': op = "$nin"
		else: op='$in'
		
	if (value == None and op in ['=', '!=']):
		f=True
		if op == '=': op='isnull'
		elif op == '!=': op='notnull'
		
	#var_dump(key)
	#var_dump(key[0:3] + " == '$in' = " + str(key[0:3] == '$in'))
	#var_dump(op)
		
	return {
		"f" : f,
		"op" : op,
		"field" : field,
		"key" : key,
		"value" : value,
	}
	
def convertOpToMongo(op, neg, value):
	res=""
	
	isString = type(value) in TypeString
	isArray = type(value) in TypeArray+TypeObject
	
	if isArray:
		if neg:
			res="nin"
		else:
			res="in"
	
	elif isString:
		if op == "=":
			if neg:
				res = "not__iexact"
			else:
				res = "iexact"
		elif op == "!=":
			if neg:
				res = "iexact"
			else:
				res = "not__iexact"
		
		elif op == "%":
			if neg:
				res = "not_icontains"
			else:
				res = "icontains"

		elif op == "!%":
			if neg:
				res = "icontains"
			else:
				res = "not_icontains"				
		
	else:
		if op == "=":
			if neg:
				res = "ne"
		elif op == "!=":
			if not neg:
				res = "ne"

		elif op == ">":
			if neg:
				res = "lte"
			else:
				res = "gt"
				
		elif op == ">=":
			if neg:
				res = "lt"
			else:
				res = "gte"		

		elif op == "<":
			if neg:
				res = "gte"
			else:
				res = "lt"	
		elif op == "<=":
			if neg:
				res = "gt"
			else:
				res = "lte"					
				
	if op == 'isnull':
		if neg:
			res = 'exists'
		else:
			res = 'notexists'
	
	elif op == 'isnotnull':
		if neg:
			res = 'notexists'
		else:
			res = 'exists'		
		
	return res
	
def getFieldsInFilter(filter):
	"""
		Получат список всех полей, которые есть в фильтре, вне зависимости от вложенности $or И $and
	"""
	fields = {}
	for key in filter:
		value = filter[key]
		isObject = isType(value, TypeObject)
		isArray = isType(value, TypeArray)				
		res = parseFilterField(key, value)
		#print (res)
		op = res['op']
		field = res['field']
		f = res['f']
		if (isObject or isArray) and (op == '$or' or op == '$and'):
			for i in iter(value):	
				val = i
				if isObject: val = value[i]	
				f = getFieldsInFilter(val)
				fields = dict(fields, **f)
		else:
			if (f == True) and (field != None):
				fields[field] = 1
	return fields

def buildNewFilter(filter, xFilter, defaultFilter):
	"""
		Строит новый фильтр на основе filter, xFilter, defaultFilter
	"""
	new_filter = dict(filter, **xFilter)
	if not isType(filter, TypeObject):
		return None	
	fields = getFieldsInFilter (filter)
	#print (fields)
	for key in defaultFilter:
		value = defaultFilter[key]
		res = parseFilterField(key, value)
		op = res['op']
		field = res['field']
		f = res['f']
		isExists = xarr(fields, field, False)
		#print (res)
		#print (isExists)
		if (not isExists) and (f == True):
			new_filter[key] = value
	return new_filter
	
def format_str_normalize_array(res, arr, key):
	for k in arr:
		val = arr[k]
		if type(val) in TypeObject:
			if (key == ''): res = format_str_normalize_array(res, val, k)
			else: res = format_str_normalize_array(res, val, key +'.'+ k)
			res[k]=val
		else:
			if (key == ''): res[k] = val
			else: res[key +'.'+ k] = val
	return res
	
def format_str(s, arr):
	s = checkType(s, TypeString, "")
	arr = checkType(arr, TypeObject, {})
	arr=format_str_normalize_array({}, arr, '')
	for key in arr:
		if isType(key, TypeString + TypeInt):
			val = arr[key]
			val = convertType(val, TypeString, str(val))
			s = s.replace("%"+key+"%", val)
		pass
	return s

class MyJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isType(obj, TypeDate):
			return int(time.mktime(obj.timetuple()))
		elif isType(obj, TypeTime):
			return int((obj.hour * 60 + obj.minute)*60 + obj.second)	
		elif isType(obj, TypeDatetime):
			return obj.timestamp()		
		try:
			res=json.JSONEncoder.default(self, obj)
		except:
			res = str(obj)
		return res

def json_encode(arr):
	return json.dumps(arr, sort_keys=True, separators=(',', ': '), cls = MyJsonEncoder)
	
def var_dump_output(var, level, space, crl, outSpaceFirst=True, outLastCrl=True):
	res = ''
	if outSpaceFirst: res = res + space * level
	
	typ = type(var)
	
	if typ in [list]:
		res = res + "[" + crl
		for i in var:
			res = res + var_dump_output(i, level + 1, space, crl, True, False) + ',' + crl
		res = res + space * level + "]" 
		
	elif typ in [dict]:
		res = res + "{" + crl 
		for i in var:
			res = res + space * (level+1) + i + ": " + var_dump_output(var[i], level + 1, space, crl, False, False)  + ',' + crl
		res = res + space * level  + "}"
	
	elif typ in [str]:
		res = res + "'"+str(var)+"'"
	
	elif typ in [NoneType]:
		res = res + "None"
	
	elif typ in (int, float, bool):
		res = res + typ.__name__ + "("+str(var)+")"
		
	elif isinstance(typ, object):
		res = res + typ.__name__ + "("+str(var)+")"
		
	if outLastCrl == True:
		res = res + crl
		
	return res
	
def var_dump(*obs):
	"""
	  shows structured information of a object, list, tuple etc
	"""
	i = 0
	for x in obs:
		
		str = var_dump_output(x, 0, '  ', '\n', True)
		print (str.strip())
		
		#dump(x, 0, i, '', object)
		i += 1
	
def urlGetAdd(*args, **kwargs):
	url = xarr(args, 0, "", TypeString)
	o = urlparse(url)
	
	#var_dump (args)
	
	scheme = checkType(o.scheme, TypeString, None)
	netloc = checkType(o.netloc, TypeString, None)
	path = checkType(o.path, TypeString, None)
	query = checkType(o.query, TypeString, '')
	force = xarr(kwargs, 'force', False)

	new_url = ''
	if (scheme != None) and (scheme != ''):
		new_url = scheme
	if (netloc != None) and (netloc != ''):
		new_url = new_url + "://" + netloc

	new_url = new_url + path
	query_arr = parse_qs(query)
	
	i=1
	while i < len(args)-1:
		key = xarr(args,i,None,TypeString)
		value = xarr(args,i+1,None,TypeString)
		i=i+2
		
		if (key != None) and (value != None):
			if key in query_arr:
				query_arr[key] = query_arr[key] + [value]
			else:
				query_arr[key] = [value]
		
		pass
	
	if len(query_arr) > 0:
		new_url += '?'
		flag=False
		for key in query_arr:
			val = query_arr[key]
			if len(val) > 0:
				if force:
					new_url = new_url + str(key) + '=' + str(val[-1]) + '&'
					flag=True
				else:
					new_url = new_url + str(key) + '=' + str(val[0]) + '&'
					flag=True
		if flag:
			new_url = new_url[:-1]
	
	return new_url
	
	
def requestToObject(obj):
	"""
		Функция осуществляет конвертацию POST И GET запросов в нормальный вложенный объект.
		Пример:
		{
			'data[backUrl]' : '123',
			'data[version]' : '1.0',
			'data[arr][1]' : '233',
			'data[arr][2]' : '5',
			'data[arr][100]' : '233',
		}		
		Приведет к :
		{
			'data':{
				'backUrl' : '123',
				'version' : '1.0',
				'arr' : {
					1 : '233',
					2 : '5',
					100 : '233',
				}
			}
		}
	"""

	#print (json_encode(obj))
	obj = checkType(obj, TypeObject, {})
	
	new_obj = {}

	# Проходим по всем элементам входного массива
	for key in obj:
		
		# Получаем массив названий из строки data[arr][1]
		arr = re.split('[\[\]]',key)
		#print arr
		val = obj[key]
		go = new_obj
		
		# Удаляем в массиве arr пустые значения
		for name in iter(arr):
			if len(name) == 0:
				arr.remove(name)
		
		i=0
		sz = len(arr)
		
		# Записываем значение val в массив new_obj
		for name in iter(arr):
			if name == "":
				name = str(len(go))	
			# Если последний элемент
			if i == sz-1:
				if (type(go) in TypeObject):
					# Здесь str ставить нельзя !!!! Ломается callback в rest view.py
					# query_arr = removeArrayInValues(requestToObject(parse_qs(query))) 
					# Массив не доходит и превращается в строку (
					go[name]=val
				else:
					break
			else:
				if not go.get(name):
					go[name]={}
				go = go[name]
				
			i = i + 1
		pass
	
	#print (json_encode(new_obj))
	
	return new_obj
	
def removeArrayInValues(*args, **kwargs):
	"""
		Удаляет послежний элемент в объекте, если он является массивом, и берет либо первое, либо последнее значение
	"""
	#print (args)
	obj = xarr(args, 0)
	get = xarr(kwargs, 'get', 1, TypeInt)
	
	if isType(obj, TypeObject):
		for key in obj:
			obj[key] = removeArrayInValues(xarr(obj, key), **kwargs)
		return obj
		
	elif isType(obj, TypeArray):
		
		if len(obj)>0:
			if get == 1:
				return obj[0]
			else:
				return obj[-1]
		else:
			return None

	else:
		return obj
		
def genRandomString(size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
"""
def genID():
	id = round(time.time()*1000000)*1000+random.randint(100,999)
	return "%x" % id
"""
def dirname(path):
	return os.path.dirname(path)
	
def basename(path):
	return os.path.basename(path)
	
def getFileExtension(path):
	return (os.path.splitext(path)[-1])[1:]
	
def pathExists(path):
	return os.path.exists(path)
	
def isDir(path):
	return os.path.isdir(path)	

def mkdir(path, isFile=False):
	if isFile == True:
		path = dirname(path)
	if not pathExists(path):
		os.makedirs(path)

def deleteLastSlash(path):
	if len(path) > 0:
		if path[len(path) - 1] == '/':
			return path[:-1]
	return path

def deleteFirstSlash(path):
	if len(path) > 0:
		if path[0] == '/':
			return path[1:]
	return path
	
def joinPath(*args):
	str = ''
	for path in args:
		path = deleteLastSlash(deleteFirstSlash(path))
		str = str + '/' + path
	return str
			
def shellescape(s):
    return "'" + s.replace("'", "'\\''") + "'"
	
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
# Usage example
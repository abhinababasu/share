#!/usr/bin/env python3 

# on windows need python.exe -m pip install requests
# on linux pip install requests 
import json 
import sys 
import requests
import traceback
import json

ip = '169.254.169.254'
port = '80'
default_version = 'latest_internal'
default_headers = {'Metadata' : 'True'}

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return True

def createUrl(resPath):
    return 'http://{0}:{1}/{2}'.format(ip, port, resPath)

def restCall(resPath, format='json', version=default_version, imds_headers = default_headers, verbose=True):
    mdUrl = 'http://{0}:{1}/{2}?api-version={3}&format={4}'.format(ip, port, resPath, version, format)
    if verbose:
        print('Calling {}'.format(mdUrl))
    val = 0
    while val < 5:
        resp = requests.get(url=mdUrl, headers=imds_headers)
        code = resp.status_code
        cont = bytes.decode(resp.content)
        if code == 429:
            print('Too many request encountered, sleeping')
            time.sleep(5)
            val += 1
            continue
        if verbose:
            print(code)
            print(cont)
        break

    return code, cont

def restCallRaw(subUrl, imds_headers = {'Metadata': 'True'}):
    mdUrl = 'http://{0}:{1}/{2}'.format(ip, port, subUrl)
    print('Calling {}'.format(mdUrl))
    resp = requests.get(url=mdUrl, headers=imds_headers)
    code = resp.status_code
    cont = bytes.decode(resp.content)
    print(code)
    print(cont)
    return code, cont

def baseTest():
    subUrl = 'metadata/instance'
    code,content = restCall(subUrl, 'json', '2017-03-01')
    if(code == 200 and len(content) > 0):
        return True

def defaultFormat():
    # Verify that default format is correct
    url1 = 'metadata/instance?api-version={}'.format(default_version)
    url2 = 'metadata/instance?api-version={}&format=json'.format(default_version)
    code1,content1 = restCallRaw(url1)
    code2,content2 = restCallRaw(url2)
    if(code1 != 200 or code1 != code2):
        print('Status code 200 expected')
        return False

    if (content1 != content2):
        print('default format does not match json')
        return False

    if not is_json(content1):
        print("Default was not JSON")
        return False

    # Verify that default format of errors is correct
    url1 = 'metadata/instance/blah?api-version={}'.format(default_version)
    url2 = 'metadata/instance/blah?api-version={}&format=json'.format(default_version)

    code1,content1 = restCallRaw(url1)
    code2,content2 = restCallRaw(url2)
    if(code1 != 404 or code1 != code2):
        print('Status code 404 expected')
        return False

    if (content1 != content2):
        print('default format does not match json')
        return False

    if not is_json(content1):
        print("Default was not JSON")
        return False

    return True

def urlPrefix():
    url = 'metadata'
    code,cont = restCall(url, 'text')
    if not cont == 'instance/':
        print('root metadata call returned invalid value')
        return False

    return True;    

def versionTests():
    # bad version should FAIL
    code, cont = restCall('metadata', 'text', 'blahversion')
    if(code != 404 or 'Invalid version' not in cont):
        print('Invalid version was not failed')
        return False

    # No version should fail
    code, cont = restCallRaw('metadata/instance')
    if(code != 400 or 'version was not specified' not in cont):
        print('Invalid version was not failed')
        return False

    return True

def queryVar():
    url = 'metadata/instance?api-version={}&cid=42'.format(default_version)
    code, cont = restCallRaw(url)
    if (code != 400):
        print('Duplicate cid not failed')
        return False
 
    url = 'metadata/instance?api-version={}&foo=bar'.format(default_version)
    code, cont = restCallRaw(url)
    if (code != 400):
        print('Unknown query variable not failed')
        return False
 
    url = 'metadata/instance?api-version={}&format=csv'.format(default_version)
    code, cont = restCallRaw(url)
    if (code != 400 or 'Unsupported format string' not in cont):
        print('Unknown format string not failed')
        return False
        
    return True

def onlyGet():
    mdUrl = createUrl('metadata?api-version={}&format=text'.format(default_version))
    resp = requests.post(url=mdUrl, headers=default_headers)
    if(resp.status_code != 400):
        print('POST was not faild')
        return False
  
    resp = requests.post(url=mdUrl, headers=default_headers)
    if(resp.status_code != 400):
        print('POST was not failed and got ', resp.status_code)
        return False
    print('POST check passed')
    
    resp = requests.put(url=mdUrl, headers=default_headers)
    if(resp.status_code != 400):
        print('PUT was not failed and got ', resp.status_code)
        return False
    print('PUT check passed')
    
    resp = requests.delete(url=mdUrl, headers=default_headers)
    if(resp.status_code != 400):
        print('DELETE was not failed and got ', resp.status_code)
        return False
    print('DELETE check passed')
    
    resp = requests.options(url=mdUrl, headers=default_headers)
    if(resp.status_code != 400):
        print('OPTIONS was not failed and got ', resp.status_code)
        return False
    print('OPTIONS check passed')
 
    return True

def requestHeader():
    code, cont = restCall('metadata', 'json', default_version, {})
    if(code != 400 or 'Required metadata header not specified' not in cont):
        print('Required header was not required')
        return False
    else:
        print('Required header was needed')

    code, cont = restCall('metadata', 'text', default_version, {'Metadata': 'True', 'X-Forwarded-For' : 'Blah'})
    if(code != 400):
        print('Bad header was not blocked')
        return False
    else:
        print('X-Forwarded-For header was blocked')

    return True

def responseHeaders():
    mdUrl = createUrl('metadata?api-version={}&format=text'.format(default_version))
    resp = requests.get(url=mdUrl, headers=default_headers)
    if(resp.status_code != 200):
        print('Request failed faild')
        return False
    
    if 'text/plain; charset=utf-8' not in resp.headers['Content-Type']:
        print('Content type was not correct')
        return False
    else:
        print('Correct content type ', resp.headers['Content-Type'])

    exp_length = int(resp.headers['Content-Length'])
    act_length = len(resp.text)
    print('Length header ', exp_length)
    print('text length ', act_length)
    if(exp_length != act_length):
        print('header specified length does not match with text length')
        return False

    return True

def recursiveHelper(subPath):
    code,cont = restCall(subPath, 'text', default_version, default_headers, False)
    if(code != 200):
        print('Error!! Call to {} failed with {}'.format(subPath, code))
        return False

    for l in cont.splitlines():
        if not l.endswith('/'):
            newPath = subPath + '/' + l
            code,res = restCall(newPath, 'text', default_version, default_headers, False)
            if code == 200:
                print(code, newPath, res)
            else:
                print('Error!! Call to {} failed with {}'.format(newPath, code))
                return False
        else:
            newl = l[:-1]
            newPath = subPath + '/' + newl
            if not recursiveHelper(newPath):
                return False

    return True

def recursiveCall():
    if recursiveHelper('metadata'):
        print('Recursive test passed')
        return True
    else:
        print('Recursive test failed')
        return False

def testCompute():
    code,content = restCall('metadata/instance/compute', 'json')
    if code != 200 or len(content) ==0 or not is_json(content):
        print('Did not get valid compute metadata')
        return False

    contJson = json.loads(content)
    expected = ['name',
                'location',
                'offer',
                'osType',
                'platformFaultDomain',
                'platformUpdateDomain',
                'publisher',
                'sku',
                'version',
                'vmId',
                'vmSize'
               ]
    print()
    retVal = True
    for key in expected:
        val = contJson.get(key)
        if val == None or len(val) == 0:
            retVal = False
            print('!!!!!! Computed data missing', key)
        else:
            print(key, val)

    return retVal

def testNetworking():
    code,content = restCall('metadata/instance/network/', 'json')
    if code != 200 or len(content) ==0 or not is_json(content):
        print('Did not get valid compute metadata')
        return false

    retVal = True
    contJson = json.loads(content)

    # Attempt querying expcted networking metadata values
    # if it does not exist KeyError is thrown and that flags error
    try:
        val = contJson['interface'][0]['ipv4']['ipAddress'][0]['privateIpAddress']
        print(val)

        val = contJson['interface'][0]['ipv4']['ipAddress'][0]['publicIpAddress']
        print(val)

        val = contJson['interface'][0]['ipv4']['subnet'][0]['address']
        print(val)

        val = contJson['interface'][0]['ipv4']['subnet'][0]['prefix']
        print(val)

        val = contJson['interface'][0]['ipv6']['ipAddress']
        print(val)

        val = contJson['interface'][0]['macAddress']
        print(val)

    except KeyError as k:
        retVal = False
        print('Missing networking data point found', str(k))

    return retVal

# List of tests to run
testList = [
            baseTest, defaultFormat, urlPrefix, versionTests, queryVar, onlyGet, requestHeader, responseHeaders,
            recursiveCall, testCompute, testNetworking
           ]

def runTests():
    passCount = 0
    failCount = 0
    failedTests = []
    for test in testList:
        print('--------------------------------------------------')
        print('Running Test: {}'.format(test.__name__))
        try:
            result = test()
        except Exception as e:
            print('Test threw exception')
            traceback.print_stack()
            traceback.print_exc()
            result = False

        if(result):
            passCount += 1
            print('PASS')
        else:
            failCount += 1
            print('FAIL')
            failedTests.append(test.__name__)

        print()

    print('==================================================')
    print('{} tests passed, {} tests failed'.format(passCount, failCount))
    if failCount > 0:
        print('Following tests failed')
        print(*failedTests, sep='\n')
    return failCount == 0

try:
    if(not runTests()):
        print('!!!! Tests failed')
        sys.exit(1)
    else:
        sys.exit(0)
except Exception as e:
    print('Unhandled exception')
    traceback.print_stack()
    traceback.print_exc()



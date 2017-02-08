# encoding=utf8
import sys
import subprocess
import git, os, shutil
import os
import zipfile
import json
import urllib
from pprint import pprint
from jsonmerge import Merger
import glob

reload(sys)
sys.setdefaultencoding('utf8')

DIR_NAME = MODULE_NAME = sys.argv[1]
URL_DOWNLOAD = sys.argv[2]
modulesInAll = [MODULE_NAME]
modulesDepends = []
FINISHEDFILE = "moduleFamily.json"
PREPATH = "./component_src/"
MODULEPATH = "./" + MODULE_NAME + '/' + MODULE_NAME + '/'
TMPDEPENDPATH = "depends"
#进入工作目录
def readyForWork():
    os.chdir(PREPATH)
    # if os.path.exists(FINISHEDFILE):
    #     os.remove(FINISHEDFILE)

    if os.path.isdir(MODULE_NAME):
        shutil.rmtree(MODULE_NAME)
    os.mkdir(MODULE_NAME)
    os.chdir(MODULE_NAME)
    print "==readyForWork End==="
#获取git代码
def getModule(module_name):
    oldModulesDepends = modulesDepends
    #REMOTE_URL = "git@github.com:" + URL_DOWNLOAD + ".git" #for 服务器
    REMOTE_URL = "https://github.com/" + URL_DOWNLOAD + ".git" #for 个人
    moduleDownLoadPath = module_name
    if os.path.isdir(moduleDownLoadPath):
        shutil.rmtree(moduleDownLoadPath)
    # os.mkdir(moduleDownLoadPath) # for download by git
    #直接拉取zip文件
    url = 'https://github.com/' + URL_DOWNLOAD + '/archive/master.zip'
    zipName = 'master' + '.zip'
    os.system('wget --no-check-certificate ' + url)
    # urllib.urlretrieve(url, zipName)
    with zipfile.ZipFile(zipName) as zf:
        zf.extractall('./')
    os.rename(module_name + '-master', module_name)
    os.remove(zipName)
    #git 方式拉代码，太慢了
    # repo = git.Repo.init(module_name)
    # origin = repo.create_remote('origin' , REMOTE_URL)
    # origin.fetch()
    # origin.pull(origin.refs[0].remote_head)

    readJson(module_name)
    print "------getModule " + module_name + " Done--------"

#模块安装
def moduleInstall(module_name):
    os.system("cd " + module_name + "&& npm install")
    print "------module install end------"

#依赖模块文件位置处理
def moveDependModulePath(module_name):
    for startdir in modulesDepends:
        shutil.move(startdir + '/' + startdir, MODULE_NAME)
        shutil.rmtree(startdir)
    print "==moveDependModulePath End==="

#模块压缩
def zipModule(module_name):
    moduleZipFile = zipfile.ZipFile(module_name + ".zip","w",zipfile.ZIP_DEFLATED)
    for startdir in modulesInAll :
        for dirpath, dirnames, filenames in os.walk(startdir):
            for filename in filenames :
                moduleZipFile.write(os.path.join(dirpath , filename))
    moduleZipFile.close()
    #移动文件
    # shutil.move(module_name + ".zip","./" + module_name + "/" + module_name + ".zip")
    print "------module zip end------"

def mergeJson(module_name):
    result = {}
    #找到所有的json文件
    output = {}
    for root, dirs, files in os.walk("./"):
        for file in files:
            if file.endswith(".json"):
                # print 11111111111
                # print(os.path.join(root, file))
                infile = open(os.path.join(root, file), "rb")
                re = json.load(infile)
                if (re.has_key('dependencies')):
                    result = dict(result.items() + list(re["dependencies"].items()))
                    if (result):
                        output["dependencies"] = result
                    # print "============"
                    # print output
    jsonFile = open( "./" + module_name + "/package.json", "r")
    # print os.getcwd()
    data = json.load(jsonFile)
    jsonFile.close()
    if (data.has_key('dependencies')):
        data['dependencies'] = dict(output['dependencies'].items() + data['dependencies'].items())

    jsonFile = open("./" + module_name  + "/package.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()
    print "------mergeJson end------"

#读取本地依赖模块
def readJson(module_name):
    oldModulesDepends = modulesDepends
    jsonFilePath = file ("./" + module_name + '/package.json')
    packJson = json.load(jsonFilePath)
    if (packJson.has_key('ownModuleDownLoadPath')):
        path = packJson['ownModuleDownLoadPath']
        print path
        print "path"
        if (packJson.has_key('ownModuleDependencies')):
            for moduleName in packJson['ownModuleDependencies']:
                if (moduleName):
                    #暂时不用配置文件ownModuleDownLoadPath
                    #newModuleDependPath = path + moduleName
                    newModuleDependPath = moduleName
                    if newModuleDependPath not in modulesDepends:
                        print "==== loading module " + newModuleDependPath + "===="
                        modulesInAll.append(newModuleDependPath)
                        modulesDepends.append(newModuleDependPath)
                        getModule(newModuleDependPath)
                        # shutil.move(module_name, newModuleDependPath)
        print "=== readJson END ===="

#下载依赖文件
def loadDependsFilesAll(module_name):
    getModule(MODULE_NAME)


#结束脚本通知
def iAmEnd():
    #print os.getcwd()
    moduleFamilyFile = file('../' +  FINISHEDFILE)
    if(moduleFamilyFile):
        moduleJsonOld = json.load(moduleFamilyFile)
    else:
        moduleJsonOld = {}
    modulesJson = {}
    for modules in modulesInAll:
        modulesJson[modules] = '1'
    modulesJson = dict(moduleJsonOld.items() + modulesJson.items())
    jStr = json.dumps(modulesJson , ensure_ascii=False)
    with open('../' +  FINISHEDFILE , "w") as f:
        f.write(jStr)

def main():
    readyForWork()
    loadDependsFilesAll(MODULE_NAME)
    mergeJson(MODULE_NAME)
    moveDependModulePath(MODULE_NAME)
    # moduleInstall(MODULE_NAME)
    zipModule(MODULE_NAME)
    iAmEnd()

main()

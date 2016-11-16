# encoding=utf8
import sys
import subprocess
import git, os, shutil
import os
import zipfile
import json
from pprint import pprint
from jsonmerge import Merger
import glob

reload(sys)
sys.setdefaultencoding('utf8')

DIR_NAME = MODULE_NAME = sys.argv[1]
modulesInAll = [MODULE_NAME]
FINISHEDFILE = "pythonFinished.txt"
PREPATH = "./component_src/"
#进入工作目录
def readyForWork():
    os.chdir(PREPATH)
    if os.path.exists(FINISHEDFILE):
        os.remove(FINISHEDFILE)
        
    if os.path.isdir(MODULE_NAME):
        shutil.rmtree(MODULE_NAME)
    os.mkdir(MODULE_NAME)
    os.chdir(MODULE_NAME)

#获取git代码
def getModule(module_name):
    REMOTE_URL = "https://github.com/finance-sh/" + module_name + ".git"
    moduleDownLoadPath = module_name
    if os.path.isdir(moduleDownLoadPath):
        shutil.rmtree(moduleDownLoadPath)
    os.mkdir(moduleDownLoadPath)
    repo = git.Repo.init(module_name)
    origin = repo.create_remote('origin' , REMOTE_URL)
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)

    print "------getModule " + module_name + " Done--------"

#模块安装
def moduleInstall(module_name):
    os.system("cd " + module_name + "&& npm install")
    print "------module install end------"

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

#json文件合并
def mergeJson(module_name):
    option = {
        "properties": {
            "*": {
                "mergeStrategy": "append"
            }
        }
    }
    merger = Merger(option)
    # result = "./" + module_name + '/package.json'
    # for startdir in modulesInAll :
    #     jsonFilePath = file ("./" + startdir + '/package.json')
    #     result = merger.merge(result, jsonFilePath)
    # pprint(result, width=40)
    # print "----------json merge end ---------"

    #找到所有的json文件
    result = {
        "x" : "p"
    }
    for root, dirs, files in os.walk("./"):
        for file in files:
            if file.endswith(".json"):
                print(os.path.join(root, file))
                with open(os.path.join(root, file), "rb") as infile:
                    result = merger.merge(result, json.load(infile))
                    print "result ===================="
                    print result 
                    print "--------------------------"
    with open("merged_file.json", "wb") as outfile:
         json.dump(result, outfile)

#读取本地依赖模块
def readJson(module_name):
    jsonFilePath = file ("./" + module_name + '/package.json')
    packJson = json.load(jsonFilePath)
    path = packJson['ownModuleDownLoadPath']
    for moduleName in packJson['ownModuleDependencies']:
        modulesInAll.append(path + moduleName)
        getModule(moduleName)
        shutil.move(moduleName, path + moduleName)

#结束脚本通知
def iAmEnd():
    os.chdir("../")
    f = file(FINISHEDFILE,"w+")
    f.writelines("end")
    f.close()

def main():
    readyForWork()
    getModule(MODULE_NAME)
    readJson(MODULE_NAME)
    # moduleInstall(MODULE_NAME)
    zipModule(MODULE_NAME)
    mergeJson(MODULE_NAME)
    iAmEnd()

main()
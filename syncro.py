import yaml, os, glob, requests, json, configparser
import urllib3
import synology_api

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = configparser.ConfigParser()
config.read("config.ini")

nameAndSirenDict = {}
dataNamePathDict = {}
apiSynoUrl = config["CREDENTIALS"]["apiSynoUrl"]
account = config["CREDENTIALS"]["account"]
passwd = config["CREDENTIALS"]["passwd"]
sidToken = ""

# Login function for FileStation API
def apiSynoLogin(account, passwd, apiSynoUrl):
    global sidToken
    loginUrl = (
        apiSynoUrl
        + "/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account="
        + account
        + "&passwd="
        + passwd
        + "&session=HumHubSynchronization&format=sid"
    )
    loginResponse = requests.request("GET", loginUrl, verify=False)
    print(loginResponse.json()["data"]["sid"])
    sidToken = loginResponse.json()["data"]["sid"]


# Logout function for FileStation API
def apiSynoLogout(account, passwd, apiSynoUrl):
    logoutUrl = (
        apiSynoUrl
        + "/auth.cgi?api=SYNO.API.Auth&version=1&method=logout&session=HumHubSynchronization"
    )
    logoutResponse = requests.request("GET", logoutUrl, verify=False)
    print(logoutResponse.json())


def apiSynoSearch(apiSynoUrl, path, sid, pattern=None, extension=None):
    taskUrl = (
        apiSynoUrl
        + "/entry.cgi?api=SYNO.FileStation.Search&version=2&method=start"
        + "&folder_path="
        + path
        + "&_sid="
        + sid
    )

    if pattern is not None and extension is None:
        taskUrl = taskUrl + "&pattern=" + pattern
    elif pattern is None and extension is not None:
        taskUrl = taskUrl + "&extension=" + extension
    elif pattern is not None and extension is not None:
        taskUrl = taskUrl + "&pattern=" + pattern + "&extension=" + extension

    taskResponse = requests.request("GET", taskUrl, verify=False)

    taskResultUrl = (
        apiSynoUrl
        + '/entry.cgi?api=SYNO.FileStation.Search&version=2&method=list&taskid="'
        + taskResponse.json()["data"]["taskid"]
        + '"&_sid='
        + sid
    )
    taskResult = requests.request("GET", taskResultUrl, verify=False)
    return taskResult


# Retrive all sirens contained in the various SIREN.txt files from SynoCloud
def getSiren():
    txtPathSirenList = []
    with open("./pattern.yml", "rt", encoding="utf-8") as file:
        ymlFile = yaml.full_load(file)
        # Read in the yml file the Siren dictionary for the path that contains all the folders of the communities
        for wildcardsPath in ymlFile["Siren"]:
            # Query to search all the SIREN.txt files path
            listPathResponse = apiSynoSearch(
                apiSynoUrl, wildcardsPath, sidToken, pattern="SIREN.txt"
            )
            for path in listPathResponse.json()["data"]["files"]:
                txtPathSirenList.append(path["path"])
            # Query to read all the SIREN.txt files with the paths retrieved just before and put the sirens in sirenList
            for txtPath in txtPathSirenList:
                ReadSirenUrl = (
                    apiSynoUrl
                    + "/entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path="
                    + txtPath
                    + "&mode=open&_sid="
                    + sidToken
                )
                ReadSirenResponse = requests.request("GET", ReadSirenUrl, verify=False)
                nameAndSirenDict[
                    os.path.basename(os.path.dirname(txtPath))
                ] = ReadSirenResponse.text


# Récupération de tous les paths/noms fichiers from SynoCloud
def getDataInfo():
    dataWildcardsPathList = []
    with open("./pattern.yml", "rt", encoding="utf-8") as file:
        yml = yaml.full_load(file)
        # On récupère dans le yml le dictionnaire Pattern et on boucle dedans pour chaque chemin
        for wildcardsPatternPath in yml["Pattern"]:
            # On récupère la liste des chemins en mettant les Siren
            for name, siren in nameAndSirenDict.items():
                if (
                    "{{SIREN}}" in wildcardsPatternPath
                    and "{{NameCT}}" in wildcardsPatternPath
                ):
                    dataWildcardsPathList.append(
                        wildcardsPatternPath.replace("{{SIREN}}", siren).replace(
                            "{{NomCT}}", name.rsplit("-").rstrip()
                        )
                    )

                dataWildcardsPathList.append(
                    wildcardsPatternPath.replace("{{SIREN}}", siren).replace(
                        "{{NomCT}}", name
                    )
                )
        for dataPath in dataWildcardsPathList:
            response = apiSynoSearch(
                apiSynoUrl,
                os.path.dirname(dataPath),
                sidToken,
                pattern="*",
                extension=os.path.basename(dataPath).replace("*.", ""),
            )
            if response.json()["data"]["files"]:
                for i in range(len(response.json()["data"]["files"])):
                    dataNamePathDict[
                        response.json()["data"]["files"][i]["name"]
                    ] = response.json()["data"]["files"][i]["path"]


# Vérification de l'existance (dans HumHub) ou non des fichiers récupéré avec getData, s'ils existent on supprime du dict
def isInHumHub():
    pass


def downloadFileFromSyno():
    if not os.path.exists("tmpScriptSync"):
        os.makedirs("tmpScriptSync")

    for fileName, filePath in dataNamePathDict.items():
        downlaodUrl = (
            apiSynoUrl
            + "/entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path="
            + filePath
            + "&mode=download&_sid="
            + sidToken
        )
        response = requests.request("GET", downlaodUrl, verify=False)

        with open("tmpScriptSync/" + fileName, "wb") as f:
            f.write(response.content)


def uploadDataToHumHub():
    pass


apiSynoLogin(account, passwd, apiSynoUrl)
getSiren()
print(nameAndSirenDict)
getDataInfo()
print(dataNamePathDict)
downloadFileFromSyno()
apiSynoLogout(account, passwd, apiSynoUrl)

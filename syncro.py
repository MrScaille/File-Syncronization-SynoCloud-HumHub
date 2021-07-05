import yaml, os, glob, requests, json, configparser
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = configparser.ConfigParser()
config.read("config.ini")

sirenList = []
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


# Retrive all sirens contained in the various SIREN.txt files
def getSiren():
    txtPathSirenList = {}
    with open("./pattern.yml", "rt", encoding="utf-8") as file:
        ymlFile = yaml.full_load(file)
        # Read in the yml file the Siren dictionary for the path that contains all the folders of the communities
        for WildcardsPath in ymlFile["Siren"]:
            # Query to search all the SIREN.txt files path
            taskUrl = (
                apiSynoUrl
                + "/entry.cgi?api=SYNO.FileStation.Search&version=2&method=start&pattern=SIREN.txt&folder_path="
                + WildcardsPath
                + "&_sid="
                + sidToken
            )
            taskResponse = requests.request("GET", taskUrl, verify=False)
            # Query to get the result of the preveious one
            listPathUrl = (
                "/entry.cgi?api=SYNO.FileStation.Search&version=2&method=list&taskid="
                + taskResponse.json()["data"]["taskid"]
                + "&_sid="
                + sidToken
            )
            listPathResponse = requests.request("GET", listPathUrl, verify=False)
            for path in listPathResponse.json()["data"]["files"]:
                txtPathSirenList.append(path["path"])
            # Query to read all the SIREN.txt files with the paths retrieved just before and put the sirens in sirenList
            for txtPath in txtPathSirenList:
                ReadSirenUrl = (
                    "entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path="
                    + txtPath
                    + "&mode=open&_sid="
                    + sidToken
                )
                ReadSirenResponse = requests.request("GET", ReadSirenUrl, verify=False)
                sirenList.append(ReadSirenResponse.text)


# Récupération de tous les paths/noms fichiers
def getDataInfo():
    indice = 0
    with open("./pattern.yml", "rt", encoding="utf-8") as file:
        yml = yaml.full_load(file)
        # On récupère dans le yml le dictionnaire Pattern et on boucle dedans pour chaque chemin
        for WildcardsPatternPath in yml["Pattern"]:
            # On récupère la liste des chemins en mettant les Siren
            dataWildcardsPathList = glob.glob(
                WildcardsPatternPath.replace("{{SIREN}}", sirenList[indice])
            )
            for dataPath in dataWildcardsPathList:
                # On remplie un dict "dataName" : "dataPath" pour avoir la liste des noms et des chemins des fichiers
                dataNamePathDict[
                    os.path.basename(os.path.normpath(dataPath))
                ] = dataPath
            indice = +1


# Vérification de l'existance (dans HumHub) ou non des fichiers récupéré avec getData, s'ils existent on supprime du dict
def isInHumHub():
    pass


def downloadDataFromSyno():
    pass


def uploadDataToHumHub():
    pass


apiSynoLogin(account, passwd, apiSynoUrl)
apiSynoLogout(account, passwd, apiSynoUrl)

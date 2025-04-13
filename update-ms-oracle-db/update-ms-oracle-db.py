import os
import oracledb
import subprocess

basePath = "" # base path to the folder containing the sql files
ms_list= [] # list of subfolders containing the sql files
starting_from_version= "#VERSION#" # starting from the subfolder version

load_dir = "" # load directory in the docker container

cointainer_id = "" # docker container id


dsn_tns = oracledb.makedsn("localhost", "1521", service_name="#INSERT_SERVICE_NAME_HERE#")  # Replace with your service name
connection = oracledb.connect(user="#USER#", password="#PASSWORD#", dsn=dsn_tns)

cursor = connection.cursor()


def executeFileScripts(file_path):

    try:
        with open(file_path, "r") as file:
            sql_commands = file.read()

        sql_commands= sql_commands.strip()

        if(sql_commands.upper().startswith("CREATE OR REPLACE PROCEDURE") or "LOADFROMFILE" in file_path):
            if(sql_commands.endswith("/")):
                sql_commands= sql_commands[:-1]
            
            commands = [sql_commands]
        else : commands = sql_commands.split(";")


        for command in commands:
            command = command.strip()  
            while(command.startswith("/")):
                command = command[1:]
                command.strip()

            if command:
                try: 
                    print(f"Executing: {command}")
                    cursor.execute(command)
                    print("Executed successfully.")
                    connection.commit()
                except Exception as e:
                    print("An error occurred:", e)

        connection.commit()
        print("All commands executed and changes committed.")

    except Exception as e:
        print("An error occurred:", e)

try:
    for ms in ms_list:
        path = basePath + "STORICO " + ms # you may need to change how the path is built
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        print(folders)
        filtered_folders = [f for f in folders if f>= starting_from_version]
        for folder in filtered_folders:
            
            version_folders= [f for f in os.listdir(path + "/" +folder + "/SCRIPTS") if os.path.isdir(os.path.join(path + "/" +folder + "/SCRIPTS", f))]
            if "#props#" in version_folders:
                for file_name in os.listdir(path + "/" +folder + "/SCRIPTS/"+ "#props#"):
                    command = "docker cp " + '"' +path + "/" +folder + "/SCRIPTS/"+ "#props#/" + file_name + '" ' +  cointainer_id+":"+load_dir
                    print(command)
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    #print(result)
            
            for version_folder in version_folders:
                if(version_folder == "#props#") : continue
                for file_name in os.listdir(path + "/" +folder + "/SCRIPTS/"+ version_folder):
                    print(file_name)
                    executeFileScripts(path + "/" +folder + "/SCRIPTS/"+ version_folder + "/" + file_name)
except Exception as e:
    print(e)

finally: 
    cursor.close()
    connection.close()

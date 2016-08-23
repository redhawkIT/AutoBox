'''
Data File: data.txt
---
Username: user
Password: pass
Host: host
Route: route
Management: management
Location: location
'''

################################################################################
#                                      Imports / Constants
################################################################################

import sys, os
import time

import paramiko


DEBUG = False
BLACKBOX = True


CREDENTIAL_FILE = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'data.txt')
USERNAME = ''
PASSWORD = ''
HOST = ''
ROUTE = ''
MANAGEMENT = ''
LOCATION = ''


GENERAL_CONFIG = os.path.join(os.path.dirname(sys.argv[0]), 'configs', 'juniper.config')
CONFIG_DESTINATION = os.path.join(os.path.dirname(sys.argv[0]), 'configs')
# CONFIG_DESTINATION = '/usr/local/cf/autodiscovery/'
CONFIG_SERVER = 'http://bowser01.s.uw.edu/cf/autodiscovery/'


PROVISIONING_LOG = os.path.join(os.path.dirname(sys.argv[0]), 'records', 'NIM_log.csv')


################################################################################
#                                      Main Function
################################################################################

def main():
    #Initialize Serial, Load Credentials, and generate a log file if necessary
    loadCredentials()
    if (os.path.exists(PROVISIONING_LOG) != True):
        clearProvisioningLog()
    
    #Menu loop
    while True:
        try:
            menu()
            choice = option(0, 7)

            #Modify Credentials
            if choice == 2:
                global USERNAME, PASSWORD
                USERNAME = raw_input('Username: ').rstrip('\n')
                PASSWORD = raw_input('Password: ').rstrip('\n')
            elif choice == 2:
                global HOST
                HOST = raw_input('Host:\t').rstrip('\n')
            elif choice == 3:
                global ROUTE
                ROUTE = raw_input('Route:\t').rstrip('\n')
            elif choice == 4:
                global MANAGEMENT
                MANAGEMENT = raw_input('Management:\t').rstrip('\n')
            elif choice == 5:
                global LOCATION
                LOCATION = raw_input('Location:\t').rstrip('\n')
                
            #Create Config File
            elif choice == 6:
                createConfig()
                    
            #Push Config Over SSH
            elif choice == 7:
                configLocation = (CONFIG_SERVER + HOST + '.txt')
                commitConfig(configLocation)
                
            #Exit Sentinel
            elif choice == 0:
                sys.exit()

        except KeyboardInterrupt:
            print('\nExiting PrimeGen...\n')
            break
        except SystemExit:
            break
            
    return
            
            
            
################################################################################
#                                      Initialization
################################################################################

def loadCredentials():
    '''Auto-load a credential file, use defaults if unavailable'''
    print('-'*40)
    global USERNAME, PASSWORD, HOST, ROUTE, MANAGEMENT, LOCATION
    try:
        r = open(CREDENTIAL_FILE, 'r')
        credentials = []
        index = 0
        line = r.readline()
        while line != '':
            line = line.rstrip('\n')
            line = line.split()
            if len(line) < 2:
                line.append('')
            credentials.append(line[1])
            index += 1
            line = r.readline()    
        r.close()
        
        print('Auto-Loading credentials:\n' + CREDENTIAL_FILE)
        USERNAME = credentials[0]
        PASSWORD = credentials[1]
        HOST = credentials[2]
        ROUTE = credentials[3]
        MANAGEMENT = credentials[4]
        LOCATION = credentials[5]
        
    except Exception as e:
        print('Could not locate credentials, loading defaults')
        USERNAME = 'root'
        PASSWORD = 'Juniper1'
        HOST = '0.0.0.0'
        ROUTE = '0.0.0.0/32'
        MANAGEMENT = '1.1.1.1/24'
        LOCATION = 'UNSPECIFIED'
    print('-'*40)
    return
    
    
def menu():
    '''Display the main menu'''
    print('\n')
    print('='*40)
    print('PrimeGen for JUNOS - v 0.1')
    print('\tCode by Keller, UW-IT NIM')
    print('\tConfig by Norm, UW-IT NIM')
    print('Base File: ' + GENERAL_CONFIG)
    print('='*40)
    print('\t1) User:\t' + USERNAME + '; ' + ('*' * len(PASSWORD)))
    print('\t2) Host:\t' + HOST)
    print('\t3) Route:\t' + ROUTE)
    print('\t4) Mngmt:\t' + MANAGEMENT)
    print('\t5) Locat:\t' + LOCATION)
    print(' .'*20)
    print('\t6) Create Config File')
    print('\t7) Fetch & Commit (SSH)')
    print('='*40)
    return



################################################################################
#                                      Primary Functions
################################################################################
    
def createConfig():
    try:
        baseConfig = loadConfig(GENERAL_CONFIG)
        customConfig = generateConfig(baseConfig)
        writeConfig(CONFIG_DESTINATION, customConfig)
        
        appendProvisioningLog(HOST, ROUTE, MANAGEMENT, LOCATION)
        
    except Exception as reason:
        returnException(reason)
    finally:
        return
        
        
def commitConfig(configLocation):
    try:
        switch = ssh(HOST, USERNAME, PASSWORD)
        switch.openShell()

        print('-'*40)
        print('=== [PG] Attempting to Load Custom Config ===')
        print('\t' + configLocation)
        print('-'*40)
        
        commandList = ['cli',
        'configure exclusive',
        'load override ' + configLocation,
        'commit confirmed 10',
        'exit'
        ]
        for com in commandList:
            switch.sendShell(com)
            time.sleep(5)
            if (BLACKBOX == True):
                print('Command:\t' + com)
                switch.readShell() #Flush the buffer, but don't print
            else:
                print(switch.readShell())
            
        print('-'*40)
        print('=== [PG] Shell Open - Type "terminate" to Exit ===')
        print('\tTo confirm a commit, use "commit check"')
        print('-'*40)
        while True:
            print(switch.readShell())
            command = raw_input('[PG]' + switch.state + '\t')
            if (command.startswith('terminate')):
                break
            switch.sendShell(command)
        
    except Exception as reason:
        print('\n')
        returnException(reason)
    finally:
        try:
            switch.closeConnection()
        except:
            pass
        print('\n')
        print('-'*40)
        print('=== [PG] Session Terminated ===')
        print('-'*40)
        return

        
        
################################################################################
#                                      Configuration Templating
################################################################################

def loadConfig(configFile):
    ''' '''
    print('-'*40)
    print('Loading Config | ' + configFile)
    print(' .'*20)
    try:
        r = open(configFile, 'r')
        configData = r.read()
    except:
        raise Exception('Failed to open and/or read ' + configFile)
    finally:
        return configData

        
def generateConfig(configData):
    ''' '''
    print('Generating custom config...')
    try:
        configData = configData.replace('[HOST]', HOST)
        configData = configData.replace('[ROUTE]', ROUTE)
        configData = configData.replace('[MANAGEMENT]', MANAGEMENT)
        configData = configData.replace('[LOCATION]', LOCATION)
        if DEBUG == True:
            print(configData)
    except:
        raise Exception('Failed to make changes to initial config file')
    finally:
        return configData
    
    
def writeConfig(destination, configData):
    try:
        destination = os.path.join(destination, (HOST + '.txt'))
        print('Writing to ' + destination)
        file = open(destination, 'w')
        file.write(configData)
        file.close()
    except:
        raise Exception('Failed to write to ' + destination)
    finally:
        print('Data successfully written!')
        return

        

################################################################################
#                                      File I/O and Provisioning Logs
################################################################################
    
def appendProvisioningLog(host, route, management, location):
    '''Add an entry to provisioning logs'''
    try:
        file = open(PROVISIONING_LOG, 'a')
        file.write(host + ', ' + route + ', ' + management + ', ' + location + '\n')
        file.close()
        print('-'*40)
        print('Appended to Provisioning Logs:')
        print(' .'*20)
        print('\tHost:\t' + host)
        print('\tRoute:\t' + route)
        print('\tMngmt:\t' + management)
        print('\tLocat:\t' + location)
        print('-'*40)
    except:
        raise Exception('Failed to write to provisioning log')
    finally:
        return
    
    
def clearProvisioningLog():
    '''Reset / create a fresh provisioning log'''
    try:
        file = open(PROVISIONING_LOG, 'w')
        file.write('Host IP, Route, Management IP, Location\n')
        file.close()
        print('Provisioning records cleared to default')
        print('-'*40)
    except:
        raise Exception('Failed to write to provisioning log')
    finally:
        return
    

    
################################################################################
#                                      SSH Operations
################################################################################

class ssh:
    shell = None
    client = None
    transport = None

    
    def __init__(self, address, username, password):
        print('Connecting:\t' + str(address))
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address, 22))
        self.transport.connect(username=username, password=password)
        self.state = '>'

            
    def openShell(self):
        self.shell = self.client.invoke_shell()
        return

        
    def sendShell(self, command):
        if (self.shell):
            self.shell.send(command + '\n')
            time.sleep(1)
        else:
            print("Shell not opened.")
        return
            
            
    def readShell(self):
        time.sleep(0.2)
        
        data = ''
        if self.shell != None and self.shell.recv_ready():
            while self.shell.recv_ready():
                data += self.shell.recv(1024)
                time.sleep(0.2)
            data = str(data).replace('\r', '')
            if (len(data) > 1):
                self.state = data[-2]

        return data
        
        
    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()
        return

        
################################################################################
#                                      Tertiary Operations
################################################################################

def option(low, high):
    '''Loops until valid menu options are selected'''
    while True:
        try:
            option = int(input('Menu >    '))
            if (option >= low) and (option <= high):
                break
            else:
                print('Option must be between ' + low + '-' + high)
        except KeyboardInterrupt as reason:
            sys.exit()
        except:
            print('Option not accepted')
    print('='*40)
    return option

    
def returnException(reason):
    '''Formatting for returning an exception'''
    print('='*40)
    print(reason)
    print('Returning to Menu - see cause above')
    print('='*40)
    return
    
    
    
################################################################################
#                                      Function Calls
################################################################################

if __name__ == '__main__':
    main()
    
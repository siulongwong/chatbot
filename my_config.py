import configparser
config = configparser.ConfigParser()
config.read(r'C:\Users\Cyril\Desktop\chatbot\config.ini')
print(config['TELEGRAM']['ACCESS_TOKEN'])
import configparser

# Create object
config_file = configparser.ConfigParser()

# Basic Section
config_file.add_section("GeneralSettings")
filename = "configuration.ini"
config_file.set("GeneralSettings", "filename", filename)

# Database
config_file.add_section("DatabaseSettings")

config_file.set("DatabaseSettings", "airports_table", "airports")
config_file.set("DatabaseSettings", "countries_table", "countries")
config_file.set("DatabaseSettings", "firs_table", "firs")
config_file.set("DatabaseSettings", "general_table", "general")
config_file.set("DatabaseSettings", "idl_table", "idl")
config_file.set("DatabaseSettings", "uirs_table", "uirs")

# Save Configfile
with open(r"{}".format(filename), 'w') as configfile_obj:
    config_file.write(configfile_obj)
    configfile_obj.flush()
    configfile_obj.close()

print("Config file '{}' created".format(filename))

# List the config
read_file = open(filename, 'r')
file_content = read_file.read()
print("Content of the config file are:\n")
print(file_content)
read_file.flush()
read_file.close()
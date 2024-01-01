import os


this_file_dir = os.path.dirname(__file__)
project_root = os.path.dirname(this_file_dir)
data = os.path.join(project_root, 'downloads', 'foto.jpg')

print(this_file_dir)
# print(project_root)
# print(data1)
# print(os.path.dirname(os.getcwd()))

subdirs_list = [name for name in os.listdir(this_file_dir) if os.path.isdir(os.path.join(this_file_dir, name))]
print(subdirs_list)

# print(os.listdir(this_file_dir))

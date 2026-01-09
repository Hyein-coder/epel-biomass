"""
GPT-generated - no works
"""
import shutil
import os
import win32com

gen_py_path = os.path.join(os.path.dirname(win32com.__file__), 'gen_py')
shutil.rmtree(gen_py_path, ignore_errors=True)

#%%
from win32com.client import gencache
gencache.EnsureDispatch('Excel.Application')


#%%
import shutil
import os
import win32com

# Primary gen_py folder
gen_py_main = os.path.join(os.path.dirname(win32com.__file__), 'gen_py')
print(f"Removing: {gen_py_main}")
shutil.rmtree(gen_py_main, ignore_errors=True)

# Also clear the temp one if it exists
import tempfile
temp_path = os.path.join(tempfile.gettempdir(), 'gen_py')
print(f"Removing: {temp_path}")
shutil.rmtree(temp_path, ignore_errors=True)

#%%
import os

path = r"C:\Users\Hyein\anaconda3\envs\Analysis\Lib\site-packages\win32com\gen_py"
os.makedirs(path, exist_ok=True)


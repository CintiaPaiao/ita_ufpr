from abc import ABC,abstractmethod
import pandas as pd
class DataSource(ABC):
    @abstractmethod
    def read(self):...
class ExcelSource(DataSource):
    def __init__(self,obj,sheet_name=0):self.obj=obj;self.sheet_name=sheet_name
    def read(self):return pd.read_excel(self.obj,sheet_name=self.sheet_name)
class CsvSource(DataSource):
    def __init__(self,obj,**kwargs):self.obj=obj;self.kwargs=kwargs
    def read(self):return pd.read_csv(self.obj,**self.kwargs)
class GoogleSheetsSource(DataSource):
    def __init__(self,url):self.url=url
    def read(self):return pd.read_excel(self.url)
class GoogleDriveSource(DataSource):
    def __init__(self,file_id,credentials=None):self.file_id=file_id;self.credentials=credentials
    def read(self):raise NotImplementedError('Google Drive API depende de credenciais institucionais; use upload manual no MVP.')

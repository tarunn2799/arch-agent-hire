import gspread
import os
from typing import List, Dict, Any
import streamlit as st 

class GSpreadUtils:
    def __init__(self):
        """Initialize with Google Sheets API credentials."""
        credentials_json = json.loads(st.secrets["gspread"]["credentials_file"])
        self.gc = gspread.service_account_from_dict(credentials_json)
    
    def open_by_key(self, sheet_key: str):
        """Open a spreadsheet using its key."""
        self.sh = self.gc.open_by_key(sheet_key)
    
    def get_worksheet(self, title: str):
        """Retrieve a worksheet by title."""
        return self.sh.worksheet(title)
    
    def create_sheet(self, title: str, rows: int = 100, cols: int = 20):
        """Create a new sheet in the spreadsheet."""
        return self.sh.add_worksheet(title=title, rows=rows, cols=cols)
    
    def append_row(self, sheet_name: str, row_data: List[Any]):
        """Append a row of data to the specified worksheet."""
        worksheet = self.get_worksheet(sheet_name)
        worksheet.append_row(row_data)
    
    def get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Retrieve all records from the specified worksheet."""
        worksheet = self.get_worksheet(sheet_name)
        return worksheet.get_all_records()
    
    def update_cell(self, sheet_name: str, row: int, col: int, value: Any):
        """Update a specific cell in the specified worksheet."""
        worksheet = self.get_worksheet(sheet_name)
        worksheet.update_cell(row, col, value)
    
    def delete_row(self, sheet_name: str, row: int):
        """Delete a specific row in the specified worksheet."""
        worksheet = self.get_worksheet(sheet_name)
        worksheet.delete_rows(row)

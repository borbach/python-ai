import json
import re
from typing import Dict, List, Optional, Union, Any
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time

class SpreadsheetCell:
    """Represents a single cell in the spreadsheet"""
    def __init__(self, value: Any = None, formula: str = None):
        self.value = value
        self.formula = formula
        self.last_updated = datetime.now()
    
    def to_dict(self):
        return {
            'value': self.value,
            'formula': self.formula,
            'last_updated': self.last_updated.isoformat()
        }

class LLMSpreadsheet:
    """Main spreadsheet class with LLM-accessible API methods"""
    
    def __init__(self, max_rows: int = 1000, max_cols: int = 100):
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.cells: Dict[str, SpreadsheetCell] = {}
        self.metadata = {
            'created': datetime.now(),
            'last_modified': datetime.now(),
            'version': '1.0'
        }
    
    def _validate_cell_reference(self, cell_ref: str) -> bool:
        """Validate cell reference format (e.g., A1, B2, AA10)"""
        pattern = r'^[A-Z]+[1-9]\d*$'
        return bool(re.match(pattern, cell_ref.upper()))
    
    def _parse_cell_reference(self, cell_ref: str) -> tuple:
        """Parse cell reference into row and column indices"""
        cell_ref = cell_ref.upper()
        col_str = re.match(r'^[A-Z]+', cell_ref).group()
        row_str = re.match(r'[1-9]\d*$', cell_ref[len(col_str):]).group()
        
        # Convert column letters to number (A=1, B=2, ..., Z=26, AA=27, etc.)
        col_num = 0
        for i, char in enumerate(reversed(col_str)):
            col_num += (ord(char) - ord('A') + 1) * (26 ** i)
        
        return int(row_str), col_num
    
    def _number_to_column(self, col_num: int) -> str:
        """Convert column number to letters (1=A, 2=B, ..., 27=AA, etc.)"""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord('A')) + result
            col_num //= 26
        return result
    
    def _cell_reference_from_indices(self, row: int, col: int) -> str:
        """Create cell reference from row and column indices"""
        return f"{self._number_to_column(col)}{row}"
    
    def set_cell(self, cell_ref: str, value: Any, formula: str = None) -> Dict[str, Any]:
        """Set value in a specific cell"""
        if not self._validate_cell_reference(cell_ref):
            return {'success': False, 'error': f'Invalid cell reference: {cell_ref}'}
        
        row, col = self._parse_cell_reference(cell_ref)
        if row > self.max_rows or col > self.max_cols:
            return {'success': False, 'error': f'Cell reference out of bounds: {cell_ref}'}
        
        # Convert value to appropriate type
        if isinstance(value, str) and value.strip():
            try:
                # Try to convert to number
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if not a number
                pass
        
        self.cells[cell_ref.upper()] = SpreadsheetCell(value, formula)
        self.metadata['last_modified'] = datetime.now()
        
        return {
            'success': True, 
            'cell': cell_ref.upper(), 
            'value': value,
            'message': f'Cell {cell_ref.upper()} set to {value}'
        }
    
    def get_cell(self, cell_ref: str) -> Dict[str, Any]:
        """Get value from a specific cell"""
        if not self._validate_cell_reference(cell_ref):
            return {'success': False, 'error': f'Invalid cell reference: {cell_ref}'}
        
        cell_ref = cell_ref.upper()
        if cell_ref in self.cells:
            cell = self.cells[cell_ref]
            return {
                'success': True,
                'cell': cell_ref,
                'value': cell.value,
                'formula': cell.formula,
                'last_updated': cell.last_updated.isoformat()
            }
        else:
            return {
                'success': True,
                'cell': cell_ref,
                'value': None,
                'message': 'Cell is empty'
            }
    
    def set_range(self, start_cell: str, end_cell: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Set values in a range of cells"""
        if not self._validate_cell_reference(start_cell) or not self._validate_cell_reference(end_cell):
            return {'success': False, 'error': 'Invalid cell reference in range'}
        
        start_row, start_col = self._parse_cell_reference(start_cell)
        end_row, end_col = self._parse_cell_reference(end_cell)
        
        results = []
        for i, row_values in enumerate(values):
            for j, value in enumerate(row_values):
                current_row = start_row + i
                current_col = start_col + j
                
                if current_row <= end_row and current_col <= end_col:
                    cell_ref = self._cell_reference_from_indices(current_row, current_col)
                    result = self.set_cell(cell_ref, value)
                    results.append(result)
        
        return {
            'success': True,
            'cells_updated': len(results),
            'results': results
        }
    
    def get_range(self, start_cell: str, end_cell: str) -> Dict[str, Any]:
        """Get values from a range of cells"""
        if not self._validate_cell_reference(start_cell) or not self._validate_cell_reference(end_cell):
            return {'success': False, 'error': 'Invalid cell reference in range'}
        
        start_row, start_col = self._parse_cell_reference(start_cell)
        end_row, end_col = self._parse_cell_reference(end_cell)
        
        values = []
        for row in range(start_row, end_row + 1):
            row_values = []
            for col in range(start_col, end_col + 1):
                cell_ref = self._cell_reference_from_indices(row, col)
                cell_data = self.get_cell(cell_ref)
                row_values.append(cell_data.get('value'))
            values.append(row_values)
        
        return {
            'success': True,
            'range': f'{start_cell.upper()}:{end_cell.upper()}',
            'values': values
        }
    
    def sum_row(self, row_number: int, start_col: str = 'A', end_col: str = None) -> Dict[str, Any]:
        """Sum all values in a row"""
        if end_col is None:
            # Find the last non-empty cell in the row
            end_col_num = 1
            for cell_ref, cell in self.cells.items():
                cell_row, cell_col = self._parse_cell_reference(cell_ref)
                if cell_row == row_number and cell.value is not None:
                    end_col_num = max(end_col_num, cell_col)
            end_col = self._number_to_column(end_col_num)
        
        start_cell = f"{start_col.upper()}{row_number}"
        end_cell = f"{end_col.upper()}{row_number}"
        
        range_data = self.get_range(start_cell, end_cell)
        if not range_data['success']:
            return range_data
        
        total = 0
        count = 0
        for row_values in range_data['values']:
            for value in row_values:
                if isinstance(value, (int, float)):
                    total += value
                    count += 1
        
        return {
            'success': True,
            'operation': 'sum_row',
            'row': row_number,
            'range': f'{start_cell}:{end_cell}',
            'sum': total,
            'cells_counted': count
        }
    
    def sum_column(self, column: str, start_row: int = 1, end_row: int = None) -> Dict[str, Any]:
        """Sum all values in a column"""
        column = column.upper()
        if end_row is None:
            # Find the last non-empty cell in the column
            end_row = 1
            for cell_ref, cell in self.cells.items():
                if cell_ref.startswith(column) and cell.value is not None:
                    cell_row, _ = self._parse_cell_reference(cell_ref)
                    end_row = max(end_row, cell_row)
        
        start_cell = f"{column}{start_row}"
        end_cell = f"{column}{end_row}"
        
        range_data = self.get_range(start_cell, end_cell)
        if not range_data['success']:
            return range_data
        
        total = 0
        count = 0
        for row_values in range_data['values']:
            for value in row_values:
                if isinstance(value, (int, float)):
                    total += value
                    count += 1
        
        return {
            'success': True,
            'operation': 'sum_column',
            'column': column,
            'range': f'{start_cell}:{end_cell}',
            'sum': total,
            'cells_counted': count
        }
    
    def average_row(self, row_number: int, start_col: str = 'A', end_col: str = None) -> Dict[str, Any]:
        """Calculate average of values in a row"""
        sum_result = self.sum_row(row_number, start_col, end_col)
        if not sum_result['success']:
            return sum_result
        
        count = sum_result['cells_counted']
        if count == 0:
            return {
                'success': False,
                'error': 'No numeric values found in row'
            }
        
        average = sum_result['sum'] / count
        
        return {
            'success': True,
            'operation': 'average_row',
            'row': row_number,
            'range': sum_result['range'],
            'average': average,
            'sum': sum_result['sum'],
            'cells_counted': count
        }
    
    def average_column(self, column: str, start_row: int = 1, end_row: int = None) -> Dict[str, Any]:
        """Calculate average of values in a column"""
        sum_result = self.sum_column(column, start_row, end_row)
        if not sum_result['success']:
            return sum_result
        
        count = sum_result['cells_counted']
        if count == 0:
            return {
                'success': False,
                'error': 'No numeric values found in column'
            }
        
        average = sum_result['sum'] / count
        
        return {
            'success': True,
            'operation': 'average_column',
            'column': column.upper(),
            'range': sum_result['range'],
            'average': average,
            'sum': sum_result['sum'],
            'cells_counted': count
        }
    
    def clear_cell(self, cell_ref: str) -> Dict[str, Any]:
        """Clear a specific cell"""
        if not self._validate_cell_reference(cell_ref):
            return {'success': False, 'error': f'Invalid cell reference: {cell_ref}'}
        
        cell_ref = cell_ref.upper()
        if cell_ref in self.cells:
            del self.cells[cell_ref]
            self.metadata['last_modified'] = datetime.now()
            return {
                'success': True,
                'message': f'Cell {cell_ref} cleared'
            }
        else:
            return {
                'success': True,
                'message': f'Cell {cell_ref} was already empty'
            }
    
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """Get information about the spreadsheet"""
        return {
            'success': True,
            'info': {
                'max_rows': self.max_rows,
                'max_cols': self.max_cols,
                'cells_used': len(self.cells),
                'metadata': {
                    'created': self.metadata['created'].isoformat(),
                    'last_modified': self.metadata['last_modified'].isoformat(),
                    'version': self.metadata['version']
                }
            }
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export entire spreadsheet to dictionary"""
        return {
            'cells': {k: v.to_dict() for k, v in self.cells.items()},
            'metadata': {
                'created': self.metadata['created'].isoformat(),
                'last_modified': self.metadata['last_modified'].isoformat(),
                'version': self.metadata['version'],
                'max_rows': self.max_rows,
                'max_cols': self.max_cols
            }
        }

# Global spreadsheet instance
spreadsheet = LLMSpreadsheet()

# Flask API
app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'LLM Spreadsheet API'
    })

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get spreadsheet information"""
    return jsonify(spreadsheet.get_spreadsheet_info())

@app.route('/api/cell/<cell_ref>', methods=['GET'])
def get_cell_api(cell_ref):
    """Get cell value via API"""
    return jsonify(spreadsheet.get_cell(cell_ref))

@app.route('/api/cell/<cell_ref>', methods=['POST'])
def set_cell_api(cell_ref):
    """Set cell value via API"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    value = data.get('value')
    formula = data.get('formula')
    
    return jsonify(spreadsheet.set_cell(cell_ref, value, formula))

@app.route('/api/cell/<cell_ref>', methods=['DELETE'])
def clear_cell_api(cell_ref):
    """Clear cell via API"""
    return jsonify(spreadsheet.clear_cell(cell_ref))

@app.route('/api/range', methods=['GET'])
def get_range_api():
    """Get range of cells via API"""
    start_cell = request.args.get('start')
    end_cell = request.args.get('end')
    
    if not start_cell or not end_cell:
        return jsonify({
            'success': False, 
            'error': 'Both start and end parameters required'
        }), 400
    
    return jsonify(spreadsheet.get_range(start_cell, end_cell))

@app.route('/api/range', methods=['POST'])
def set_range_api():
    """Set range of cells via API"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    start_cell = data.get('start')
    end_cell = data.get('end')
    values = data.get('values')
    
    if not all([start_cell, end_cell, values]):
        return jsonify({
            'success': False, 
            'error': 'start, end, and values parameters required'
        }), 400
    
    return jsonify(spreadsheet.set_range(start_cell, end_cell, values))

@app.route('/api/sum/row/<int:row>', methods=['GET'])
def sum_row_api(row):
    """Sum row via API"""
    start_col = request.args.get('start_col', 'A')
    end_col = request.args.get('end_col')
    
    return jsonify(spreadsheet.sum_row(row, start_col, end_col))

@app.route('/api/sum/column/<column>', methods=['GET'])
def sum_column_api(column):
    """Sum column via API"""
    start_row = int(request.args.get('start_row', 1))
    end_row = request.args.get('end_row')
    if end_row:
        end_row = int(end_row)
    
    return jsonify(spreadsheet.sum_column(column, start_row, end_row))

@app.route('/api/average/row/<int:row>', methods=['GET'])
def average_row_api(row):
    """Average row via API"""
    start_col = request.args.get('start_col', 'A')
    end_col = request.args.get('end_col')
    
    return jsonify(spreadsheet.average_row(row, start_col, end_col))

@app.route('/api/average/column/<column>', methods=['GET'])
def average_column_api(column):
    """Average column via API"""
    start_row = int(request.args.get('start_row', 1))
    end_row = request.args.get('end_row')
    if end_row:
        end_row = int(end_row)
    
    return jsonify(spreadsheet.average_column(column, start_row, end_row))

@app.route('/api/export', methods=['GET'])
def export_spreadsheet():
    """Export entire spreadsheet"""
    return jsonify(spreadsheet.export_to_dict())

@app.route('/api/bulk', methods=['POST'])
def bulk_operations():
    """Perform multiple operations in one request"""
    data = request.get_json()
    if not data or 'operations' not in data:
        return jsonify({
            'success': False, 
            'error': 'operations array required'
        }), 400
    
    results = []
    for op in data['operations']:
        op_type = op.get('type')
        
        if op_type == 'set_cell':
            result = spreadsheet.set_cell(op['cell'], op['value'], op.get('formula'))
        elif op_type == 'get_cell':
            result = spreadsheet.get_cell(op['cell'])
        elif op_type == 'sum_row':
            result = spreadsheet.sum_row(op['row'], op.get('start_col', 'A'), op.get('end_col'))
        elif op_type == 'sum_column':
            result = spreadsheet.sum_column(op['column'], op.get('start_row', 1), op.get('end_row'))
        elif op_type == 'average_row':
            result = spreadsheet.average_row(op['row'], op.get('start_col', 'A'), op.get('end_col'))
        elif op_type == 'average_column':
            result = spreadsheet.average_column(op['column'], op.get('start_row', 1), op.get('end_row'))
        else:
            result = {'success': False, 'error': f'Unknown operation type: {op_type}'}
        
        results.append({'operation': op, 'result': result})
    
    return jsonify({
        'success': True,
        'operations_completed': len(results),
        'results': results
    })

def run_server():
    """Run the Flask server"""
    print("Starting LLM Spreadsheet API Server...")
    print("API Documentation:")
    print("==================")
    print("GET    /api/health                    - Health check")
    print("GET    /api/info                      - Spreadsheet info")
    print("GET    /api/cell/<cell_ref>           - Get cell value")
    print("POST   /api/cell/<cell_ref>           - Set cell value")
    print("DELETE /api/cell/<cell_ref>           - Clear cell")
    print("GET    /api/range?start=A1&end=B2     - Get range values")
    print("POST   /api/range                     - Set range values")
    print("GET    /api/sum/row/<row>             - Sum row")
    print("GET    /api/sum/column/<column>       - Sum column")
    print("GET    /api/average/row/<row>         - Average row")
    print("GET    /api/average/column/<column>   - Average column")
    print("GET    /api/export                    - Export spreadsheet")
    print("POST   /api/bulk                      - Bulk operations")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Example usage
    print("LLM Spreadsheet API")
    print("===================")
    
    # Test the spreadsheet functionality
    print("\n--- Testing Spreadsheet Operations ---")
    
    # Set some sample data
    spreadsheet.set_cell('A1', 10)
    spreadsheet.set_cell('A2', 20)
    spreadsheet.set_cell('A3', 30)
    spreadsheet.set_cell('B1', 5)
    spreadsheet.set_cell('B2', 15)
    spreadsheet.set_cell('B3', 25)
    
    # Test operations
    print("Sample data set in A1:B3")
    print("Sum of row 1:", spreadsheet.sum_row(1))
    print("Sum of column A:", spreadsheet.sum_column('A'))
    print("Average of row 2:", spreadsheet.average_row(2))
    print("Average of column B:", spreadsheet.average_column('B'))
    
    # Start the API server
    print("\n--- Starting API Server ---")
    run_server()




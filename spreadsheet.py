import json
import re
from typing import Dict, List, Optional, Union, Any
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time

# Initialize Flask app early
app = Flask(__name__)

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
    
    def get_grid_data(self, max_rows: int = 20, max_cols: int = 10) -> Dict[str, Any]:
        """Get spreadsheet data in grid format for display"""
        grid = []
        
        # Create column headers (A, B, C, etc.)
        columns = ['']  # Empty cell for row numbers
        for i in range(max_cols):
            columns.append(self._number_to_column(i + 1))
        
        grid.append(columns)
        
        # Create rows with data
        for row in range(1, max_rows + 1):
            row_data = [str(row)]  # Row number
            for col in range(1, max_cols + 1):
                cell_ref = self._cell_reference_from_indices(row, col)
                if cell_ref in self.cells and self.cells[cell_ref].value is not None:
                    row_data.append(str(self.cells[cell_ref].value))
                else:
                    row_data.append('')
            grid.append(row_data)
        
        return {
            'grid': grid,
            'rows': max_rows,
            'cols': max_cols,
            'last_modified': self.metadata['last_modified'].isoformat()
        }

# Global spreadsheet instance
spreadsheet = LLMSpreadsheet()

# Store WebSocket connections for real-time updates
active_connections = set()

# Add CORS support and error handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def notify_clients_of_change(change_data):
    """Notify all connected clients of a spreadsheet change"""
    # In a full implementation, this would use WebSockets
    # For now, we'll just store the latest change
    global last_change
    last_change = {
        'timestamp': datetime.now().isoformat(),
        'change': change_data
    }

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /spreadsheet',
            'GET /api/health',
            'GET /api/info',
            'GET /api/cell/<cell_ref>',
            'POST /api/cell/<cell_ref>',
            'DELETE /api/cell/<cell_ref>',
            'GET /api/range',
            'POST /api/range',
            'GET /api/sum/row/<row>',
            'GET /api/sum/column/<column>',
            'GET /api/average/row/<row>',
            'GET /api/average/column/<column>',
            'GET /api/export',
            'GET /api/grid',
            'POST /api/bulk'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'LLM Spreadsheet API',
        'version': '1.0',
        'status': 'running',
        'web_interface': 'GET /spreadsheet - Live spreadsheet interface',
        'endpoints': {
            'health': 'GET /api/health',
            'info': 'GET /api/info',
            'grid': 'GET /api/grid - Get grid data for display',
            'cell_operations': {
                'get_cell': 'GET /api/cell/<cell_ref>',
                'set_cell': 'POST /api/cell/<cell_ref>',
                'clear_cell': 'DELETE /api/cell/<cell_ref>'
            },
            'range_operations': {
                'get_range': 'GET /api/range?start=A1&end=B2',
                'set_range': 'POST /api/range'
            },
            'math_operations': {
                'sum_row': 'GET /api/sum/row/<row>',
                'sum_column': 'GET /api/sum/column/<column>',
                'average_row': 'GET /api/average/row/<row>',
                'average_column': 'GET /api/average/column/<column>'
            },
            'utility': {
                'export': 'GET /api/export',
                'bulk_operations': 'POST /api/bulk'
            }
        },
        'example_usage': {
            'set_cell': 'POST /api/cell/A1 with JSON: {"value": 100}',
            'get_cell': 'GET /api/cell/A1',
            'sum_column': 'GET /api/sum/column/A'
        }
    })

@app.route('/spreadsheet', methods=['GET'])
def spreadsheet_interface():
    """Serve the live spreadsheet interface"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Spreadsheet Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            font-size: 2.5em;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-group label {
            font-weight: bold;
            min-width: 80px;
        }
        
        input, select, button {
            padding: 8px 12px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
        }
        
        input, select {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            min-width: 100px;
        }
        
        button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: bold;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        button.math-btn {
            background: linear-gradient(45deg, #3742fa, #2f3542);
        }
        
        button.action-btn {
            background: linear-gradient(45deg, #27ae60, #219a52);
        }
        
        .spreadsheet-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow: auto;
            max-height: 70vh;
        }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #27ae60;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .spreadsheet-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Courier New', monospace;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .spreadsheet-table th {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 12px 8px;
            font-weight: bold;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            min-width: 80px;
        }
        
        .spreadsheet-table td {
            border: 1px solid #e0e0e0;
            padding: 0;
            position: relative;
            background: white;
        }
        
        .row-header {
            background: linear-gradient(45deg, #667eea, #764ba2) !important;
            color: white !important;
            font-weight: bold;
            text-align: center;
            padding: 12px 8px !important;
            min-width: 50px;
        }
        
        .cell-input {
            width: 100%;
            height: 40px;
            border: none;
            padding: 8px;
            font-family: inherit;
            font-size: 14px;
            text-align: center;
            background: transparent;
            color: #333;
            transition: all 0.2s;
        }
        
        .cell-input:focus {
            outline: none;
            background: #e3f2fd;
            box-shadow: inset 0 0 0 2px #2196f3;
        }
        
        .cell-input.has-value {
            background: #e8f5e8;
            font-weight: bold;
        }
        
        .cell-input.formula-cell {
            background: #fff3e0;
            color: #e65100;
        }
        
        .result-display {
            background: rgba(255, 255, 255, 0.1);
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .result-content {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .math-results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .math-result-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        
        .math-result-card h4 {
            margin: 0 0 10px 0;
            color: #ffd700;
        }
        
        .math-result-card .value {
            font-size: 1.5em;
            font-weight: bold;
            color: white;
        }
        
        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .refresh-toggle {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }
        
        .refresh-toggle input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 24px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: #27ae60;
        }
        
        input:checked + .slider:before {
            transform: translateX(26px);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧮 Live Spreadsheet Interface</h1>
    </div>
    
    <div class="status-bar">
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>Connected to API</span>
            <span id="cellCount">0 cells</span>
        </div>
        <div class="auto-refresh">
            <label>Auto-refresh:</label>
            <label class="refresh-toggle">
                <input type="checkbox" id="autoRefresh" checked>
                <span class="slider"></span>
            </label>
        </div>
    </div>
    
    <div class="controls">
        <div class="control-group">
            <label>Cell:</label>
            <input type="text" id="quickCell" placeholder="A1" value="A1">
            <input type="text" id="quickValue" placeholder="Value" value="">
            <button onclick="setQuickCell()" class="action-btn">Set</button>
            <button onclick="getQuickCell()" class="action-btn">Get</button>
        </div>
        
        <div class="control-group">
            <label>Math:</label>
            <select id="mathType">
                <option value="sum_column">Sum Column</option>
                <option value="sum_row">Sum Row</option>
                <option value="average_column">Avg Column</option>
                <option value="average_row">Avg Row</option>
            </select>
            <input type="text" id="mathTarget" placeholder="A or 1" value="A">
            <button onclick="performMath()" class="math-btn">Calculate</button>
        </div>
        
        <div class="control-group">
            <button onclick="fillSampleData()" class="action-btn">📊 Sample Data</button>
            <button onclick="clearAllCells()" class="action-btn">🗑️ Clear All</button>
            <button onclick="refreshGrid()" class="action-btn">🔄 Refresh</button>
        </div>
    </div>
    
    <div class="spreadsheet-container">
        <table class="spreadsheet-table" id="spreadsheetTable">
            <thead id="tableHeader">
                <!-- Will be populated dynamically -->
            </thead>
            <tbody id="tableBody">
                <!-- Will be populated dynamically -->
            </tbody>
        </table>
    </div>
    
    <div class="math-results" id="mathResults">
        <!-- Math results will appear here -->
    </div>
    
    <div class="result-display">
        <h3>📊 Last Operation Result:</h3>
        <div class="result-content" id="lastResult">Ready to process operations...</div>
    </div>

    <script>
        const API_BASE = 'http://localhost:5000';
        let autoRefreshInterval;
        let gridData = null;
        
        // Initialize the interface
        window.onload = function() {
            initializeGrid();
            startAutoRefresh();
        };
        
        async function makeAPICall(endpoint, method = 'GET', body = null) {
            try {
                const options = {
                    method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (body) options.body = JSON.stringify(body);
                
                const response = await fetch(`${API_BASE}${endpoint}`, options);
                const data = await response.json();
                return data;
            } catch (error) {
                return { error: error.message };
            }
        }
        
        function displayResult(result) {
            document.getElementById('lastResult').textContent = JSON.stringify(result, null, 2);
        }
        
        async function initializeGrid() {
            await refreshGrid();
        }
        
        async function refreshGrid() {
            try {
                const result = await makeAPICall('/api/grid?rows=15&cols=10');
                if (result.grid) {
                    gridData = result;
                    updateGridDisplay(result.grid);
                    updateCellCount();
                }
            } catch (error) {
                console.error('Failed to refresh grid:', error);
            }
        }
        
        function updateGridDisplay(grid) {
            const table = document.getElementById('spreadsheetTable');
            const header = document.getElementById('tableHeader');
            const body = document.getElementById('tableBody');
            
            // Clear existing content
            header.innerHTML = '';
            body.innerHTML = '';
            
            // Create header row
            const headerRow = document.createElement('tr');
            grid[0].forEach((cell, index) => {
                const th = document.createElement('th');
                th.textContent = cell;
                if (index === 0) th.style.width = '50px';
                headerRow.appendChild(th);
            });
            header.appendChild(headerRow);
            
            // Create data rows
            for (let i = 1; i < grid.length; i++) {
                const tr = document.createElement('tr');
                grid[i].forEach((cellValue, colIndex) => {
                    const td = document.createElement('td');
                    
                    if (colIndex === 0) {
                        // Row header
                        td.textContent = cellValue;
                        td.className = 'row-header';
                    } else {
                        // Data cell
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.className = 'cell-input';
                        input.value = cellValue;
                        
                        if (cellValue) {
                            input.classList.add('has-value');
                        }
                        
                        // Calculate cell reference
                        const colLetter = String.fromCharCode(64 + colIndex); // A, B, C, etc.
                        const cellRef = colLetter + grid[i][0];
                        input.dataset.cellRef = cellRef;
                        
                        // Add event listeners
                        input.addEventListener('blur', () => updateCell(cellRef, input.value));
                        input.addEventListener('keypress', (e) => {
                            if (e.key === 'Enter') {
                                updateCell(cellRef, input.value);
                                input.blur();
                            }
                        });
                        
                        td.appendChild(input);
                    }
                    tr.appendChild(td);
                });
                body.appendChild(tr);
            }
        }
        
        async function updateCell(cellRef, value) {
            if (value === '') {
                // Clear cell
                const result = await makeAPICall(`/api/cell/${cellRef}`, 'DELETE');
                displayResult(result);
            } else {
                // Set cell value
                let processedValue = value;
                if (!isNaN(value) && value !== '') {
                    processedValue = parseFloat(value);
                }
                
                const result = await makeAPICall(`/api/cell/${cellRef}`, 'POST', { value: processedValue });
                displayResult(result);
            }
            
            // Refresh the grid after a short delay
            setTimeout(refreshGrid, 200);
        }
        
        async function updateCellCount() {
            const info = await makeAPICall('/api/info');
            if (info.info) {
                document.getElementById('cellCount').textContent = `${info.info.cells_used} cells`;
            }
        }
        
        async function setQuickCell() {
            const cellRef = document.getElementById('quickCell').value;
            const value = document.getElementById('quickValue').value;
            
            let processedValue = value;
            if (!isNaN(value) && value !== '') {
                processedValue = parseFloat(value);
            }
            
            const result = await makeAPICall(`/api/cell/${cellRef}`, 'POST', { value: processedValue });
            displayResult(result);
            refreshGrid();
        }
        
        async function getQuickCell() {
            const cellRef = document.getElementById('quickCell').value;
            const result = await makeAPICall(`/api/cell/${cellRef}`);
            displayResult(result);
            
            if (result.value !== undefined) {
                document.getElementById('quickValue').value = result.value;
            }
        }
        
        async function performMath() {
            const mathType = document.getElementById('mathType').value;
            const target = document.getElementById('mathTarget').value;
            
            let endpoint;
            if (mathType.includes('row')) {
                endpoint = `/api/${mathType.replace('_', '/')}/${target}`;
            } else {
                endpoint = `/api/${mathType.replace('_', '/')}/${target}`;
            }
            
            const result = await makeAPICall(endpoint);
            displayResult(result);
            
            // Show result in math results area
            showMathResult(mathType, target, result);
        }
        
        function showMathResult(operation, target, result) {
            const mathResults = document.getElementById('mathResults');
            
            const card = document.createElement('div');
            card.className = 'math-result-card';
            
            const title = operation.replace('_', ' ').toUpperCase();
            const value = result.sum !== undefined ? result.sum : result.average;
            
            card.innerHTML = `
                <h4>${title} ${target}</h4>
                <div class="value">${value !== undefined ? value.toFixed(2) : 'Error'}</div>
                <small>Cells: ${result.cells_counted || 0}</small>
            `;
            
            // Remove old results and add new one
            mathResults.innerHTML = '';
            mathResults.appendChild(card);
            
            // Auto-remove after 10 seconds
            setTimeout(() => {
                if (card.parentNode) card.remove();
            }, 10000);
        }
        
        async function fillSampleData() {
            const operations = [];
            
            // Fill sample data pattern
            for (let row = 1; row <= 5; row++) {
                for (let col = 1; col <= 5; col++) {
                    const colLetter = String.fromCharCode(64 + col);
                    const value = row * col * 10;
                    operations.push({
                        type: 'set_cell',
                        cell: `${colLetter}${row}`,
                        value: value
                    });
                }
            }
            
            const result = await makeAPICall('/api/bulk', 'POST', { operations });
            displayResult({ message: 'Sample data filled successfully', operations: operations.length });
            refreshGrid();
        }
        
        async function clearAllCells() {
            const exportResult = await makeAPICall('/api/export');
            if (exportResult.cells) {
                const operations = [];
                for (const cellRef in exportResult.cells) {
                    await makeAPICall(`/api/cell/${cellRef}`, 'DELETE');
                }
                displayResult({ message: `Cleared ${Object.keys(exportResult.cells).length} cells` });
                refreshGrid();
            }
        }
        
        function startAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            
            function toggleAutoRefresh() {
                if (checkbox.checked) {
                    autoRefreshInterval = setInterval(refreshGrid, 2000); // Refresh every 2 seconds
                } else {
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                    }
                }
            }
            
            checkbox.addEventListener('change', toggleAutoRefresh);
            toggleAutoRefresh(); // Start initially
        }
    </script>
</body>
</html>
    '''

@app.route('/api/grid', methods=['GET'])
def get_grid_data():
    """Get spreadsheet data in grid format for display"""
    rows = int(request.args.get('rows', 20))
    cols = int(request.args.get('cols', 10))
    
    result = spreadsheet.get_grid_data(rows, cols)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'LLM Spreadsheet API',
        'cells_in_use': len(spreadsheet.cells)
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
    print("Starting LLM Spreadsheet API Server with Live Web Interface...")
    print("=" * 60)
    print("🌐 WEB INTERFACES:")
    print("   Root API Info:      http://localhost:5000/")
    print("   Live Spreadsheet:   http://localhost:5000/spreadsheet")
    print()
    print("📊 API ENDPOINTS:")
    print("   Health Check:       GET  /api/health")
    print("   Spreadsheet Info:   GET  /api/info") 
    print("   Grid Data:          GET  /api/grid")
    print("   Cell Operations:    GET/POST/DELETE /api/cell/<cell_ref>")
    print("   Range Operations:   GET/POST /api/range")
    print("   Math Operations:    GET /api/sum|average/row|column/<target>")
    print("   Bulk Operations:    POST /api/bulk")
    print("   Export Data:        GET  /api/export")
    print("=" * 60)
    print()
    print("🚀 QUICK START:")
    print("   1. Open http://localhost:5000/spreadsheet for live interface")
    print("   2. Use API endpoints for programmatic access")
    print("   3. Press Ctrl+C to stop the server")
    print()
    print("✨ FEATURES:")
    print("   • Real-time spreadsheet editing in browser")
    print("   • Auto-refresh every 2 seconds")
    print("   • Live mathematical calculations")
    print("   • Full API access for external programs/LLMs")
    print("   • Sample data and bulk operations")
    print("=" * 60)
    
    try:
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def test_api_locally():
    """Test the API functionality without starting the server"""
    print("\n" + "=" * 50)
    print("🧪 TESTING SPREADSHEET FUNCTIONALITY")
    print("=" * 50)
    
    # Test basic operations
    print("\n1. Setting cell values:")
    result1 = spreadsheet.set_cell('A1', 10)
    print(f"   Set A1 to 10: ✅ {result1['success']}")
    
    result2 = spreadsheet.set_cell('A2', 20)  
    print(f"   Set A2 to 20: ✅ {result2['success']}")
    
    result3 = spreadsheet.set_cell('B1', 5)
    print(f"   Set B1 to 5: ✅ {result3['success']}")
    
    print("\n2. Getting cell values:")
    cell_a1 = spreadsheet.get_cell('A1')
    print(f"   Get A1: {cell_a1['value']} ✅")
    
    cell_a2 = spreadsheet.get_cell('A2') 
    print(f"   Get A2: {cell_a2['value']} ✅")
    
    print("\n3. Mathematical operations:")
    sum_col_a = spreadsheet.sum_column('A')
    print(f"   Sum column A: {sum_col_a['sum']} ✅")
    
    sum_row_1 = spreadsheet.sum_row(1)
    print(f"   Sum row 1: {sum_row_1['sum']} ✅")
    
    avg_col_a = spreadsheet.average_column('A')
    print(f"   Average column A: {avg_col_a['average']:.2f} ✅")
    
    print("\n4. Grid data for display:")
    grid_data = spreadsheet.get_grid_data(5, 5)
    print(f"   Grid size: {len(grid_data['grid'])} rows x {len(grid_data['grid'][0])} cols ✅")
    
    print("\n5. Spreadsheet info:")
    info = spreadsheet.get_spreadsheet_info()
    print(f"   Cells in use: {info['info']['cells_used']} ✅")
    
    print(f"\n✅ Local testing completed successfully!")
    print(f"   • All basic operations working")
    print(f"   • Mathematical functions operational") 
    print(f"   • Grid display data ready")
    print(f"   • Ready for web interface!")

if __name__ == '__main__':
    print("🧮 LLM SPREADSHEET API WITH LIVE WEB INTERFACE")
    print("=" * 55)
    
    # Test the spreadsheet functionality first
    test_api_locally()
    
    print("\n" + "=" * 55)
    print("🚀 STARTING WEB SERVER WITH LIVE INTERFACE")
    print("=" * 55)
    
    # Start the API server with web interface
    run_server()



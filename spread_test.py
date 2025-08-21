import requests
import json

class SpreadsheetAPIClient:
    """Simple client to test the Spreadsheet API"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_info(self):
        """Get spreadsheet information"""
        try:
            response = requests.get(f"{self.base_url}/api/info")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def set_cell(self, cell_ref, value, formula=None):
        """Set a cell value"""
        try:
            data = {"value": value}
            if formula:
                data["formula"] = formula
            
            response = requests.post(
                f"{self.base_url}/api/cell/{cell_ref}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_cell(self, cell_ref):
        """Get a cell value"""
        try:
            response = requests.get(f"{self.base_url}/api/cell/{cell_ref}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def set_range(self, start_cell, end_cell, values):
        """Set a range of cells"""
        try:
            data = {
                "start": start_cell,
                "end": end_cell,
                "values": values
            }
            response = requests.post(
                f"{self.base_url}/api/range",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_range(self, start_cell, end_cell):
        """Get a range of cells"""
        try:
            response = requests.get(
                f"{self.base_url}/api/range",
                params={"start": start_cell, "end": end_cell}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def sum_row(self, row, start_col=None, end_col=None):
        """Sum a row"""
        try:
            params = {}
            if start_col:
                params["start_col"] = start_col
            if end_col:
                params["end_col"] = end_col
            
            response = requests.get(
                f"{self.base_url}/api/sum/row/{row}",
                params=params
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def sum_column(self, column, start_row=None, end_row=None):
        """Sum a column"""
        try:
            params = {}
            if start_row:
                params["start_row"] = start_row
            if end_row:
                params["end_row"] = end_row
            
            response = requests.get(
                f"{self.base_url}/api/sum/column/{column}",
                params=params
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def average_row(self, row, start_col=None, end_col=None):
        """Average a row"""
        try:
            params = {}
            if start_col:
                params["start_col"] = start_col
            if end_col:
                params["end_col"] = end_col
            
            response = requests.get(
                f"{self.base_url}/api/average/row/{row}",
                params=params
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def average_column(self, column, start_row=None, end_row=None):
        """Average a column"""
        try:
            params = {}
            if start_row:
                params["start_row"] = start_row
            if end_row:
                params["end_row"] = end_row
            
            response = requests.get(
                f"{self.base_url}/api/average/column/{column}",
                params=params
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def export_spreadsheet(self):
        """Export the entire spreadsheet"""
        try:
            response = requests.get(f"{self.base_url}/api/export")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def bulk_operations(self, operations):
        """Perform bulk operations"""
        try:
            data = {"operations": operations}
            response = requests.post(
                f"{self.base_url}/api/bulk",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def demo_api():
    """Demonstrate the API functionality"""
    print("Spreadsheet API Demo")
    print("=" * 30)
    
    # Create client
    client = SpreadsheetAPIClient()
    
    # Test health check
    print("1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    if "error" in health:
        print("❌ API server is not running. Please start the server first.")
        return
    
    # Test setting cells
    print("\n2. Setting Cell Values:")
    print("Setting A1 = 100")
    result = client.set_cell('A1', 100)
    print(json.dumps(result, indent=2))
    
    print("Setting A2 = 200")
    result = client.set_cell('A2', 200)
    print(json.dumps(result, indent=2))
    
    print("Setting A3 = 300")
    result = client.set_cell('A3', 300)
    print(json.dumps(result, indent=2))
    
    print("Setting B1 = 50")
    result = client.set_cell('B1', 50)
    print(json.dumps(result, indent=2))
    
    # Test getting cells
    print("\n3. Getting Cell Values:")
    result = client.get_cell('A1')
    print(f"A1 = {json.dumps(result, indent=2)}")
    
    # Test range operations
    print("\n4. Setting Range A4:B5:")
    result = client.set_range('A4', 'B5', [[10, 20], [30, 40]])
    print(json.dumps(result, indent=2))
    
    print("\n5. Getting Range A1:B5:")
    result = client.get_range('A1', 'B5')
    print(json.dumps(result, indent=2))
    
    # Test mathematical operations
    print("\n6. Mathematical Operations:")
    
    print("Sum of column A:")
    result = client.sum_column('A')
    print(json.dumps(result, indent=2))
    
    print("Sum of row 1:")
    result = client.sum_row(1)
    print(json.dumps(result, indent=2))
    
    print("Average of column A:")
    result = client.average_column('A')
    print(json.dumps(result, indent=2))
    
    # Test bulk operations
    print("\n7. Bulk Operations:")
    operations = [
        {"type": "set_cell", "cell": "C1", "value": 25},
        {"type": "set_cell", "cell": "C2", "value": 75},
        {"type": "sum_column", "column": "C"}
    ]
    result = client.bulk_operations(operations)
    print(json.dumps(result, indent=2))
    
    # Test export
    print("\n8. Export Spreadsheet:")
    result = client.export_spreadsheet()
    print("Exported data (showing first few cells):")
    if 'cells' in result:
        for cell_ref, cell_data in list(result['cells'].items())[:5]:
            print(f"  {cell_ref}: {cell_data['value']}")
    
    print("\n✅ Demo completed successfully!")
    print("\nYou can now use this API from any LLM program by making HTTP requests")
    print("to the endpoints shown above.")

def interactive_mode():
    """Interactive mode for testing the API"""
    client = SpreadsheetAPIClient()
    
    print("\nInteractive Spreadsheet API Testing")
    print("=" * 35)
    print("Commands:")
    print("  set <cell> <value>     - Set cell value (e.g., 'set A1 100')")
    print("  get <cell>             - Get cell value (e.g., 'get A1')")
    print("  sum_col <column>       - Sum column (e.g., 'sum_col A')")
    print("  sum_row <row>          - Sum row (e.g., 'sum_row 1')")
    print("  avg_col <column>       - Average column (e.g., 'avg_col A')")
    print("  avg_row <row>          - Average row (e.g., 'avg_row 1')")
    print("  info                   - Get spreadsheet info")
    print("  export                 - Export spreadsheet")
    print("  demo                   - Run full demo")
    print("  quit                   - Exit")
    print()
    
    while True:
        try:
            command = input("Enter command: ").strip().split()
            if not command:
                continue
                
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'set' and len(command) == 3:
                cell, value = command[1], command[2]
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    pass  # Keep as string
                result = client.set_cell(cell, value)
                print(json.dumps(result, indent=2))
            elif cmd == 'get' and len(command) == 2:
                result = client.get_cell(command[1])
                print(json.dumps(result, indent=2))
            elif cmd == 'sum_col' and len(command) == 2:
                result = client.sum_column(command[1])
                print(json.dumps(result, indent=2))
            elif cmd == 'sum_row' and len(command) == 2:
                result = client.sum_row(int(command[1]))
                print(json.dumps(result, indent=2))
            elif cmd == 'avg_col' and len(command) == 2:
                result = client.average_column(command[1])
                print(json.dumps(result, indent=2))
            elif cmd == 'avg_row' and len(command) == 2:
                result = client.average_row(int(command[1]))
                print(json.dumps(result, indent=2))
            elif cmd == 'info':
                result = client.get_info()
                print(json.dumps(result, indent=2))
            elif cmd == 'export':
                result = client.export_spreadsheet()
                print(json.dumps(result, indent=2))
            elif cmd == 'demo':
                demo_api()
            else:
                print("Invalid command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")

if __name__ == '__main__':
    print("Spreadsheet API Test Client")
    print("=" * 30)
    print("Make sure the API server is running on http://localhost:5000")
    print()
    
    choice = input("Choose mode:\n1. Run demo\n2. Interactive mode\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        demo_api()
    elif choice == '2':
        interactive_mode()
    else:
        print("Running demo by default...")
        demo_api()


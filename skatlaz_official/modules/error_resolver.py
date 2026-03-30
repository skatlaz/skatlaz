"""
Error Resolver Module - StackOverflow-style error resolution
"""

import requests
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import html
import sys
import os

class ErrorResolver:
    """Error resolution with StackOverflow and Google integration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def resolve_error(self, error_message: str, context: str = "") -> str:
        """Resolve error using multiple sources"""
        # Extract error details
        error_info = self._parse_error(error_message)
        
        # Search StackOverflow
        so_results = self._search_stackoverflow(error_info['error'])
        
        # Search Google (simulated)
        google_results = self._search_google(error_info['error'])
        
        # Get AI analysis (simulated)
        ai_analysis = self._get_ai_analysis(error_info, context)
        
        return self._format_resolution(error_info, so_results, google_results, ai_analysis)
    
    def _parse_error(self, error_message: str) -> Dict:
        """Parse error message to extract details"""
        error_info = {
            'full_error': error_message,
            'error_type': '',
            'error': '',
            'line': '',
            'file': '',
            'traceback': []
        }
        
        # Extract error type
        type_match = re.search(r'([A-Za-z]+Error):', error_message)
        if type_match:
            error_info['error_type'] = type_match.group(1)
        
        # Extract line number
        line_match = re.search(r'line (\d+)', error_message)
        if line_match:
            error_info['line'] = line_match.group(1)
        
        # Extract file name
        file_match = re.search(r'File "([^"]+)"', error_message)
        if file_match:
            error_info['file'] = file_match.group(1)
        
        # Extract main error message
        lines = error_message.split('\n')
        if lines:
            error_info['error'] = lines[-1].strip()
        
        return error_info
    
    def _search_stackoverflow(self, error: str) -> List[Dict]:
        """Search StackOverflow for similar errors"""
        try:
            # Use StackExchange API
            url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': error[:100],
                'site': 'stackoverflow',
                'pagesize': 5
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': html.unescape(item.get('title', '')),
                        'link': item.get('link', ''),
                        'score': item.get('score', 0),
                        'answer_count': item.get('answer_count', 0)
                    })
                
                return results
            
        except Exception as e:
            pass
        
        return []
    
    def _search_google(self, error: str) -> List[Dict]:
        """Search Google for error solutions (simulated)"""
        # Simulated Google search results
        return [
            {
                'title': f"How to fix {error[:50]}",
                'snippet': f"Common solutions for {error[:50]} include checking syntax, ensuring proper imports, and validating data types.",
                'url': "https://stackoverflow.com/questions/search"
            },
            {
                'title': f"Understanding {error[:50]} in Python",
                'snippet': "This error typically occurs when... Here's how to debug it step by step.",
                'url': "https://realpython.com/python-errors"
            }
        ]
    
    def _get_ai_analysis(self, error_info: Dict, context: str) -> str:
        """Get AI-powered error analysis (simulated)"""
        error_type = error_info.get('error_type', 'Unknown Error')
        error_msg = error_info.get('error', '')
        line = error_info.get('line', 'unknown')
        file = error_info.get('file', 'unknown')
        
        analysis = f"**Root Cause Analysis:**\n"
        analysis += f"The error '{error_type}' typically occurs when {self._get_common_cause(error_type)}.\n\n"
        
        analysis += "**Step-by-Step Solution:**\n"
        analysis += f"1. Check line {line} in file {file} for syntax or logic issues\n"
        analysis += "2. Verify that all variables are properly defined before use\n"
        analysis += "3. Ensure you're using the correct data types\n"
        analysis += "4. Add proper error handling with try-except blocks\n\n"
        
        analysis += "**Example Fix:**\n"
        analysis += f"```python\n"
        analysis += f"try:\n"
        analysis += f"    # Your code that caused the error\n"
        analysis += f"    # Add your code here\n"
        analysis += f"except {error_type} as e:\n"
        analysis += f"    print(f\"Error occurred: {{e}}\")\n"
        analysis += f"    # Handle the error appropriately\n"
        analysis += f"```\n\n"
        
        analysis += "**Prevention Tips:**\n"
        analysis += "- Always validate inputs before processing\n"
        analysis += "- Use type hints to catch type errors early\n"
        analysis += "- Write unit tests to catch edge cases\n"
        analysis += "- Add logging for better debugging\n"
        
        return analysis
    
    def _get_common_cause(self, error_type: str) -> str:
        """Get common cause for error type"""
        causes = {
            'AttributeError': "an object doesn't have the attribute you're trying to access",
            'ImportError': "a module or package cannot be imported",
            'KeyError': "a dictionary key doesn't exist",
            'ValueError': "a function receives an argument of correct type but inappropriate value",
            'TypeError': "an operation is performed on an object of inappropriate type",
            'IndexError': "a sequence index is out of range",
            'NameError': "a variable or function name is not defined",
            'SyntaxError': "there's invalid syntax in the code",
            'IndentationError': "indentation is inconsistent",
            'FileNotFoundError': "the specified file doesn't exist",
            'ZeroDivisionError': "division by zero occurs",
            'RuntimeError': "an error that doesn't fit into other categories occurs"
        }
        return causes.get(error_type, "there's an issue in your code")
    
    def _format_resolution(self, error_info: Dict, so_results: List, google_results: List, ai_analysis: str) -> str:
        """Format the complete error resolution"""
        result = "🐛 **Error Resolution Report**\n"
        result += "=" * 50 + "\n\n"
        
        result += "**Error Details:**\n"
        result += f"- Type: {error_info.get('error_type', 'Unknown')}\n"
        result += f"- Message: {error_info.get('error', 'N/A')}\n"
        result += f"- File: {error_info.get('file', 'N/A')}\n"
        result += f"- Line: {error_info.get('line', 'N/A')}\n\n"
        
        result += "🔍 **StackOverflow Solutions:**\n"
        
        if so_results:
            for i, result_item in enumerate(so_results[:3], 1):
                result += f"\n{i}. **{result_item['title']}**\n"
                result += f"   Score: {result_item['score']} | Answers: {result_item['answer_count']}\n"
                result += f"   Link: {result_item['link']}\n"
        else:
            result += "\nNo StackOverflow results found. Try searching manually.\n"
        
        result += "\n🤖 **AI-Powered Analysis:**\n"
        result += ai_analysis + "\n"
        
        result += "📚 **Related Resources:**\n"
        result += "- Python Documentation: https://docs.python.org/3/\n"
        result += f"- StackOverflow: https://stackoverflow.com/search?q={error_info.get('error_type', 'error').replace('Error', '')}\n"
        result += "- Python Error Reference: https://docs.python.org/3/library/exceptions.html\n\n"
        
        result += "💡 **Pro Tip:** Always use try-except blocks for error-prone operations and log errors for debugging!\n"
        
        return result
    
    def analyze_error_code(self, code: str, error: str) -> str:
        """Analyze code with specific error"""
        result = "🔧 **Code Error Analysis**\n\n"
        result += "**Code:**\n"
        result += f"```python\n{code[:500]}\n```\n\n"
        result += "**Error:**\n"
        result += f"{error}\n\n"
        
        # Try to suggest fixes based on error type
        if "NameError" in error:
            result += "**Suggested Fix:**\n"
            result += "This NameError means a variable or function is not defined. Check:\n"
            result += "1. Is the variable spelled correctly?\n"
            result += "2. Was the variable defined before use?\n"
            result += "3. Is it in the correct scope?\n"
        elif "TypeError" in error:
            result += "**Suggested Fix:**\n"
            result += "This TypeError indicates a type mismatch. Check:\n"
            result += "1. Are you using the correct data types?\n"
            result += "2. Did you convert types when needed?\n"
            result += "3. Check function signatures for expected types\n"
        elif "IndexError" in error:
            result += "**Suggested Fix:**\n"
            result += "This IndexError means you're accessing an index that doesn't exist. Check:\n"
            result += "1. Is the index within range?\n"
            result += "2. Use len() to check list/string length\n"
            result += "3. Add boundary checks before accessing\n"
        
        return result
    
    def quick_fix(self, error: str) -> str:
        """Provide quick fix suggestions for common errors"""
        error_lower = error.lower()
        
        fixes = {
            "indentation": "Fix indentation: Use consistent spaces (4 spaces recommended). Check that all blocks are properly aligned.",
            "syntax": "Check for missing colons, parentheses, or quotes. Verify that all brackets are properly closed.",
            "import": "Install missing package with pip install [package_name]. Check that the module name is correct.",
            "attribute": "Check if the object actually has this attribute. Use dir() to list available attributes.",
            "key": "Check if the key exists in dictionary. Use dict.get() to safely access keys.",
            "value": "Validate input values before passing to functions. Use try-except to handle invalid values.",
            "name": "Define the variable before using it. Check spelling and scope.",
            "file": "Check if file exists and path is correct. Use os.path.exists() to verify."
        }
        
        for key, fix in fixes.items():
            if key in error_lower:
                result = f"🔧 **Quick Fix for {key.title()} Error**\n\n"
                result += fix + "\n\n"
                result += "**Example:**\n"
                result += self._get_example_fix(key)
                return result
        
        return "No quick fix available. Try searching online or provide more details about the error."
    
    def _get_example_fix(self, error_type: str) -> str:
        """Get example fix for common errors"""
        examples = {
            "indentation": "```python\n# Wrong:\ndef func():\nprint(\"hello\")\n\n# Correct:\ndef func():\n    print(\"hello\")\n```",
            "syntax": "```python\n# Wrong:\nif x > 5\n    print(x)\n\n# Correct:\nif x > 5:\n    print(x)\n```",
            "import": "```bash\npip install requests\n```",
            "attribute": "```python\n# Check available attributes\nprint(dir(object))\n```",
            "key": "```python\n# Safe dictionary access\nvalue = my_dict.get('key', default_value)\n```"
        }
        return examples.get(error_type, "Check documentation for proper usage.")

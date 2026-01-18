"""
Elite+ Compression Module

Wrapper for SIRCL (Semantic Identifier & Repetition Compaction Layer) encoder.
Uses Node.js subprocess to call the JavaScript implementation.
"""

import subprocess
import json
import os
from pathlib import Path


class ElitePlusEncoder:
    """Wrapper for Elite+ SIRCL encoder."""
    
    def __init__(self):
        # Get the path to the wrapper script
        self.base_dir = Path(__file__).parent.parent
        self.js_dir = self.base_dir / 'static' / 'js'
        self.wrapper_script = self.js_dir / 'elite_plus_wrapper.js'
        self.sircl_script = self.js_dir / 'sircl.js'
        
        # Check if Node.js is available
        try:
            result = subprocess.run(['node', '--version'], 
                                   capture_output=True, 
                                   timeout=5)
            self.node_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.node_available = False
    
    def is_available(self):
        """Check if Elite+ compression is available (Node.js installed)."""
        return self.node_available and self.wrapper_script.exists() and self.sircl_script.exists()
    
    def compress(self, code, config=None):
        """
        Compress code using Elite+ SIRCL encoder.
        
        Args:
            code: C code string to compress
            config: Optional configuration dict for SIRCL encoder
        
        Returns:
            dict with 'code' (compressed code) and 'metadata' (encoding metadata)
            or None if compression failed or unavailable
        """
        if not self.is_available():
            return None
        
        if config is None:
            config = {}
        
        try:
            # Prepare input data
            input_data = {
                'code': code,
                'config': config,
                'filePath': ''
            }
            
            # Call Node.js wrapper (run from js directory so imports work)
            process = subprocess.Popen(
                ['node', 'elite_plus_wrapper.js'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.js_dir)
            )
            
            stdout, stderr = process.communicate(input=json.dumps(input_data), timeout=30)
            
            if process.returncode != 0:
                print(f"Elite+ compression error: {stderr}")
                return None
            
            result = json.loads(stdout)
            
            if not result.get('success', False):
                print(f"Elite+ compression failed: {result.get('error', 'Unknown error')}")
                return None
            
            return {
                'code': result.get('code', ''),
                'metadata': result.get('metadata', {})
            }
            
        except subprocess.TimeoutExpired:
            print("Elite+ compression timed out")
            return None
        except json.JSONDecodeError as e:
            print(f"Elite+ compression JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"Elite+ compression error: {e}")
            return None


# Global instance
_elite_plus_encoder = None

def get_elite_plus_encoder():
    """Get or create global Elite+ encoder instance."""
    global _elite_plus_encoder
    if _elite_plus_encoder is None:
        _elite_plus_encoder = ElitePlusEncoder()
    return _elite_plus_encoder

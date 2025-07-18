#!/usr/bin/env python3
"""
Build and Distribution Script for Agent Memory OS

This script builds the package and prepares it for PyPI distribution.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class PackageBuilder:
    """Build and distribute the Agent Memory OS package"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.egg_info_dir = self.project_root / "agent_memory_os.egg-info"
        
    def clean_build_dirs(self):
        """Clean build directories"""
        print("🧹 Cleaning build directories...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir, self.egg_info_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✅ Cleaned {dir_path}")
    
    def run_tests(self):
        """Run the comprehensive test suite"""
        print("\n🧪 Running comprehensive test suite...")
        
        result = subprocess.run([
            sys.executable, "run_tests.py"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        if result.returncode != 0:
            print("❌ Tests failed! Cannot proceed with build.")
            print("Test output:")
            print(result.stdout)
            print("Test errors:")
            print(result.stderr)
            return False
        
        print("✅ All tests passed!")
        return True
    
    def check_setup(self):
        """Check setup.py configuration"""
        print("\n📋 Checking setup.py configuration...")
        
        try:
            # Check if setup.py exists and is valid by running check command
            result = subprocess.run([
                sys.executable, "setup.py", "check"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print(f"❌ setup.py has issues:")
                print(result.stderr)
                return False
            
            print("✅ setup.py is valid")
            return True
        except Exception as e:
            print(f"❌ setup.py check failed: {e}")
            return False
    
    def build_package(self):
        """Build the package"""
        print("\n🔨 Building package...")
        
        # Clean first
        self.clean_build_dirs()
        
        # Build
        result = subprocess.run([
            sys.executable, "setup.py", "sdist", "bdist_wheel"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        if result.returncode != 0:
            print("❌ Build failed!")
            print("Build output:")
            print(result.stdout)
            print("Build errors:")
            print(result.stderr)
            return False
        
        print("✅ Package built successfully!")
        
        # List built files
        if self.dist_dir.exists():
            print("\n📦 Built files:")
            for file_path in self.dist_dir.iterdir():
                print(f"  📄 {file_path.name}")
        
        return True
    
    def check_package(self):
        """Check the built package"""
        print("\n🔍 Checking built package...")
        
        if not self.dist_dir.exists():
            print("❌ No dist directory found!")
            return False
        
        # Check for wheel and source distribution
        files = list(self.dist_dir.iterdir())
        wheel_files = [f for f in files if f.suffix == '.whl']
        source_files = [f for f in files if f.name.endswith('.tar.gz')]
        
        if not wheel_files:
            print("❌ No wheel file found!")
            return False
        
        if not source_files:
            print("❌ No source distribution found!")
            return False
        
        print(f"✅ Found {len(wheel_files)} wheel file(s) and {len(source_files)} source distribution(s)")
        return True
    
    def test_install(self):
        """Test installing the built package"""
        print("\n📥 Testing package installation...")
        
        # Find the wheel file
        wheel_files = list(self.dist_dir.glob("*.whl"))
        if not wheel_files:
            print("❌ No wheel file found for testing!")
            return False
        
        wheel_file = wheel_files[0]
        
        # Create a temporary virtual environment for testing
        import tempfile
        import venv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_venv = Path(temp_dir) / "test_venv"
            venv.create(temp_venv, with_pip=True)
            
            # Get pip and python paths
            if os.name == 'nt':  # Windows
                pip_path = temp_venv / "Scripts" / "pip"
                python_path = temp_venv / "Scripts" / "python"
            else:  # Unix/Linux/macOS
                pip_path = temp_venv / "bin" / "pip"
                python_path = temp_venv / "bin" / "python"
            
            # Install the package
            result = subprocess.run([
                str(pip_path), "install", str(wheel_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Package installation failed!")
                print("Installation errors:")
                print(result.stderr)
                return False
            
            # Test import
            result = subprocess.run([
                str(python_path), "-c", "import agent_memory_sdk; print('✅ Import successful')"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Package import failed!")
                print("Import errors:")
                print(result.stderr)
                return False
            
            print("✅ Package installation and import test passed!")
            return True
    
    def validate_metadata(self):
        """Validate package metadata"""
        print("\n📊 Validating package metadata...")
        
        try:
            # Read setup.py to check for required fields
            setup_content = (self.project_root / "setup.py").read_text()
            
            # Basic checks for required fields
            required_fields = ['name=', 'version=', 'description=', 'author=']
            for field in required_fields:
                if field not in setup_content:
                    print(f"❌ Missing {field} in setup.py")
                    return False
            
            print("✅ Package metadata is valid")
            return True
            
        except Exception as e:
            print(f"❌ Metadata validation failed: {e}")
            return False
    
    def prepare_for_upload(self):
        """Prepare package for PyPI upload"""
        print("\n🚀 Preparing for PyPI upload...")
        
        # Check if we have the necessary files
        if not self.check_package():
            return False
        
        # Validate metadata
        if not self.validate_metadata():
            return False
        
        print("✅ Package is ready for PyPI upload!")
        print("\n📋 Next steps:")
        print("1. Test upload to TestPyPI:")
        print("   python -m twine upload --repository testpypi dist/*")
        print("2. Upload to PyPI:")
        print("   python -m twine upload dist/*")
        print("3. Verify installation:")
        print("   pip install agent-memory-os")
        
        return True
    
    def build_all(self):
        """Run the complete build process"""
        print("🔨 AGENT MEMORY OS - PACKAGE BUILD PROCESS")
        print("=" * 60)
        
        steps = [
            ("Running Tests", self.run_tests),
            ("Checking Setup", self.check_setup),
            ("Building Package", self.build_package),
            ("Checking Package", self.check_package),
            ("Testing Installation", self.test_install),
            ("Preparing for Upload", self.prepare_for_upload),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                print(f"\n❌ Build process failed at: {step_name}")
                return False
        
        print(f"\n{'='*20} BUILD COMPLETE {'='*20}")
        print("🎉 Package is ready for PyPI distribution!")
        return True


def main():
    """Main entry point"""
    builder = PackageBuilder()
    
    try:
        success = builder.build_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during build: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
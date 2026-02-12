import subprocess
import os
import re
from ollama import chat
from datetime import datetime


class TestAgent:
    """AI-powered test agent that analyzes code and generates tests automatically"""

    __test__ = False  # Prevent pytest from trying to test this class

    def __init__(self, model="llama3.2"):
        self.model = model
        self.report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files_analyzed": [],
            "functions_found": [],
            "tests_found": [],
            "missing_tests": [],
            "test_results": "",
            "coverage": "",
            "generated_tests": [],
            "fixed_tests": [],
            "recommendations": [],
        }

    def run_tests(self, path="."):
        """Run pytest tests"""
        try:
            result = subprocess.run(
                ["pytest", path, "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = (
                f"Return code: {result.returncode}\n\n{result.stdout}\n{result.stderr}"
            )
            self.report_data["test_results"] = output
            return output
        except Exception as e:
            error = f"Error: {str(e)}"
            self.report_data["test_results"] = error
            return error

    def analyze_coverage(self, path="."):
        """Analyze test coverage"""
        try:
            result = subprocess.run(
                [
                    "pytest",
                    path,
                    "--cov=.",
                    "--cov-report=term-missing",
                    "--ignore=test_agent.py",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.report_data["coverage"] = result.stdout
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    def list_files(self, directory="."):
        """List Python files"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [
                d
                for d in dirs
                if d not in ["venv", ".venv", "__pycache__", ".pytest_cache", ".git"]
            ]
            for filename in filenames:
                if filename.endswith(".py") and filename != "test_agent.py":
                    rel_path = os.path.relpath(os.path.join(root, filename), directory)
                    files.append(rel_path)
        self.report_data["files_analyzed"] = files
        return files

    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def extract_functions(self, filepath):
        """Extract functions from file"""
        content = self.read_file(filepath)
        functions = []

        for line in content.split("\n"):
            if line.strip().startswith("def ") and not line.strip().startswith(
                "def __"
            ):
                func_name = line.strip().split("(")[0].replace("def ", "")
                functions.append(func_name)

        return functions

    def generate_test_for_function(self, function_name, function_code, existing_tests):
        """Generate test for a single function"""
        print(f"   🔨 Generating test for: {function_name}")

        prompt = f"""Create a pytest test for this Python function.

FUNCTION:
{function_code}

EXISTING TESTS (don't repeat these):
{existing_tests}

CRITICAL REQUIREMENTS:
1. Test function name: test_{function_name}
2. NEVER add import statements - they're already in the file!
3. Use function directly by name: {function_name}(...)
4. Test normal cases
5. Test edge cases (e.g., zero, negative numbers)
6. Test error conditions ONLY if function raises exceptions
7. IMPORTANT: Calculate mathematical results CORRECTLY (e.g., (-1)^2 = 1, NOT -1)
8. DO NOT add explanations or comments

EXAMPLE OF CORRECT TEST:
def test_power():
    assert power(2, 3) == 8
    assert power(-1, 2) == 1
    with pytest.raises(ValueError):
        power(10, "text")

Provide ONLY test code without ```python``` tags or explanations."""

        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 500},
        )

        test_code = response["message"]["content"].strip()
        test_code = test_code.replace("```python", "").replace("```", "").strip()

        return test_code

    def identify_missing_tests(self):
        """Identify missing tests"""
        print("\n🔍 Identifying missing tests...")

        code_files = [f for f in self.list_files() if not f.startswith("test_")]
        test_files = [f for f in self.list_files() if f.startswith("test_")]

        missing_tests = []

        for code_file in code_files:
            print(f"\n   📄 Analyzing: {code_file}")
            functions = self.extract_functions(code_file)
            self.report_data["functions_found"].extend(functions)

            existing_tests = ""
            for test_file in test_files:
                existing_tests += self.read_file(test_file)

            test_functions = []
            for test_file in test_files:
                test_functions.extend(self.extract_functions(test_file))

            self.report_data["tests_found"] = test_functions

            for func in functions:
                test_name = f"test_{func}"
                if test_name not in existing_tests:
                    print(f"      ⚠️  Missing: {func}")
                    missing_tests.append({"function": func, "file": code_file})
                    self.report_data["missing_tests"].append(func)
                else:
                    print(f"      ✅ Tested: {func}")

        return missing_tests

    def generate_missing_tests(self, missing_tests):
        """Generate all missing tests"""
        if not missing_tests:
            print("\n✅ All functions are tested!")
            return []

        print(f"\n🤖 Generating {len(missing_tests)} missing tests...\n")

        generated = []

        for item in missing_tests:
            func_name = item["function"]
            code_file = item["file"]

            full_code = self.read_file(code_file)

            function_code = ""
            capture = False
            indent_level = 0

            for line in full_code.split("\n"):
                if f"def {func_name}(" in line:
                    capture = True
                    indent_level = len(line) - len(line.lstrip())
                    function_code = line + "\n"
                elif capture:
                    current_indent = len(line) - len(line.lstrip())
                    if (
                        line.strip()
                        and current_indent <= indent_level
                        and not line.strip().startswith("#")
                    ):
                        break
                    function_code += line + "\n"

            existing_tests = ""
            test_file = f"test_{code_file}"
            if os.path.exists(test_file):
                existing_tests = self.read_file(test_file)

            test_code = self.generate_test_for_function(
                func_name, function_code, existing_tests
            )

            generated.append({"function": func_name, "test_code": test_code})
            self.report_data["generated_tests"].append(
                {"function": func_name, "code": test_code}
            )

        return generated

    def write_tests_to_file(self, generated_tests, test_file="test_calculator.py"):
        """Write generated tests to file"""
        if not generated_tests:
            return

        print(f"\n📝 Writing tests to file: {test_file}\n")

        existing_content = ""
        required_functions = set()

        if os.path.exists(test_file):
            with open(test_file, "r", encoding="utf-8") as f:
                existing_content = f.read()

        for item in generated_tests:
            required_functions.add(item["function"])
            test_code = item["test_code"]
            func_calls = re.findall(r"\b(\w+)\s*\(", test_code)
            for func in func_calls:
                if func not in [
                    "assert",
                    "pytest",
                    "raises",
                    "print",
                ] and not func.startswith("test_"):
                    required_functions.add(func)

        missing_imports = []
        import_line_start = "from calculator import"

        if import_line_start in existing_content:
            import_match = re.search(r"from calculator import (.+)", existing_content)
            if import_match:
                current_imports = set(
                    imp.strip() for imp in import_match.group(1).split(",")
                )
                missing_imports = [
                    func for func in required_functions if func not in current_imports
                ]
        else:
            missing_imports = list(required_functions)

        if missing_imports:
            print(f"   📦 Adding missing imports: {', '.join(missing_imports)}")

            if import_line_start in existing_content:
                # Update existing import line
                import_match = re.search(
                    r"from calculator import (.+)", existing_content
                )
                if import_match:
                    current_imports = import_match.group(1).strip()
                    if "\n" in current_imports:
                        current_imports = current_imports.split("\n")[0]
                    new_imports = current_imports + ", " + ", ".join(missing_imports)
                    existing_content = existing_content.replace(
                        f"from calculator import {current_imports}",
                        f"from calculator import {new_imports}",
                    )

                    with open(test_file, "w", encoding="utf-8") as f:
                        f.write(existing_content)
            else:
                # No imports exist - create them at the beginning
                import_header = "import pytest\n"
                import_header += (
                    f"from calculator import {', '.join(sorted(missing_imports))}\n"
                )

                if existing_content.strip():
                    # Prepend to existing content
                    existing_content = import_header + "\n" + existing_content
                else:
                    # File is empty or only has whitespace
                    existing_content = import_header

                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(existing_content)

        with open(test_file, "a", encoding="utf-8") as f:
            f.write("\n\n# ========================================\n")
            f.write("# AUTO-GENERATED TESTS\n")
            f.write(f'# Generated: {self.report_data["timestamp"]}\n')
            f.write("# ========================================\n\n")

            for item in generated_tests:
                f.write(f'# Test for function: {item["function"]}\n')
                f.write(item["test_code"])
                f.write("\n\n")

        print(f"   ✅ {len(generated_tests)} tests added!")
        if missing_imports:
            print(f"   ✅ {len(missing_imports)} imports added!")

    def validate_and_fix_tests(self, max_attempts=3):
        """Validate tests and fix errors automatically"""
        print("\n🔧 Validating and fixing tests...\n")

        attempt = 1
        while attempt <= max_attempts:
            print(f"   Attempt {attempt}/{max_attempts}")
            result = self.run_tests()

            if "FAILED" not in result and result.startswith("Return code: 0"):
                print("   ✅ All tests passed!\n")
                return True

            if "FAILED" in result:
                print(f"   ⚠️  Found errors, attempting to fix...\n")

                prompt = f"""Tests failed. Analyze the error and fix it.

TEST RESULTS:
{result}

READ test_calculator.py AND FIX THE LATEST TESTS.

Provide only the corrected test code that replaces the failing tests.
DO NOT provide explanations, only code."""

                response = chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.1, "num_predict": 1000},
                )

                fixed_code = response["message"]["content"].strip()
                fixed_code = (
                    fixed_code.replace("```python", "").replace("```", "").strip()
                )

                self.report_data["fixed_tests"].append(
                    {"attempt": attempt, "error": result, "fix": fixed_code}
                )

                print(f"   🔨 Fixed code attempt {attempt}:")
                print(f"   {fixed_code[:100]}...\n")

                attempt += 1
            else:
                break

        if attempt > max_attempts:
            print("   ❌ Test fixing failed after maximum attempts\n")
            return False

        return True

    def generate_recommendations(self, analysis):
        """Generate recommendations using AI"""
        print("\n💡 Generating recommendations...\n")

        prompt = f"""Based on this analysis, provide 5 concrete recommendations to improve the project's tests.

{analysis}

Provide recommendations briefly and clearly in the format:
1. [Recommendation]
2. [Recommendation]
...

FOCUS ON:
- Test quality
- Missing tests
- Improving test coverage
- Best practices"""

        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.5, "num_predict": 500},
        )

        recommendations = response["message"]["content"].strip()
        self.report_data["recommendations"] = recommendations
        return recommendations

    def generate_markdown_report(self):
        """Create markdown report"""
        print("\n📄 Creating markdown report...\n")

        coverage_percent = "N/A"
        if "TOTAL" in self.report_data["coverage"]:
            lines = self.report_data["coverage"].split("\n")
            for line in lines:
                if "calculator.py" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage_percent = parts[3]

        report = f"""# 🤖 Test Agent Report

**Created:** {self.report_data['timestamp']}  
**Model:** {self.model}  
**Test Coverage:** {coverage_percent}

---

## 📊 Summary

- **Files analyzed:** {len(self.report_data['files_analyzed'])}
- **Functions found:** {len(self.report_data['functions_found'])}
- **Existing tests:** {len(self.report_data['tests_found'])}
- **Missing tests:** {len(self.report_data['missing_tests'])}
- **Generated tests:** {len(self.report_data['generated_tests'])}
- **Fixed tests:** {len(self.report_data['fixed_tests'])}

---

## 📁 Analyzed Files

"""

        for f in self.report_data["files_analyzed"]:
            report += f"- `{f}`\n"

        report += "\n---\n\n## 🔍 Found Functions\n\n"

        for func in self.report_data["functions_found"]:
            status = (
                "✅ Tested"
                if f"test_{func}" in str(self.report_data["tests_found"])
                else "❌ Not tested"
            )
            report += f"- **{func}()** - {status}\n"

        if self.report_data["missing_tests"]:
            report += "\n---\n\n## ⚠️ Missing Tests\n\n"
            report += "The following functions needed tests:\n\n"
            for func in self.report_data["missing_tests"]:
                report += f"- `{func}()`\n"

        if self.report_data["generated_tests"]:
            report += "\n---\n\n## ✨ Generated Tests\n\n"
            for item in self.report_data["generated_tests"]:
                report += f"### Test for function: `{item['function']}()`\n\n"
                report += "```python\n"
                report += item["code"]
                report += "\n```\n\n"

        if self.report_data["fixed_tests"]:
            report += "\n---\n\n## 🔧 Fixed Tests\n\n"
            report += f"Agent made {len(self.report_data['fixed_tests'])} fix attempts for failing tests.\n\n"

        report += "\n---\n\n## 🧪 Test Results\n\n```\n"
        report += self.report_data["test_results"]
        report += "\n```\n"

        report += "\n---\n\n## 📈 Test Coverage\n\n```\n"
        report += self.report_data["coverage"]
        report += "\n```\n"

        if self.report_data["recommendations"]:
            report += "\n---\n\n## 💡 Recommendations\n\n"
            report += self.report_data["recommendations"]

        report += "\n\n---\n\n"
        report += "*Report generated automatically by AI Test Agent*\n"
        report += f"*Powered by Ollama ({self.model})*\n"

        filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"   ✅ Report saved: {filename}\n")
        return filename

    def analyze_project(self):
        """Main method - complete analysis"""
        print("\n" + "=" * 60)
        print("🚀 STARTING PROJECT ANALYSIS")
        print("=" * 60)

        print("\n📁 Step 1: Listing files...")
        files = self.list_files()
        print(f"   Found {len(files)} Python files")

        missing_tests = self.identify_missing_tests()

        print("\n▶️  Step 2: Running existing tests...")
        test_results = self.run_tests()

        print("\n📊 Step 3: Analyzing test coverage...")
        coverage = self.analyze_coverage()

        if missing_tests:
            generated = self.generate_missing_tests(missing_tests)

            if generated:
                self.write_tests_to_file(generated)
                self.validate_and_fix_tests()

                print("\n▶️  Step 4: Re-running tests after fixes...")
                self.run_tests()
                self.analyze_coverage()

        print("\n🧠 Step 5: AI analyzing project...")

        context = f"""PROJECT ANALYSIS:

Files: {', '.join(files)}
Functions: {', '.join(self.report_data['functions_found'])}
Tests: {', '.join(self.report_data['tests_found'])}
Missing tests: {', '.join(self.report_data['missing_tests'])}

Test results:
{test_results}

Coverage:
{coverage}

Provide a brief, concise analysis of the project's test situation (max 200 words)."""

        analysis = chat(
            model=self.model,
            messages=[{"role": "user", "content": context}],
            options={"temperature": 0.3, "num_predict": 500},
        )["message"]["content"]

        recommendations = self.generate_recommendations(analysis)
        report_file = self.generate_markdown_report()

        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"\n📄 Report: {report_file}")
        print(f"🧪 Generated tests: test_calculator.py")
        print("\n")

        return {
            "analysis": analysis,
            "recommendations": recommendations,
            "report_file": report_file,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TEST AGENT - AI-Powered Test Generator")
    print("=" * 60)
    print(f"Using: Ollama (llama3.2)")
    print("=" * 60)

    agent = TestAgent()
    result = agent.analyze_project()

    print("💬 Brief Analysis:")
    print("-" * 60)
    print(result["analysis"])
    print("\n💡 Recommendations:")
    print("-" * 60)
    print(result["recommendations"])

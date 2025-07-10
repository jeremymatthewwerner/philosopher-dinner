#!/usr/bin/env python3
"""
GitHub Issue Manager for Automated Bug Tracking
Automatically files issues when bugs are found and resolves them when fixed.
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class GitHubIssueManager:
    """Manages GitHub issues for automated bug tracking and resolution"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.bug_db_path = self.repo_path / "bug_tracking.json"
        self.load_bug_database()
    
    def load_bug_database(self):
        """Load the bug tracking database"""
        if self.bug_db_path.exists():
            try:
                with open(self.bug_db_path, 'r') as f:
                    self.bug_db = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.bug_db = {"tracked_bugs": {}, "resolved_bugs": {}}
        else:
            self.bug_db = {"tracked_bugs": {}, "resolved_bugs": {}}
    
    def save_bug_database(self):
        """Save the bug tracking database"""
        with open(self.bug_db_path, 'w') as f:
            json.dump(self.bug_db, f, indent=2)
    
    def run_gh_command(self, args: List[str]) -> Tuple[bool, str]:
        """Run a GitHub CLI command"""
        try:
            result = subprocess.run(
                ['gh'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout.strip()
        except FileNotFoundError:
            return False, "GitHub CLI not found. Install with: brew install gh"
        except Exception as e:
            return False, str(e)
    
    def create_bug_issue(self, test_name: str, error_message: str, 
                        test_output: str, context: Dict = None) -> Optional[str]:
        """Create a GitHub issue for a discovered bug"""
        
        # Create a unique bug identifier
        bug_id = f"test-{test_name}-{hash(error_message) % 10000}"
        
        # Check if we've already filed this bug
        if bug_id in self.bug_db["tracked_bugs"]:
            existing_issue = self.bug_db["tracked_bugs"][bug_id]
            print(f"🔍 Bug already tracked: Issue #{existing_issue['issue_number']}")
            return existing_issue["issue_number"]
        
        # Create issue title and body
        title = f"🐛 [AUTO] Bug in {test_name}: {error_message[:50]}..."
        
        body = f"""## 🐛 Automated Bug Report
        
**Test:** `{test_name}`
**Discovered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Bug ID:** `{bug_id}`

### Error Message
```
{error_message}
```

### Test Output
```
{test_output}
```

### Context
{json.dumps(context or {}, indent=2)}

### Reproduction Steps
1. Run the test suite: `python3 autotest.py --quick`
2. The test `{test_name}` should fail with the above error

### Expected Behavior
The test should pass without errors.

### Environment
- Python: {sys.version}
- Platform: {sys.platform}
- Working Directory: {os.getcwd()}

---
*This issue was automatically created by the CI system when a test failed.*
*Tag: `automated-bug-report`*
"""
        
        # Create the GitHub issue
        success, output = self.run_gh_command([
            'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', 'bug,automated'
        ])
        
        if success:
            # Extract issue number from output
            issue_number = output.split('/')[-1] if '/' in output else output
            
            # Track the bug in our database
            self.bug_db["tracked_bugs"][bug_id] = {
                "issue_number": issue_number,
                "test_name": test_name,
                "error_message": error_message,
                "created_at": datetime.now().isoformat(),
                "status": "open"
            }
            
            self.save_bug_database()
            print(f"✅ Filed GitHub issue #{issue_number} for bug: {error_message[:50]}...")
            return issue_number
        else:
            print(f"❌ Failed to create GitHub issue: {output}")
            return None
    
    def resolve_bug_issue(self, test_name: str, issue_number: str = None) -> bool:
        """Resolve a bug issue when the test passes"""
        
        # Find the bug by test name
        bug_to_resolve = None
        bug_id = None
        
        for bid, bug_info in self.bug_db["tracked_bugs"].items():
            if bug_info["test_name"] == test_name:
                if issue_number is None or bug_info["issue_number"] == issue_number:
                    bug_to_resolve = bug_info
                    bug_id = bid
                    break
        
        if not bug_to_resolve:
            return False
        
        # Get current commit for linking
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            current_commit = result.stdout.strip()
            short_commit = current_commit[:8] if result.returncode == 0 else "unknown"
        except:
            current_commit = "unknown"
            short_commit = "unknown"
        
        # Close the GitHub issue
        close_message = f"""## 🎉 Bug Resolved
        
**Test:** `{test_name}`
**Resolved:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Bug ID:** `{bug_id}`
**Resolution Commit:** `{short_commit}`

### Resolution
The test `{test_name}` is now passing. The bug has been automatically resolved.

### Related Commits
This issue was resolved around commit [`{short_commit}`](https://github.com/{self.get_repo_info()}/commit/{current_commit}).

### Verification
Run the test suite to verify the fix:
```bash
python3 autotest.py --quick
```

---
*This issue was automatically resolved by the CI system when the test started passing.*
"""
        
        success, output = self.run_gh_command([
            'issue', 'close', bug_to_resolve["issue_number"],
            '--comment', close_message
        ])
        
        if success:
            # Move bug to resolved database
            self.bug_db["resolved_bugs"][bug_id] = {
                **bug_to_resolve,
                "resolved_at": datetime.now().isoformat(),
                "status": "resolved"
            }
            
            # Remove from tracked bugs
            del self.bug_db["tracked_bugs"][bug_id]
            
            self.save_bug_database()
            print(f"✅ Resolved GitHub issue #{bug_to_resolve['issue_number']} for test: {test_name}")
            return True
        else:
            print(f"❌ Failed to close GitHub issue: {output}")
            return False
    
    def check_resolved_bugs(self, test_results: Dict) -> List[str]:
        """Check if any previously failing tests are now passing"""
        resolved_issues = []
        
        for bug_id, bug_info in list(self.bug_db["tracked_bugs"].items()):
            test_name = bug_info["test_name"]
            
            # Check if the test is now passing
            if test_results.get(test_name, {}).get("status") == "passed":
                issue_number = self.resolve_bug_issue(test_name)
                if issue_number:
                    resolved_issues.append(bug_info["issue_number"])
        
        return resolved_issues
    
    def get_bug_statistics(self) -> Dict:
        """Get statistics about tracked and resolved bugs"""
        return {
            "total_bugs_found": len(self.bug_db["tracked_bugs"]) + len(self.bug_db["resolved_bugs"]),
            "currently_tracked": len(self.bug_db["tracked_bugs"]),
            "resolved_bugs": len(self.bug_db["resolved_bugs"]),
            "resolution_rate": len(self.bug_db["resolved_bugs"]) / max(1, len(self.bug_db["tracked_bugs"]) + len(self.bug_db["resolved_bugs"]))
        }
    
    def list_tracked_bugs(self) -> List[Dict]:
        """List all currently tracked bugs"""
        return list(self.bug_db["tracked_bugs"].values())
    
    def list_resolved_bugs(self) -> List[Dict]:
        """List all resolved bugs"""
        return list(self.bug_db["resolved_bugs"].values())
    
    def get_repo_info(self):
        """Get repository owner/name for URL construction"""
        try:
            import subprocess
            result = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from various URL formats
                if 'github.com' in url:
                    if url.startswith('git@'):
                        # SSH format: git@github.com:owner/repo.git
                        parts = url.split(':')[1].replace('.git', '')
                    else:
                        # HTTPS format: https://github.com/owner/repo.git
                        parts = url.split('github.com/')[-1].replace('.git', '')
                    return parts
            
            return "unknown/unknown"
        except:
            return "unknown/unknown"


def main():
    """Main function for testing the issue manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Issue Manager for Bug Tracking")
    parser.add_argument("--test-create", action="store_true", help="Test creating a bug issue")
    parser.add_argument("--test-resolve", action="store_true", help="Test resolving a bug issue")
    parser.add_argument("--stats", action="store_true", help="Show bug statistics")
    parser.add_argument("--list-bugs", action="store_true", help="List tracked bugs")
    
    args = parser.parse_args()
    
    manager = GitHubIssueManager()
    
    if args.test_create:
        issue_number = manager.create_bug_issue(
            test_name="test_example",
            error_message="Example test failure",
            test_output="Test output here",
            context={"test_type": "unit", "component": "example"}
        )
        print(f"Created test issue: {issue_number}")
    
    if args.test_resolve:
        resolved = manager.resolve_bug_issue("test_example")
        print(f"Resolved test issue: {resolved}")
    
    if args.stats:
        stats = manager.get_bug_statistics()
        print("📊 Bug Statistics:")
        print(f"  Total bugs found: {stats['total_bugs_found']}")
        print(f"  Currently tracked: {stats['currently_tracked']}")
        print(f"  Resolved bugs: {stats['resolved_bugs']}")
        print(f"  Resolution rate: {stats['resolution_rate']:.2%}")
    
    if args.list_bugs:
        bugs = manager.list_tracked_bugs()
        print(f"📋 Tracked Bugs ({len(bugs)}):")
        for bug in bugs:
            print(f"  • #{bug['issue_number']} - {bug['test_name']}: {bug['error_message'][:50]}...")


if __name__ == "__main__":
    main()
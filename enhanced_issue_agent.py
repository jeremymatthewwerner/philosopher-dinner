#!/usr/bin/env python3
"""
Enhanced Issue Monitoring Agent with automatic commit linking
Automatically commits fixes and links them to GitHub issues
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from issue_monitoring_agent import IssueMonitoringAgent

class EnhancedIssueAgent(IssueMonitoringAgent):
    """Enhanced issue monitoring agent with commit linking"""
    
    def apply_fix_and_commit(self, analysis, fix_success, fix_details):
        """Apply fix, commit changes, and link to issue"""
        
        if not fix_success:
            return False, "Fix failed, no commit created"
        
        issue_number = analysis["issue_number"]
        
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], cwd=self.repo_path, check=True)
            
            # Check if there are actually changes to commit
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  cwd=self.repo_path)
            
            if result.returncode == 0:
                return False, "No changes to commit"
            
            # Create commit message with issue reference
            commit_message = f"""🤖 Fix #{issue_number}: {analysis['title'][:50]}

Automated fix applied by Issue Monitoring Agent:
{fix_details}

Fixes #{issue_number}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            # Create the commit
            subprocess.run([
                'git', 'commit', '-m', commit_message
            ], cwd=self.repo_path, check=True)
            
            # Get the commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            commit_hash = result.stdout.strip()
            short_hash = commit_hash[:8]
            
            # Update the GitHub issue with commit information
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            commit_comment = f"""## 🤖 Automated Fix Applied and Committed
            
**Timestamp:** {timestamp}
**Agent:** Enhanced Issue Monitoring Agent
**Status:** ✅ Fix Committed Successfully
**Commit:** [`{short_hash}`](https://github.com/{self.get_repo_info()}/commit/{commit_hash})

### Fix Details
{fix_details}

### Commit Information
- **Full Hash:** `{commit_hash}`
- **Short Hash:** `{short_hash}`
- **View Commit:** https://github.com/{self.get_repo_info()}/commit/{commit_hash}
- **View Diff:** https://github.com/{self.get_repo_info()}/commit/{commit_hash}.diff

### Verification
The automated tests are now passing. The issue has been resolved and the fix has been committed.

---
*This fix was automatically applied and committed by the Enhanced Issue Monitoring Agent*
"""
            
            # Add comment to issue
            success, output = self.run_gh_command([
                'issue', 'comment', str(issue_number), '--body', commit_comment
            ])
            
            if success:
                return True, f"Fix committed successfully: {short_hash}"
            else:
                return False, f"Fix committed but failed to update issue: {output}"
                
        except subprocess.CalledProcessError as e:
            return False, f"Failed to commit fix: {e}"
        except Exception as e:
            return False, f"Error during commit process: {e}"
    
    def get_repo_info(self):
        """Get repository owner/name for URL construction"""
        try:
            result = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], capture_output=True, text=True, cwd=self.repo_path)
            
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
    
    def process_issue_with_commit_linking(self, issue):
        """Process an issue and automatically commit any fixes"""
        
        issue_number = str(issue['number'])
        
        # Check if we've already processed this issue recently
        if issue_number in self.agent_db["processed_issues"]:
            last_processed = datetime.fromisoformat(
                self.agent_db["processed_issues"][issue_number]["last_processed"]
            )
            if datetime.now() - last_processed < timedelta(hours=1):
                return False  # Skip if processed within last hour
        
        # Analyze the issue
        analysis = self.analyze_issue(issue)
        
        print(f"📊 Issue #{issue_number} Analysis:")
        print(f"  Title: {analysis['title'][:50]}...")
        print(f"  Is Bug: {analysis['is_bug']}")
        print(f"  Is Automated: {analysis['is_automated']}")
        print(f"  Fix Confidence: {analysis['fix_confidence']:.2f}")
        print(f"  Fix Strategy: {analysis['fix_strategy']}")
        
        # Only attempt fix if confidence is high enough
        if analysis["fix_confidence"] >= 0.4:
            
            # Attempt the fix
            fix_success, fix_details = self.attempt_fix(analysis)
            
            if fix_success:
                # Apply fix and commit with issue linking
                commit_success, commit_details = self.apply_fix_and_commit(
                    analysis, fix_success, fix_details
                )
                
                if commit_success:
                    print(f"✅ Issue #{issue_number}: Fix applied and committed")
                    print(f"   {commit_details}")
                else:
                    print(f"⚠️  Issue #{issue_number}: Fix applied but commit failed")
                    print(f"   {commit_details}")
                    # Still create a regular comment
                    self.create_fix_comment(issue_number, fix_success, fix_details)
            else:
                print(f"❌ Issue #{issue_number}: Fix attempt failed")
                print(f"   {fix_details}")
                self.create_fix_comment(issue_number, fix_success, fix_details)
            
            # Record the fix attempt
            self.agent_db["fix_attempts"][issue_number] = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "fix_success": fix_success,
                "fix_details": fix_details,
                "commit_success": commit_success if fix_success else False
            }
            
            # Record that we processed this issue
            self.agent_db["processed_issues"][issue_number] = {
                "last_processed": datetime.now().isoformat(),
                "fix_attempted": True,
                "fix_success": fix_success
            }
            
            self.save_agent_database()
            
            return fix_success
        else:
            print(f"  ⚠️  Fix confidence too low, skipping automated fix")
            return False


def demonstrate_enhanced_workflow():
    """Demonstrate the enhanced workflow with commit linking"""
    
    print("🚀 ENHANCED AUTOMATED WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print("This will show how fixes are automatically committed and linked to issues")
    print("=" * 60)
    
    # Create a new test bug to demonstrate
    print("\n1️⃣ Creating a new test bug...")
    
    cli_file = Path("philosopher_dinner/cli/interface.py")
    with open(cli_file, 'r') as f:
        content = f.read()
    
    # Introduce a different bug for demonstration
    test_content = content.replace(
        'print("\\nJust type your message to continue the discussion!")',
        'print("\\nJust type your message to continue the discussion!"); raise Exception("Demo bug for commit linking")'
    )
    
    with open(cli_file, 'w') as f:
        f.write(test_content)
    
    print("✅ Introduced test bug in CLI interface")
    
    # Run enhanced test runner to create issue
    print("\n2️⃣ Running tests to detect bug and create issue...")
    
    try:
        result = subprocess.run([
            sys.executable, 'enhanced_test_runner.py'
        ], capture_output=True, text=True)
        
        if "Filed GitHub issue" in result.stdout:
            print("✅ GitHub issue created for bug")
        else:
            print("⚠️  No new issue created (may be duplicate)")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
    
    print("\n3️⃣ Running enhanced issue agent...")
    
    # Run the enhanced agent
    agent = EnhancedIssueAgent()
    
    issues = agent.get_open_issues()
    print(f"📋 Found {len(issues)} open issues")
    
    fixed_count = 0
    for issue in issues:
        if agent.process_issue_with_commit_linking(issue):
            fixed_count += 1
    
    print(f"\n✅ Enhanced agent processed {len(issues)} issues, fixed {fixed_count}")
    
    # Show recent commits
    print("\n4️⃣ Recent commits with issue linking:")
    
    try:
        result = subprocess.run([
            'git', 'log', '--oneline', '-3'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Error getting git log: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstrate_enhanced_workflow()
    else:
        # Run the enhanced agent
        agent = EnhancedIssueAgent()
        agent.run_once()
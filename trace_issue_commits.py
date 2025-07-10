#!/usr/bin/env python3
"""
Trace Issue-to-Commit Links
Find the commits that fixed specific GitHub issues
"""

import subprocess
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def get_issue_details(issue_number: str) -> Optional[Dict]:
    """Get details about a GitHub issue"""
    try:
        result = subprocess.run([
            'gh', 'issue', 'view', issue_number, '--json', 
            'number,title,body,state,createdAt,closedAt,comments'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Error getting issue details: {e}")
        return None

def get_commits_around_time(start_time: str, end_time: str) -> List[Dict]:
    """Get commits within a time range"""
    try:
        result = subprocess.run([
            'git', 'log', '--pretty=format:%H|%h|%s|%an|%ad', 
            '--date=iso', f'--since={start_time}', f'--until={end_time}'
        ], capture_output=True, text=True)
        
        commits = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'short_hash': parts[1],
                            'message': parts[2],
                            'author': parts[3],
                            'date': parts[4]
                        })
        return commits
    except Exception as e:
        print(f"Error getting commits: {e}")
        return []

def find_fix_commits(issue_number: str) -> List[Dict]:
    """Find commits that likely fixed the given issue"""
    
    issue = get_issue_details(issue_number)
    if not issue:
        return []
    
    print(f"🔍 Analyzing Issue #{issue_number}: {issue['title'][:50]}...")
    
    # Get time range to search for commits
    created_at = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
    
    if issue['state'] == 'CLOSED' and issue['closedAt']:
        closed_at = datetime.fromisoformat(issue['closedAt'].replace('Z', '+00:00'))
        # Search from creation to closure + 1 hour buffer
        end_time = closed_at + timedelta(hours=1)
    else:
        # For open issues, search up to now
        end_time = datetime.now()
    
    print(f"📅 Searching commits from {created_at} to {end_time}")
    
    # Get commits in the time range
    commits = get_commits_around_time(
        created_at.strftime('%Y-%m-%dT%H:%M:%S'),
        end_time.strftime('%Y-%m-%dT%H:%M:%S')
    )
    
    # Find commits that reference this issue
    likely_fixes = []
    
    for commit in commits:
        commit_score = 0
        reasons = []
        
        # Check for direct issue reference
        if f"#{issue_number}" in commit['message']:
            commit_score += 10
            reasons.append(f"Direct reference to #{issue_number}")
        
        # Check for "fix" keywords
        fix_keywords = ['fix', 'resolve', 'close', 'fixes', 'resolves', 'closes']
        for keyword in fix_keywords:
            if keyword.lower() in commit['message'].lower():
                commit_score += 3
                reasons.append(f"Contains fix keyword: {keyword}")
        
        # Check for automated commit markers
        if "🤖" in commit['message'] or "automated" in commit['message'].lower():
            commit_score += 5
            reasons.append("Automated commit marker")
        
        # Check for help-related fixes if issue is about help
        if "help" in issue['title'].lower() and "help" in commit['message'].lower():
            commit_score += 4
            reasons.append("Help-related fix for help issue")
        
        # If commit is right around issue closure time
        if issue['state'] == 'CLOSED' and issue['closedAt']:
            closed_time = datetime.fromisoformat(issue['closedAt'].replace('Z', '+00:00'))
            commit_time = datetime.fromisoformat(commit['date'].replace(' ', 'T'))
            
            time_diff = abs((commit_time - closed_time).total_seconds())
            if time_diff < 3600:  # Within 1 hour
                commit_score += 7
                reasons.append(f"Committed within 1 hour of issue closure ({time_diff/60:.1f} min)")
        
        if commit_score > 5:  # Threshold for likely fix
            likely_fixes.append({
                'commit': commit,
                'score': commit_score,
                'reasons': reasons
            })
    
    # Sort by score (highest first)
    likely_fixes.sort(key=lambda x: x['score'], reverse=True)
    
    return likely_fixes

def analyze_issue_comments_for_commits(issue_number: str) -> List[str]:
    """Look for commit hashes mentioned in issue comments"""
    
    try:
        result = subprocess.run([
            'gh', 'issue', 'view', issue_number, '--comments'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            comments_text = result.stdout
            
            # Look for commit hash patterns (8+ hex characters)
            commit_pattern = r'\b[a-f0-9]{8,40}\b'
            potential_commits = re.findall(commit_pattern, comments_text)
            
            # Verify these are actual commit hashes
            verified_commits = []
            for potential_hash in potential_commits:
                try:
                    verify_result = subprocess.run([
                        'git', 'show', '--no-patch', '--format="%H"', potential_hash
                    ], capture_output=True, text=True)
                    
                    if verify_result.returncode == 0:
                        verified_commits.append(potential_hash)
                except:
                    continue
            
            return verified_commits
        
    except Exception as e:
        print(f"Error analyzing comments: {e}")
    
    return []

def trace_issue_to_commits(issue_number: str):
    """Main function to trace an issue to its fixing commits"""
    
    print(f"🔗 TRACING ISSUE #{issue_number} TO COMMITS")
    print("=" * 50)
    
    # Method 1: Find commits mentioned in comments
    print("\n📝 Method 1: Commits mentioned in issue comments")
    comment_commits = analyze_issue_comments_for_commits(issue_number)
    
    if comment_commits:
        print(f"✅ Found {len(comment_commits)} commits mentioned in comments:")
        for commit_hash in comment_commits:
            try:
                result = subprocess.run([
                    'git', 'show', '--no-patch', '--format=%h %s (%an, %ar)', commit_hash
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  🔸 {result.stdout.strip()}")
                    print(f"    View: https://github.com/{get_repo_name()}/commit/{commit_hash}")
            except:
                print(f"  🔸 {commit_hash[:8]} (details unavailable)")
    else:
        print("  ❌ No commits found in comments")
    
    # Method 2: Analyze commit timeline and content
    print("\n🕒 Method 2: Timeline and content analysis")
    likely_fixes = find_fix_commits(issue_number)
    
    if likely_fixes:
        print(f"✅ Found {len(likely_fixes)} likely fix commits:")
        for i, fix in enumerate(likely_fixes[:3]):  # Show top 3
            commit = fix['commit']
            print(f"\n  {i+1}. {commit['short_hash']} - Score: {fix['score']}")
            print(f"     Message: {commit['message'][:60]}...")
            print(f"     Author: {commit['author']}")
            print(f"     Date: {commit['date']}")
            print(f"     Reasons: {', '.join(fix['reasons'])}")
            print(f"     View: https://github.com/{get_repo_name()}/commit/{commit['hash']}")
    else:
        print("  ❌ No likely fix commits found")
    
    # Method 3: Direct git log search
    print(f"\n🔍 Method 3: Git log search for issue #{issue_number}")
    try:
        result = subprocess.run([
            'git', 'log', '--grep', f'#{issue_number}', '--oneline'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Found commits that reference this issue:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    hash_msg = line.split(' ', 1)
                    if len(hash_msg) == 2:
                        commit_hash, message = hash_msg
                        print(f"  🔸 {commit_hash} {message[:60]}...")
                        print(f"    View: https://github.com/{get_repo_name()}/commit/{commit_hash}")
        else:
            print("  ❌ No commits found that reference this issue")
    except Exception as e:
        print(f"  ❌ Error searching git log: {e}")

def get_repo_name():
    """Get the repository name for URL construction"""
    try:
        result = subprocess.run([
            'git', 'remote', 'get-url', 'origin'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            url = result.stdout.strip()
            if 'github.com' in url:
                if url.startswith('git@'):
                    return url.split(':')[1].replace('.git', '')
                else:
                    return url.split('github.com/')[-1].replace('.git', '')
        return "unknown/unknown"
    except:
        return "unknown/unknown"

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trace GitHub issues to fixing commits")
    parser.add_argument("issue_number", help="GitHub issue number to trace")
    
    args = parser.parse_args()
    
    trace_issue_to_commits(args.issue_number)

if __name__ == "__main__":
    main()
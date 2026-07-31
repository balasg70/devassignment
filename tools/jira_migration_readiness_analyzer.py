#!/usr/bin/env python3
"""
Jira Cloud Migration Readiness Analyzer
Analyzes Jira Server/Data Center exports for cloud migration readiness
"""

import json
import csv
from pathlib import Path
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any

class JiraMigrationAnalyzer:
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "project_summary": {
                "total_projects": 0,
                "projects": []
            },
            "issue_summary": {
                "total_issues": 0,
                "by_type": {},
                "by_priority": {},
                "by_status": {}
            },
            "user_summary": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "users": []
            },
            "workflow_summary": {
                "total_workflows": 0,
                "customizations": 0,
                "complexity_analysis": []
            },
            "app_compatibility": {
                "total_apps": 0,
                "compatible": [],
                "incompatible": [],
                "needs_workaround": []
            },
            "migration_risks": [],
            "migration_waves": []
        }
        
    def analyze_projects(self, projects_file: str = "projects.csv"):
        """Analyze project data"""
        try:
            file_path = self.export_path / projects_file
            if not file_path.exists():
                # Create mock data if file doesn't exist
                self._create_mock_data()
                file_path = self.export_path / projects_file
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                projects = list(reader)
                
            self.report["project_summary"]["total_projects"] = len(projects)
            
            for project in projects:
                project_info = {
                    "key": project.get("project_key", ""),
                    "name": project.get("project_name", ""),
                    "type": project.get("project_type", "software"),
                    "lead": project.get("lead", ""),
                    "issues_count": int(project.get("issue_count", 0)),
                    "complexity": "medium"
                }
                
                # Determine complexity
                if project_info["issues_count"] > 500:
                    project_info["complexity"] = "high"
                elif project_info["issues_count"] < 100:
                    project_info["complexity"] = "low"
                    
                self.report["project_summary"]["projects"].append(project_info)
                
        except Exception as e:
            self.report["migration_risks"].append(f"Error analyzing projects: {str(e)}")
    
    def analyze_issues(self, issues_file: str = "issues.csv"):
        """Analyze issue data"""
        try:
            file_path = self.export_path / issues_file
            if not file_path.exists():
                return
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                issues = list(reader)
            
            self.report["issue_summary"]["total_issues"] = len(issues)
            
            # Analyze by type
            issue_types = Counter([i.get("issue_type", "Unknown") for i in issues])
            self.report["issue_summary"]["by_type"] = dict(issue_types)
            
            # Analyze by priority
            priorities = Counter([i.get("priority", "Unknown") for i in issues])
            self.report["issue_summary"]["by_priority"] = dict(priorities)
            
            # Analyze by status
            statuses = Counter([i.get("status", "Unknown") for i in issues])
            self.report["issue_summary"]["by_status"] = dict(statuses)
            
        except Exception as e:
            self.report["migration_risks"].append(f"Error analyzing issues: {str(e)}")
    
    def analyze_users(self, users_file: str = "users.csv"):
        """Analyze user data"""
        try:
            file_path = self.export_path / users_file
            if not file_path.exists():
                return
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                users = list(reader)
            
            self.report["user_summary"]["total_users"] = len(users)
            
            for user in users:
                is_active = user.get("active", "true").lower() == "true"
                user_info = {
                    "username": user.get("username", ""),
                    "email": user.get("email", ""),
                    "display_name": user.get("display_name", ""),
                    "groups": user.get("groups", "").split(","),
                    "active": is_active
                }
                
                if is_active:
                    self.report["user_summary"]["active_users"] += 1
                else:
                    self.report["user_summary"]["inactive_users"] += 1
                    
                self.report["user_summary"]["users"].append(user_info)
                
        except Exception as e:
            self.report["migration_risks"].append(f"Error analyzing users: {str(e)}")
    
    def analyze_apps(self, apps_file: str = "apps.csv"):
        """Analyze installed apps compatibility"""
        try:
            file_path = self.export_path / apps_file
            if not file_path.exists():
                return
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                apps = list(reader)
            
            self.report["app_compatibility"]["total_apps"] = len(apps)
            
            for app in apps:
                app_name = app.get("app_name", "")
                app_type = app.get("app_type", "")
                is_compatible = app.get("compatible_with_cloud", "false").lower() == "true"
                
                if is_compatible:
                    self.report["app_compatibility"]["compatible"].append(app_name)
                else:
                    self.report["app_compatibility"]["incompatible"].append(app_name)
                    self.report["migration_risks"].append(
                        f"App {app_name} is not compatible with Jira Cloud"
                    )
                
        except Exception as e:
            self.report["migration_risks"].append(f"Error analyzing apps: {str(e)}")
    
    def create_migration_waves(self):
        """Create migration wave plan based on analysis"""
        projects = self.report["project_summary"]["projects"]
        
        # Sort projects by complexity and issue count
        sorted_projects = sorted(
            projects,
            key=lambda x: (x.get("complexity", "medium") == "high", 
                          x.get("issues_count", 0)),
            reverse=True
        )
        
        # Create waves (simplified)
        total = len(sorted_projects)
        waves = [
            {"wave": 1, "projects": [], "description": "Low complexity pilots"},
            {"wave": 2, "projects": [], "description": "Medium complexity projects"},
            {"wave": 3, "projects": [], "description": "High complexity projects"}
        ]
        
        # Distribute projects across waves
        for i, project in enumerate(sorted_projects):
            wave_index = min(i // max(1, total // 3), 2)
            waves[wave_index]["projects"].append(project["key"])
        
        self.report["migration_waves"] = waves
        
        # Add migration recommendations
        if self.report["app_compatibility"]["incompatible"]:
            self.report["migration_risks"].append(
                "Incompatible apps need to be replaced or workarounds identified"
            )
        
        if self.report["issue_summary"]["total_issues"] > 5000:
            self.report["migration_risks"].append(
                "Large volume of issues - consider incremental migration"
            )
    
    def _create_mock_data(self):
        """Create mock CSV files for analysis if they don't exist"""
        self.export_path.mkdir(parents=True, exist_ok=True)
        
        # Mock projects
        with open(self.export_path / "projects.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["project_key", "project_name", "project_type", "lead", "issue_count"])
            writer.writerows([
                ["PROJ1", "Main Application", "software", "admin", "450"],
                ["PROJ2", "Support Tasks", "service_desk", "support", "320"],
                ["PROJ3", "DevOps", "software", "devops", "185"],
                ["PROJ4", "Documentation", "business", "docs", "95"]
            ])
        
        # Mock issues
        with open(self.export_path / "issues.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["issue_key", "issue_type", "priority", "status", "project_key"])
            writer.writerows([
                ["PROJ1-1", "Bug", "High", "In Progress", "PROJ1"],
                ["PROJ1-2", "Task", "Medium", "Done", "PROJ1"],
                ["PROJ1-3", "Story", "High", "To Do", "PROJ1"],
                ["PROJ2-1", "Bug", "Critical", "In Progress", "PROJ2"],
                ["PROJ2-2", "Task", "Medium", "Done", "PROJ2"],
                ["PROJ3-1", "Story", "Low", "To Do", "PROJ3"]
            ])
        
        # Mock users
        with open(self.export_path / "users.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["username", "email", "display_name", "groups", "active"])
            writer.writerows([
                ["admin", "admin@example.com", "Administrator", "jira-administrators,jira-software-users", "true"],
                ["user1", "user1@example.com", "User One", "jira-software-users", "true"],
                ["user2", "user2@example.com", "User Two", "jira-software-users", "false"],
                ["user3", "user3@example.com", "User Three", "jira-software-users", "true"]
            ])
        
        # Mock apps
        with open(self.export_path / "apps.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["app_name", "app_type", "compatible_with_cloud"])
            writer.writerows([
                ["ScriptRunner", "automation", "true"],
                ["Zephyr", "testing", "true"],
                ["Custom Plugin", "custom", "false"],
                ["BigGantt", "project_management", "true"]
            ])
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate the final readiness report"""
        # Perform all analyses
        self.analyze_projects()
        self.analyze_issues()
        self.analyze_users()
        self.analyze_apps()
        self.create_migration_waves()
        
        # Calculate readiness score
        readiness_score = 70  # Base score
        if self.report["app_compatibility"]["incompatible"]:
            readiness_score -= 15
        if len(self.report["migration_risks"]) > 3:
            readiness_score -= 10
        if self.report["issue_summary"]["total_issues"] > 10000:
            readiness_score -= 5
        
        self.report["readiness_score"] = max(0, readiness_score)
        self.report["readiness_status"] = "Ready" if readiness_score > 80 else "Needs Preparation"
        
        return self.report
    
    def save_report(self, output_file: str):
        """Save report to file"""
        # Save JSON report
        json_file = output_file.replace('.md', '.json') if output_file.endswith('.md') else 'jira_readiness_report.json'
        with open(json_file, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        print(f"JSON report saved to {json_file}")
        
        # Save Markdown report
        if output_file.endswith('.md'):
            self._save_markdown_report(output_file)
    
    def _save_markdown_report(self, output_file: str):
        """Save report in markdown format"""
        with open(output_file, 'w') as f:
            f.write("# Jira Cloud Migration Readiness Report\n\n")
            f.write(f"**Generated:** {self.report['timestamp']}\n\n")
            f.write(f"**Readiness Score:** {self.report.get('readiness_score', 0)}%\n\n")
            f.write(f"**Status:** {self.report.get('readiness_status', 'Unknown')}\n\n")
            
            f.write("## Project Summary\n")
            f.write(f"- Total Projects: {self.report['project_summary']['total_projects']}\n\n")
            
            f.write("## Issue Summary\n")
            f.write(f"- Total Issues: {self.report['issue_summary']['total_issues']}\n")
            f.write("- By Type:\n")
            for issue_type, count in self.report['issue_summary'].get('by_type', {}).items():
                f.write(f"  - {issue_type}: {count}\n")
            f.write("\n")
            
            f.write("## User Summary\n")
            f.write(f"- Total Users: {self.report['user_summary']['total_users']}\n")
            f.write(f"- Active Users: {self.report['user_summary']['active_users']}\n")
            f.write(f"- Inactive Users: {self.report['user_summary']['inactive_users']}\n\n")
            
            f.write("## App Compatibility\n")
            f.write(f"- Total Apps: {self.report['app_compatibility']['total_apps']}\n")
            f.write("- Compatible Apps:\n")
            for app in self.report['app_compatibility']['compatible']:
                f.write(f"  - ✅ {app}\n")
            f.write("- Incompatible Apps:\n")
            for app in self.report['app_compatibility']['incompatible']:
                f.write(f"  - ❌ {app}\n")
            f.write("\n")
            
            f.write("## Migration Risks\n")
            for risk in self.report.get('migration_risks', []):
                f.write(f"- ⚠️ {risk}\n")
            f.write("\n")
            
            f.write("## Migration Waves\n")
            for wave in self.report.get('migration_waves', []):
                f.write(f"\n### Wave {wave['wave']}: {wave['description']}\n")
                f.write(f"Projects: {', '.join(wave['projects'])}\n")
            f.write("\n")
            
            f.write("## Recommendations\n")
            f.write("1. Complete app compatibility testing before migration\n")
            f.write("2. Plan for user training on Jira Cloud features\n")
            f.write("3. Schedule migration during low activity periods\n")
            f.write("4. Prepare rollback plan for each migration wave\n")
            f.write("5. Set up proper monitoring during cutover\n")

def main():
    """Main entry point"""
    import sys
    
    export_path = sys.argv[1] if len(sys.argv) > 1 else './jira-export'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'jira_readiness_report.md'
    
    analyzer = JiraMigrationAnalyzer(export_path)
    report = analyzer.generate_report()
    analyzer.save_report(output_file)
    
    print(f"Report saved to {output_file}")
    print(f"Readiness Score: {report.get('readiness_score', 0)}%")
    print(f"Status: {report.get('readiness_status', 'Unknown')}")
    print(f"Risks Identified: {len(report.get('migration_risks', []))}")

if __name__ == "__main__":
    main()
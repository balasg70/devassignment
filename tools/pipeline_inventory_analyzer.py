#!/usr/bin/env python3
"""
Pipeline Inventory Analyzer
Analyzes Jenkins, Bamboo, and GitLab CI/CD pipeline configurations
"""

import os
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class PipelineInventoryAnalyzer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.inventory = {
            "timestamp": datetime.now().isoformat(),
            "total_pipelines": 0,
            "pipelines": [],
            "summary": {
                "jenkins": 0,
                "bamboo": 0,
                "gitlab": 0,
                "secrets_found": 0,
                "deployment_targets": {},
                "build_tools": {},
                "risk_levels": {
                    "low": 0,
                    "medium": 0,
                    "high": 0
                }
            }
        }
    
    def analyze_jenkins(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Jenkinsfile"""
        result = {
            "type": "jenkins",
            "file": str(file_path),
            "stages": [],
            "tools": [],
            "secrets": [],
            "agents": [],
            "environment": []
        }
        
        try:
            content = file_path.read_text()
            
            # Find stages
            stage_pattern = r'stage\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            stages = re.findall(stage_pattern, content)
            result["stages"] = stages
            
            # Find tools
            tool_pattern = r'tool\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            tools = re.findall(tool_pattern, content)
            result["tools"] = list(set(tools))
            
            # Find credentials
            cred_pattern = r'credentials\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            creds = re.findall(cred_pattern, content)
            if creds:
                result["secrets"] = list(set(creds))
            
            # Find agents
            agent_pattern = r'agent\s*\{[^}]*label\s*[\'"]([^\'"]+)[\'"]'
            agents = re.findall(agent_pattern, content)
            result["agents"] = list(set(agents)) if agents else ["default"]
            
            # Find environment variables
            env_pattern = r'env\.([A-Z_]+)'
            env_vars = re.findall(env_pattern, content)
            result["environment"] = list(set(env_vars))
            
            # Determine build tool
            if "maven" in content.lower():
                result["build_tool"] = "maven"
            elif "gradle" in content.lower():
                result["build_tool"] = "gradle"
            else:
                result["build_tool"] = "unknown"
            
            # Risk assessment
            risk = "low"
            if result["secrets"] or "prod" in "".join(stages).lower():
                risk = "high"
            elif len(stages) > 5:
                risk = "medium"
            result["risk"] = risk
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def analyze_bamboo(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Bamboo YAML Specs"""
        result = {
            "type": "bamboo",
            "file": str(file_path),
            "stages": [],
            "jobs": [],
            "tasks": [],
            "secrets": [],
            "agents": [],
            "environment": []
        }
        
        try:
            content = file_path.read_text()
            
            # Try to parse as YAML
            try:
                data = yaml.safe_load(content)
                if data:
                    # Extract stages
                    if 'stages' in data:
                        result["stages"] = [s.get('name', 'stage') for s in data.get('stages', [])]
                    
                    # Extract jobs
                    if 'jobs' in data:
                        result["jobs"] = [j.get('name', 'job') for j in data.get('jobs', [])]
                    
                    # Extract tasks
                    if 'tasks' in data:
                        result["tasks"] = [t.get('task', 'unknown') for t in data.get('tasks', [])]
                    
                    # Extract secrets
                    secret_vars = re.findall(r'\$\{bamboo\.\S+\}', content)
                    if secret_vars:
                        result["secrets"] = list(set(secret_vars))
                    
                    # Extract agents
                    if 'agent' in data:
                        result["agents"] = [data['agent'].get('name', 'default')]
            except:
                # Fallback to regex
                pass
            
            # Determine risk
            risk = "medium"
            if result["secrets"] or len(result["stages"]) > 3:
                risk = "high"
            elif len(result["stages"]) <= 2:
                risk = "low"
            result["risk"] = risk
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def analyze_gitlab(self, file_path: Path) -> Dict[str, Any]:
        """Analyze GitLab CI file"""
        result = {
            "type": "gitlab",
            "file": str(file_path),
            "stages": [],
            "jobs": [],
            "secrets": [],
            "variables": [],
            "artifacts": []
        }
        
        try:
            content = file_path.read_text()
            
            # Parse YAML
            try:
                data = yaml.safe_load(content)
                if data:
                    # Extract stages
                    if 'stages' in data:
                        result["stages"] = data.get('stages', [])
                    
                    # Extract jobs
                    jobs = [k for k, v in data.items() if isinstance(v, dict) and 'script' in v]
                    result["jobs"] = jobs
                    
                    # Extract variables
                    if 'variables' in data:
                        result["variables"] = list(data['variables'].keys())
                    
                    # Extract secrets
                    var_refs = re.findall(r'\$\{?([A-Z_]+)\}?', content)
                    if var_refs:
                        result["secrets"] = list(set(var_refs))
                    
                    # Extract artifacts
                    artifact_pattern = r'artifacts:'
                    if re.search(artifact_pattern, content):
                        artifact_match = re.findall(r'paths:\s*-\s*([^\n]+)', content)
                        result["artifacts"] = artifact_match
            except:
                pass
            
            # Determine risk
            risk = "medium"
            if result["secrets"] or "prod" in " ".join(result["stages"]).lower():
                risk = "high"
            elif len(result["jobs"]) <= 3:
                risk = "low"
            result["risk"] = risk
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def analyze_directory(self, path: Path):
        """Analyze all pipeline files in directory"""
        for file_path in path.rglob('*'):
            if file_path.is_file():
                if file_path.name == 'Jenkinsfile':
                    result = self.analyze_jenkins(file_path)
                    self.inventory["pipelines"].append(result)
                    self.inventory["summary"]["jenkins"] += 1
                    self.inventory["total_pipelines"] += 1
                    self._update_summary(result)
                
                elif file_path.suffix in ['.yml', '.yaml'] and 'bamboo' in file_path.name.lower():
                    result = self.analyze_bamboo(file_path)
                    self.inventory["pipelines"].append(result)
                    self.inventory["summary"]["bamboo"] += 1
                    self.inventory["total_pipelines"] += 1
                    self._update_summary(result)
                
                elif file_path.name == '.gitlab-ci.yml':
                    result = self.analyze_gitlab(file_path)
                    self.inventory["pipelines"].append(result)
                    self.inventory["summary"]["gitlab"] += 1
                    self.inventory["total_pipelines"] += 1
                    self._update_summary(result)
    
    def _update_summary(self, result: Dict[str, Any]):
        """Update summary statistics"""
        # Update risk levels
        risk = result.get('risk', 'medium')
        self.inventory["summary"]["risk_levels"][risk] = \
            self.inventory["summary"]["risk_levels"].get(risk, 0) + 1
        
        # Update secrets count
        if result.get('secrets'):
            self.inventory["summary"]["secrets_found"] += len(result['secrets'])
        
        # Update build tools
        if 'build_tool' in result:
            tool = result['build_tool']
            self.inventory["summary"]["build_tools"][tool] = \
                self.inventory["summary"]["build_tools"].get(tool, 0) + 1
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final report"""
        return self.inventory
    
    def save_report(self, output_file: str):
        """Save report to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.inventory, f, indent=2, default=str)
        print(f"Report saved to {output_file}")

def main():
    """Main entry point"""
    import sys
    
    base_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'pipeline_inventory.json'
    
    analyzer = PipelineInventoryAnalyzer(base_path)
    analyzer.analyze_directory(Path(base_path))
    report = analyzer.generate_report()
    analyzer.save_report(output_file)
    
    # Print summary
    print("\n=== Pipeline Inventory Summary ===")
    print(f"Total Pipelines: {report['total_pipelines']}")
    print(f"  - Jenkins: {report['summary']['jenkins']}")
    print(f"  - Bamboo: {report['summary']['bamboo']}")
    print(f"  - GitLab: {report['summary']['gitlab']}")
    print(f"\nRisk Levels:")
    for level, count in report['summary']['risk_levels'].items():
        print(f"  - {level.capitalize()}: {count}")
    print(f"\nSecrets Found: {report['summary']['secrets_found']}")
    print(f"Build Tools: {report['summary']['build_tools']}")

if __name__ == "__main__":
    main()
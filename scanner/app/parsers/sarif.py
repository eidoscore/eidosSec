"""Generic SARIF Parser for security tools"""
import json
import logging
from typing import List, Dict, Any, Optional
from app.schemas import FindingSchema, SeverityLevel

logger = logging.getLogger(__name__)

class SarifParser:
    """
    Parses SARIF (Static Analysis Results Interchange Format) JSON output.
    Used by modern tools like CodeQL, Trivy, Gosec, etc.
    """
    
    @staticmethod
    def parse(sarif_content: str, tool_name: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(sarif_content)
            
            for run in data.get("runs", []):
                # Map rules for metadata lookup
                rules = {}
                if "tool" in run and "driver" in run["tool"] and "rules" in run["tool"]["driver"]:
                    for rule in run["tool"]["driver"]["rules"]:
                        rules[rule["id"]] = rule
                
                for result in run.get("results", []):
                    try:
                        rule_id = result.get("ruleId")
                        rule_desc = rules.get(rule_id, {}).get("shortDescription", {}).get("text", "No description")
                        
                        # Determine severity
                        level = result.get("level", "warning")
                        severity = SarifParser._map_severity(level)
                        
                        # Get location
                        locations = result.get("locations", [])
                        if not locations:
                            continue
                            
                        physical_loc = locations[0].get("physicalLocation", {})
                        file_path = physical_loc.get("artifactLocation", {}).get("uri", "unknown")
                        region = physical_loc.get("region", {})
                        line_start = region.get("startLine", 1)
                        line_end = region.get("endLine", line_start)
                        snippet = region.get("snippet", {}).get("text", None)
                        
                        findings.append(FindingSchema(
                            type=rule_id or tool_name,
                            severity=severity,
                            confidence=80, # Default high confidence for SARIF tools
                            file_path=file_path,
                            line_start=line_start,
                            line_end=line_end,
                            message=result.get("message", {}).get("text", rule_desc),
                            code_snippet=snippet,
                            metadata={
                                "tool": tool_name,
                                "raw_rule": rules.get(rule_id, {})
                            }
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse individual SARIF result: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to parse SARIF output for {tool_name}: {e}")
            
        return findings

    @staticmethod
    def _map_severity(level: str) -> SeverityLevel:
        level = level.lower()
        if level in ["error", "critical"]:
            return SeverityLevel.CRITICAL
        elif level == "warning":
            return SeverityLevel.MEDIUM
        elif level == "note":
            return SeverityLevel.INFO
        return SeverityLevel.MEDIUM

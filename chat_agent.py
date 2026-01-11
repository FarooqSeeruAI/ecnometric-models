#!/usr/bin/env python3
"""
Conversational AI Agent for CGE Model
Handles natural language questions and converts them to MCP tool calls
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class CGEModelChatAgent:
    """
    Conversational agent that interprets natural language questions
    and prepares MCP tool call payloads
    """
    
    def __init__(self):
        self.variable_mappings = self._load_variable_mappings()
        self.sector_mappings = self._load_sector_mappings()
        self.question_patterns = self._load_question_patterns()
    
    def _load_variable_mappings(self) -> Dict[str, str]:
        """Map natural language terms to model variables"""
        return {
            # Employment
            "emirati employment": "x1labiEmplWgt_EMIRATI",
            "emirati workforce": "x1labiEmplWgt_EMIRATI",
            "emiratization": "x1labiEmplWgt_EMIRATI",
            "migrant employment": "x1labiEmplWgt_MIGRANTHH",
            "migrant workforce": "x1labiEmplWgt_MIGRANTHH",
            "commuting employment": "x1labiEmplWgt_COMMUTING",
            "employment": "employi",
            "labor": "f1labio",
            "wages": "p1labi",
            
            # Economic
            "gdp": "realgdp",
            "gdp growth": "realgdp",
            "economic growth": "realgdp",
            "gdp income": "INCGDP",
            "inflation": "p3tot",
            "cpi": "p3tot",
            "consumer price": "p3tot",
            "prices": "p3tot",
            
            # Productivity
            "productivity": "aprimRatio",
            "agriculture productivity": "aprimRatio_AG",
            "mining productivity": "aprimRatio_MIN",
            "manufacturing productivity": "aprimRatio_MACH",
            
            # Tax
            "tax": "taxcsi",
            "tax rate": "taxcsi",
            "taxation": "taxcsi",
        }
    
    def _load_sector_mappings(self) -> Dict[str, str]:
        """Map sector names to codes"""
        return {
            "agriculture": "AG",
            "farming": "AG",
            "mining": "MIN",
            "food": "FBT",
            "food and beverages": "FBT",
            "textiles": "TEX",
            "leather": "LEATHER",
            "wood": "WOOD",
            "paper": "PPP",
            "chemicals": "CHM",
            "rubber": "RUBBER",
            "metals": "METAL",
            "machinery": "MACH",
            "electrical": "ELEC",
            "transport equipment": "TRNEQUIP",
            "construction": "CNS",
            "trade": "TRD",
            "transport": "ATP",
            "finance": "OFI",
            "government": "GOV",
            "education": "EDU",
            "health": "HHT",
            "real estate": "RSA",
        }
    
    def _load_question_patterns(self) -> Dict[str, Any]:
        """Patterns for different question types"""
        return {
            "run_scenario": [
                r"what (would|will|if)",
                r"what (happen|be|result)",
                r"analyze (the|a) (impact|effect|consequence)",
                r"simulate",
                r"run (a|the) (scenario|simulation|model)",
                r"show (me|us) (what|how)",
                r"calculate",
                r"what if",
            ],
            "compare": [
                r"compare",
                r"difference (between|in)",
                r"versus|vs",
                r"better (than|or)",
            ],
            "list": [
                r"what (variables|sectors|options)",
                r"list (variables|sectors)",
                r"show (me|us) (available|all)",
                r"what (can|could) (i|we) (shock|change|modify)",
            ],
            "status": [
                r"status (of|for)",
                r"is (it|the scenario) (done|finished|complete)",
                r"how (is|are) (the|it)",
            ],
            "results": [
                r"results (of|for|from)",
                r"what (are|were) (the|results)",
                r"show (me|us) (the|results)",
                r"get (the|results)",
            ],
        }
    
    def parse_question(self, question: str) -> Dict[str, Any]:
        """
        Parse a natural language question and determine the intent
        
        Returns:
        --------
        Dict with:
            - intent: str (run_scenario, compare, list, status, results)
            - tool: str (MCP tool name)
            - payload: Dict (tool arguments)
            - confidence: float (0-1)
        """
        question_lower = question.lower()
        
        # Determine intent
        intent = self._determine_intent(question_lower)
        
        # Extract payload based on intent
        if intent == "run_scenario":
            return self._parse_scenario_question(question_lower)
        elif intent == "compare":
            return self._parse_compare_question(question_lower)
        elif intent == "list":
            return self._parse_list_question(question_lower)
        elif intent == "status":
            return self._parse_status_question(question_lower)
        elif intent == "results":
            return self._parse_results_question(question_lower)
        else:
            return {
                "intent": "unknown",
                "tool": None,
                "payload": {},
                "confidence": 0.0,
                "message": "I didn't understand your question. Try asking about running scenarios, comparing results, or listing variables."
            }
    
    def _determine_intent(self, question: str) -> str:
        """Determine the intent from question patterns"""
        scores = {}
        for intent, patterns in self.question_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, question))
            if score > 0:
                scores[intent] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "unknown"
    
    def _parse_scenario_question(self, question: str) -> Dict[str, Any]:
        """Parse a scenario question and extract shocks"""
        shocks = {}
        scenario_name = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        year = 2023
        steps = 1
        
        # Extract percentages and values
        percentage_pattern = r"(\d+(?:\.\d+)?)\s*%"
        percentages = re.findall(percentage_pattern, question)
        
        # Extract variable mentions
        for term, variable in self.variable_mappings.items():
            if term in question:
                # Try to find associated percentage
                # Look for pattern like "15% emirati employment"
                pattern = rf"(\d+(?:\.\d+)?)\s*%[^\d]*{term}|{term}[^\d]*(\d+(?:\.\d+)?)\s*%"
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    value = float(match.group(1) or match.group(2))
                    shocks[variable] = value
                elif percentages:
                    # Use first percentage if found
                    shocks[variable] = float(percentages[0])
        
        # Extract sector productivity
        for sector_name, sector_code in self.sector_mappings.items():
            if sector_name in question:
                pattern = rf"(\d+(?:\.\d+)?)\s*%[^\d]*{sector_name}|{sector_name}[^\d]*(\d+(?:\.\d+)?)\s*%"
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    value = float(match.group(1) or match.group(2))
                    shocks[f"aprimRatio_{sector_code}"] = value
        
        # Extract GDP mentions
        if "gdp" in question or "economic growth" in question:
            gdp_match = re.search(r"(\d+(?:\.\d+)?)\s*%[^\d]*(?:gdp|growth)|(?:gdp|growth)[^\d]*(\d+(?:\.\d+)?)\s*%", question, re.IGNORECASE)
            if gdp_match:
                value = float(gdp_match.group(1) or gdp_match.group(2))
                shocks["realgdp"] = value
        
        # Extract year
        year_match = re.search(r"(?:year|in)\s+(\d{4})", question)
        if year_match:
            year = int(year_match.group(1))
        
        # Extract duration
        duration_match = re.search(r"(\d+)\s*(?:years?|steps?)", question)
        if duration_match:
            steps = int(duration_match.group(1))
        
        # Extract scenario name if mentioned
        name_match = re.search(r"(?:scenario|named|called)\s+['\"]?(\w+)['\"]?", question)
        if name_match:
            scenario_name = name_match.group(1)
        
        if not shocks:
            return {
                "intent": "run_scenario",
                "tool": "run_scenario",
                "payload": {},
                "confidence": 0.3,
                "message": "I found a scenario request but couldn't extract specific shocks. Please specify values like '15% emirati employment' or '5% GDP growth'."
            }
        
        return {
            "intent": "run_scenario",
            "tool": "run_scenario",
            "payload": {
                "scenario_name": scenario_name,
                "year": year,
                "steps": steps,
                "shocks": shocks
            },
            "confidence": 0.8,
            "message": f"Prepared scenario with shocks: {shocks}"
        }
    
    def _parse_compare_question(self, question: str) -> Dict[str, Any]:
        """Parse a comparison question"""
        # Extract scenario IDs if mentioned
        scenario_ids = re.findall(r"scenario[_\s]+(\w+)", question)
        
        return {
            "intent": "compare",
            "tool": "compare_scenarios",
            "payload": {
                "scenario_id_1": scenario_ids[0] if len(scenario_ids) > 0 else None,
                "scenario_id_2": scenario_ids[1] if len(scenario_ids) > 1 else None,
            },
            "confidence": 0.6 if len(scenario_ids) >= 2 else 0.3,
            "message": "Please provide two scenario IDs to compare"
        }
    
    def _parse_list_question(self, question: str) -> Dict[str, Any]:
        """Parse a list question"""
        category = "all"
        if "employment" in question:
            category = "employment"
        elif "economic" in question or "gdp" in question:
            category = "economic"
        elif "productivity" in question or "sector" in question:
            category = "productivity"
        elif "tax" in question:
            category = "tax"
        
        if "sector" in question:
            return {
                "intent": "list",
                "tool": "list_sectors",
                "payload": {},
                "confidence": 0.9
            }
        else:
            return {
                "intent": "list",
                "tool": "list_available_variables",
                "payload": {"category": category},
                "confidence": 0.8
            }
    
    def _parse_status_question(self, question: str) -> Dict[str, Any]:
        """Parse a status question"""
        scenario_id = re.search(r"scenario[_\s]+(\w+)", question)
        
        return {
            "intent": "status",
            "tool": "get_scenario_status",
            "payload": {
                "scenario_id": scenario_id.group(1) if scenario_id else None
            },
            "confidence": 0.7 if scenario_id else 0.3
        }
    
    def _parse_results_question(self, question: str) -> Dict[str, Any]:
        """Parse a results question"""
        scenario_id = re.search(r"scenario[_\s]+(\w+)", question)
        
        # Extract variables if mentioned
        variables = []
        for term, variable in self.variable_mappings.items():
            if term in question:
                variables.append(variable)
        
        return {
            "intent": "results",
            "tool": "get_scenario_results",
            "payload": {
                "scenario_id": scenario_id.group(1) if scenario_id else None,
                "variables": variables if variables else None,
                "format": "json"
            },
            "confidence": 0.7 if scenario_id else 0.3
        }
    
    def format_response(self, tool_response: Dict[str, Any], original_question: str) -> str:
        """Format MCP tool response into natural language"""
        if "error" in tool_response:
            return f"I encountered an error: {tool_response['error']}"
        
        if tool_response.get("tool") == "run_scenario":
            scenario_id = tool_response.get("scenario_id")
            return f"I've started running your scenario. Scenario ID: {scenario_id}. " \
                   f"You can check the status or get results once it completes."
        
        elif tool_response.get("tool") == "get_scenario_status":
            status = tool_response.get("status", "unknown")
            return f"The scenario status is: {status}"
        
        elif tool_response.get("tool") == "get_scenario_results":
            return f"Here are the results: {json.dumps(tool_response, indent=2)}"
        
        elif tool_response.get("tool") == "list_available_variables":
            return f"Available variables: {json.dumps(tool_response, indent=2)}"
        
        return json.dumps(tool_response, indent=2)


# Example usage
if __name__ == "__main__":
    agent = CGEModelChatAgent()
    
    # Test questions
    test_questions = [
        "What would happen if we increase Emirati employment by 15%?",
        "Run a scenario with 10% GDP growth and 5% increase in agriculture productivity",
        "Show me the results from scenario_12345",
        "What variables can I shock?",
        "Compare scenario_1 and scenario_2",
        "What's the status of scenario_20240101_120000?",
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        result = agent.parse_question(question)
        print(f"A: {json.dumps(result, indent=2)}")

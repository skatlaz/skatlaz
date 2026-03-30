"""
Learning Loop Module - Adaptive learning from interactions
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

class LearningLoop:
    """Adaptive learning system that improves from interactions"""
    
    def __init__(self, memory_path: str = "data/learning"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.memory_path / "interactions.json"
        self.learnings_file = self.memory_path / "learnings.json"
        
        self.interactions = self._load_interactions()
        self.learnings = self._load_learnings()
        
    def _load_interactions(self) -> List[Dict]:
        """Load past interactions"""
        if self.interactions_file.exists():
            try:
                with open(self.interactions_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_learnings(self) -> Dict:
        """Load learned patterns"""
        if self.learnings_file.exists():
            try:
                with open(self.learnings_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_interactions(self):
        """Save interactions to file"""
        try:
            with open(self.interactions_file, 'w') as f:
                json.dump(self.interactions[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            print(f"Error saving interactions: {e}")
    
    def _save_learnings(self):
        """Save learnings to file"""
        try:
            with open(self.learnings_file, 'w') as f:
                json.dump(self.learnings, f, indent=2)
        except Exception as e:
            print(f"Error saving learnings: {e}")
    
    def record_interaction(self, prompt: str, response: str, success: bool = True):
        """Record an interaction for learning"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt[:200],  # Limit length
            'response': response[:200],
            'success': success,
            'prompt_hash': hashlib.md5(prompt.encode()).hexdigest()
        }
        
        self.interactions.append(interaction)
        self._save_interactions()
        
        # Extract patterns for learning
        if success:
            self._learn_from_success(prompt, response)
        else:
            self._learn_from_failure(prompt, response)
    
    def _learn_from_success(self, prompt: str, response: str):
        """Learn from successful interactions"""
        # Extract key patterns
        prompt_keywords = self._extract_keywords(prompt)
        response_type = self._classify_response(response)
        
        for keyword in prompt_keywords:
            key = f"success_pattern_{keyword}"
            if key not in self.learnings:
                self.learnings[key] = {
                    'keyword': keyword,
                    'count': 0,
                    'response_types': {}
                }
            
            self.learnings[key]['count'] += 1
            
            if response_type not in self.learnings[key]['response_types']:
                self.learnings[key]['response_types'][response_type] = 0
            self.learnings[key]['response_types'][response_type] += 1
        
        self._save_learnings()
    
    def _learn_from_failure(self, prompt: str, response: str):
        """Learn from failed interactions"""
        prompt_keywords = self._extract_keywords(prompt)
        
        for keyword in prompt_keywords:
            key = f"failure_pattern_{keyword}"
            if key not in self.learnings:
                self.learnings[key] = {
                    'keyword': keyword,
                    'count': 0,
                    'suggestions': []
                }
            
            self.learnings[key]['count'] += 1
        
        self._save_learnings()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        import re
        # Simple keyword extraction
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        return list(set(words[:5]))  # Return unique keywords
    
    def _classify_response(self, response: str) -> str:
        """Classify the type of response"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['code', '```', 'function', 'class']):
            return 'code'
        elif any(word in response_lower for word in ['story', 'once upon', 'character']):
            return 'story'
        elif any(word in response_lower for word in ['weather', 'temperature', '°c']):
            return 'weather'
        elif any(word in response_lower for word in ['search', 'found', 'results']):
            return 'search'
        else:
            return 'chat'
    
    def get_learned_patterns(self) -> Dict:
        """Get learned patterns for optimization"""
        return {
            'success_patterns': {k: v for k, v in self.learnings.items() if k.startswith('success_pattern_')},
            'failure_patterns': {k: v for k, v in self.learnings.items() if k.startswith('failure_pattern_')},
            'total_interactions': len(self.interactions),
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate from interactions"""
        if not self.interactions:
            return 1.0
        
        successes = sum(1 for i in self.interactions if i.get('success', True))
        return successes / len(self.interactions)
    
    def get_suggestion(self, prompt: str) -> Optional[str]:
        """Get suggestion based on learned patterns"""
        keywords = self._extract_keywords(prompt)
        
        for keyword in keywords:
            pattern_key = f"success_pattern_{keyword}"
            if pattern_key in self.learnings:
                pattern = self.learnings[pattern_key]
                if pattern['count'] > 3:  # If we've seen this enough times
                    # Find best response type
                    if pattern['response_types']:
                        best_type = max(pattern['response_types'], key=pattern['response_types'].get)
                        return f"Based on past interactions, a {best_type} response works well for this topic."
            
            failure_key = f"failure_pattern_{keyword}"
            if failure_key in self.learnings:
                pattern = self.learnings[failure_key]
                if pattern['count'] > 2:
                    return "I've encountered similar questions before. Let me try a different approach to help better."
        
        return None
    
    def get_statistics(self) -> str:
        """Get learning statistics"""
        patterns = self.get_learned_patterns()
        
        stats = f"""📊 **Learning Statistics**

**Total Interactions:** {patterns['total_interactions']}
**Success Rate:** {patterns['success_rate']:.1%}

**Learned Patterns:**
- Success patterns: {len(patterns['success_patterns'])}
- Failure patterns: {len(patterns['failure_patterns'])}

**Improvement Areas:"""
        
        if patterns['failure_patterns']:
            stats += "\n  " + ", ".join(list(patterns['failure_patterns'].keys())[:3])
        else:
            stats += "\n  No failure patterns detected yet"
        
        return stats
    
    def reset_learning(self):
        """Reset all learning data"""
        self.interactions = []
        self.learnings = {}
        self._save_interactions()
        self._save_learnings()

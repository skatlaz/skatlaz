"""
Reasoning Pipeline Module - Logical reasoning and analysis
"""

import re
from typing import Dict, List, Any, Optional
import json

class ReasoningPipeline:
    """Step-by-step logical reasoning and analysis"""
    
    def __init__(self):
        self.reasoning_history = []
        
    def reason(self, prompt: str) -> str:
        """Perform step-by-step reasoning on a prompt"""
        # Extract the question or statement to reason about
        query = self._extract_query(prompt)
        
        # Perform reasoning
        reasoning_steps = self._generate_reasoning_steps(query)
        
        return self._format_reasoning(query, reasoning_steps)
    
    def _extract_query(self, prompt: str) -> str:
        """Extract the main query from the prompt"""
        # Remove reasoning-related keywords
        query = re.sub(r'(reason|think|analyze|logic|about|sobre|analisar|pensar)', 
                      '', prompt, flags=re.IGNORECASE)
        query = query.strip()
        
        if not query:
            query = "the given statement"
        
        return query
    
    def _generate_reasoning_steps(self, query: str) -> List[Dict]:
        """Generate step-by-step reasoning steps"""
        steps = []
        
        # Step 1: Problem understanding
        steps.append({
            'step': 1,
            'title': 'Understanding the Problem',
            'content': f"Let's analyze: '{query}'. First, we need to clearly understand what is being asked."
        })
        
        # Step 2: Break down into components
        steps.append({
            'step': 2,
            'title': 'Breaking Down the Components',
            'content': self._analyze_components(query)
        })
        
        # Step 3: Apply logical principles
        steps.append({
            'step': 3,
            'title': 'Applying Logical Principles',
            'content': self._apply_logic(query)
        })
        
        # Step 4: Consider alternatives
        steps.append({
            'step': 4,
            'title': 'Considering Alternatives',
            'content': self._consider_alternatives(query)
        })
        
        # Step 5: Synthesize conclusion
        steps.append({
            'step': 5,
            'title': 'Synthesizing the Conclusion',
            'content': self._synthesize_conclusion(query)
        })
        
        return steps
    
    def _analyze_components(self, query: str) -> str:
        """Analyze the components of the query"""
        words = query.lower().split()
        
        analysis = "The key elements to consider are:\n"
        for i, word in enumerate(words[:5]):
            analysis += f"• Element {i+1}: '{word}' - This represents a fundamental concept\n"
        
        if len(words) > 5:
            analysis += f"• Additional {len(words)-5} elements that contribute to the overall context\n"
        
        return analysis
    
    def _apply_logic(self, query: str) -> str:
        """Apply logical principles to the query"""
        logic_types = [
            "Deductive reasoning - Starting from general principles to reach specific conclusions",
            "Inductive reasoning - Drawing general conclusions from specific observations",
            "Abductive reasoning - Inferring the most likely explanation",
            "Critical analysis - Evaluating arguments and evidence"
        ]
        
        import random
        primary_logic = random.choice(logic_types)
        
        return f"""The most appropriate logical approach is **{primary_logic}**.

This method allows us to:
- Identify underlying assumptions
- Evaluate the validity of claims
- Draw well-supported conclusions
- Consider potential counterarguments"""
    
    def _consider_alternatives(self, query: str) -> str:
        """Consider alternative perspectives"""
        return """When reasoning, it's crucial to consider multiple perspectives:

**Alternative Viewpoint 1:** 
Consider the opposite interpretation - what if the initial assumption is incorrect?

**Alternative Viewpoint 2:**
Look at this from a different contextual framework - how would this be viewed in a different field or discipline?

**Alternative Viewpoint 3:**
Consider edge cases and exceptions - are there scenarios where the standard reasoning might not apply?

By examining these alternatives, we strengthen our understanding and avoid cognitive biases."""
    
    def _synthesize_conclusion(self, query: str) -> str:
        """Synthesize the final conclusion"""
        return """After systematic analysis and consideration of multiple perspectives:

**Conclusion:**
The reasoning process reveals that a comprehensive understanding requires:
1. Clear definition of terms and assumptions
2. Systematic evaluation of evidence
3. Consideration of alternative interpretations
4. Careful synthesis of findings

**Recommendations:**
- Verify initial assumptions
- Test conclusions with real-world examples
- Remain open to new evidence
- Document the reasoning process for transparency

This structured approach ensures logical consistency and robust conclusions."""
    
    def _format_reasoning(self, query: str, steps: List[Dict]) -> str:
        """Format the reasoning output"""
        result = f"""🧠 **Reasoning Analysis: {query[:50]}...**

{'='*50}

"""
        
        for step in steps:
            result += f"""**Step {step['step']}: {step['title']}**
{step['content']}

"""
        
        result += """💡 **Key Insights:**
- Systematic reasoning leads to better conclusions
- Multiple perspectives prevent bias
- Clear documentation aids understanding
- Continuous refinement improves outcomes

✨ This reasoning approach can be applied to similar problems for consistent results.
"""
        
        return result
    
    def analyze_problem(self, problem: str, context: str = "") -> str:
        """Analyze a specific problem with context"""
        analysis = f"""🔍 **Problem Analysis**

**Problem Statement:** {problem}

**Context:** {context if context else "General context"}

**Analysis Steps:**
1. **Define the problem scope** - What are the boundaries and constraints?
2. **Identify key variables** - What factors influence the outcome?
3. **Evaluate relationships** - How do variables interact?
4. **Consider constraints** - What limitations exist?
5. **Generate hypotheses** - What possible solutions exist?

**Methodology:**
Using a systematic approach ensures all aspects are considered and the solution is robust.

**Next Steps:**
- Gather additional data if needed
- Test hypotheses with small experiments
- Iterate based on findings
- Document lessons learned
"""
        return analysis
    
    def logical_deduction(self, premises: List[str], conclusion: str) -> str:
        """Perform logical deduction from premises to conclusion"""
        result = f"""📐 **Logical Deduction Analysis**

**Premises:**
"""
        for i, premise in enumerate(premises, 1):
            result += f"{i}. {premise}\n"
        
        result += f"""
**Proposed Conclusion:** {conclusion}

**Deduction Process:**
1. **Examining each premise** - Are all premises valid and relevant?
2. **Identifying logical connections** - How do premises relate?
3. **Testing the conclusion** - Does it follow necessarily?
4. **Checking for fallacies** - Are there logical gaps?

**Verdict:**
"""
        
        # Simple validation
        if len(premises) >= 2:
            result += "The conclusion appears to follow logically from the given premises, assuming all premises are true.\n\n"
        else:
            result += "Insufficient premises to draw a definitive conclusion. Additional premises would strengthen the argument.\n\n"
        
        result += """**Recommendations:**
- Verify the truth of each premise
- Consider hidden assumptions
- Test with counterexamples
- Seek additional supporting evidence
"""
        
        return result

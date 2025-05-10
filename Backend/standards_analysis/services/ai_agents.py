# standards_analysis/services/ai_agents.py
import re
import time
import json
import logging
from typing import List, Dict, Any

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage # For older Langchain, might be langchain_core.messages

from .ai_config import aicfg # Use the Django-integrated config

# Get a logger instance
logger = logging.getLogger('standards_analysis.ai_system.agents')

# --- StandardDocument Class (moved here or to ai_orchestration.py for better context) ---
class StandardDocument: # Copied from MAI.py
    """Class to represent an AAOIFI standard document."""
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content

# --- BaseAgent Class (from MAI.py / FastAPI structure) ---
class BaseAgent:
    def __init__(self, name: str, description: str, model_name: str = aicfg.GPT4_MODEL, **kwargs):
        self.name = name
        self.description = description
        self.model_name = model_name
        self.agent_type = kwargs.get("agent_type", "generic")
        self.logger = logging.getLogger(f'standards_analysis.ai_system.agents.{self.__class__.__name__}')

        if not aicfg.OPENAI_API_KEY:
            self.logger.error("OPENAI_API_KEY not set in AIConfig.")
            raise ValueError("OPENAI_API_KEY not set.")
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=aicfg.OPENAI_API_KEY, temperature=0.2)

    def execute(self, input_data: Any) -> Any:
        raise NotImplementedError("Subclasses must implement this method")

    def _run_llm_chain(self, prompt_template: ChatPromptTemplate, input_vars: Dict = None) -> str:
        if input_vars is None:
            input_vars = {}
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        try:
            # Langchain 0.1.0+
            if hasattr(chain, 'invoke'):
                 # If prompt template has input_variables, they must be in input_vars
                if prompt_template.input_variables:
                    response = chain.invoke(input_vars)
                else: # If prompt template has no input_variables (e.g. from_messages directly)
                    response = chain.invoke({}) # Pass empty dict
                return response.get("text", str(response)) if isinstance(response, dict) else str(response)
            else: # Fallback for older LangChain
                return chain.run(input_vars)
        except Exception as e:
            self.logger.error(f"Error running LLM chain ({self.name}): {e}. Input keys: {list(input_vars.keys()) if input_vars else 'None'}. Prompt vars: {prompt_template.input_variables}")
            # Try older run method as a fallback if invoke fails unexpectedly
            try:
                 return chain.run(input_vars if prompt_template.input_variables else {})
            except Exception as e2:
                self.logger.error(f"LLM chain run fallback also failed ({self.name}): {e2}")
                return f"Error in LLM call: {e2}"


    def log_execution(self, input_summary: str, output_summary: str, start_time: float):
        end_time = time.time()
        self.logger.info(
            f"Agent '{self.name}' (Type: {self.agent_type}) executed. "
            f"Duration: {end_time - start_time:.2f}s. "
            f"Input: {str(input_summary)[:100]}..., Output: {str(output_summary)[:100]}..."
        )

# --- NewBaseAgent Class (from MAI.py / FastAPI structure) ---
class NewBaseAgent:
    def __init__(self, name: str, description: str, agent_type: str, model_name: str = aicfg.GPT4_MODEL):
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.model_name = model_name
        self.logger = logging.getLogger(f'standards_analysis.ai_system.agents.{self.__class__.__name__}')

        if not aicfg.OPENAI_API_KEY:
            self.logger.error("OpenAI API key not found in AIConfig.")
            raise ValueError("OpenAI API key not configured.")
        self.llm = ChatOpenAI(model_name=self.model_name, openai_api_key=aicfg.OPENAI_API_KEY, temperature=0.2)

    def _run_chain(self, messages: List[Any]) -> str: # messages should be SystemMessage, HumanMessage etc.
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        try:
            if hasattr(chain, 'invoke'):
                response = chain.invoke({}) # Assuming messages fully define the prompt
                return response.get("text", str(response)) if isinstance(response, dict) else str(response)
            else:
                return chain.run({})
        except Exception as e:
            self.logger.error(f"Error running LLM chain for agent {self.name}: {e}")
            # Fallback attempt
            try:
                return chain.run({})
            except Exception as e2:
                self.logger.error(f"LLM chain run fallback also failed ({self.name}): {e2}")
                return f"Error in LLM call: {e2}"

    def log_execution(self, input_summary: str, output_summary: str, start_time: float):
        end_time = time.time()
        self.logger.info(
            f"Agent '{self.name}' (Type: {self.agent_type}) executed. "
            f"Duration: {end_time - start_time:.2f}s. "
            f"Input: {str(input_summary)[:100]}..., Output: {str(output_summary)[:100]}..."
        )

    def _extract_section(self, text: str, section_name: str, heading_level_char: str = "#", min_hashes: int = 2) -> str:
        # (Copied from MAI.py's NewBaseAgent)
        self.logger.debug(f"NewBaseAgent: Attempting to extract section: '{section_name}' with marker {heading_level_char*min_hashes}")
        processed_section_name_for_regex = re.escape(section_name.replace('_', ' '))
        marker_regex = re.escape(heading_level_char) * min_hashes
        pattern_str = (
            r"^[ \t]*" + marker_regex + r"\s*" +
            processed_section_name_for_regex +
            r"\s*\n" +
            r"(.*?)" +
            r"(?=(^[ \t]*" + marker_regex + r"\s*\w|\Z))"
        )
        pattern = re.compile(pattern_str, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        match = pattern.search(text)
        if match:
            extracted = match.group(1).strip()
            self.logger.info(f"NewBaseAgent: Successfully extracted section: '{section_name}'. Length: {len(extracted)}")
            if not extracted:
                 self.logger.warning(f"NewBaseAgent: Extracted section '{section_name}' is empty (heading found, no content under it).")
            return extracted
        self.logger.warning(f"NewBaseAgent: Section '{section_name}' (searched as '{processed_section_name_for_regex}' with marker '{marker_regex}') not found. Text searched (first 500 chars): {text[:500]}")
        return f"Section '{section_name}' not found."

# --- All specific agent implementations (ReviewAgent, EnhancementAgent, etc.) ---
# These will inherit from BaseAgent or NewBaseAgent and use their _run_llm_chain or _run_chain methods.
# Make sure they use `aicfg` for model names if needed.
# Example: ReviewAgent
class ReviewAgent(BaseAgent): # From MAI.py
    def __init__(self):
        super().__init__(
            name="ReviewAgent",
            description="Analyzes AAOIFI standards to extract key elements, principles, and requirements.",
            model_name=aicfg.GPT4_MODEL # Use configured model
        )
        self.system_prompt = """
        You are an expert in Islamic finance and AAOIFI standards. Your task is to carefully review
        the provided standard document and extract the following key elements.
        Use clear Markdown headings for each section exactly as listed below (e.g., ## Core principles and objectives).
        It is crucial that you provide content under each of these specified headings.

        ## Core principles and objectives
        [Your extraction here]
        ## Key definitions and terminology
        [Your extraction here]
        ## Main requirements and procedures
        [Your extraction here]
        ## Compliance criteria and guidelines
        [Your extraction here]
        ## Practical implementation considerations
        [Your extraction here]
        Be thorough but concise.
        """

    def execute(self, standard: StandardDocument) -> Dict[str, Any]: # Takes StandardDocument object
        start_time = time.time()
        
        # This prompt template will be used by _run_llm_chain.
        # The HumanMessage includes dynamic content.
        # _run_llm_chain needs to handle this. If input_vars is used by _run_llm_chain,
        # then the HumanMessage should use placeholders.
        # Given _run_llm_chain in BaseAgent, we construct the full prompt here.
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Standard Name: {standard.name}\n\nContent:\n{standard.content}")
        ])
        # Since the prompt messages are fully formed, pass {} as input_vars.
        result_text = self._run_llm_chain(prompt, {}) # No further variables for chain.run
        
        parsed_result = {
            "standard_name": standard.name,
            "review_result": result_text, 
            "core_principles": self._extract_section(result_text, "Core principles and objectives"),
            "key_definitions": self._extract_section(result_text, "Key definitions and terminology"),
            "main_requirements": self._extract_section(result_text, "Main requirements and procedures"),
            "compliance_criteria": self._extract_section(result_text, "Compliance criteria and guidelines"),
            "implementation_considerations": self._extract_section(result_text, "Practical implementation considerations")
        }
        self.log_execution(f"Standard: {standard.name}", parsed_result.get("core_principles","N/A"), start_time)
        return parsed_result

    def _extract_section(self, text: str, section_name: str) -> str:
        # (Copied from MAI.py's ReviewAgent)
        self.logger.debug(f"ReviewAgent: Attempting to extract section: '{section_name}'")
        escaped_section_name = re.escape(section_name)
        pattern_str = (
            r"^[ \t]*(?:##\s*)" + escaped_section_name + r"\s*\n" +
            r"(.*?)" + r"(?=(^[ \t]*##\s*\w|\Z))"
        )
        pattern = re.compile(pattern_str, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        match = pattern.search(text)
        if match:
            extracted_content = match.group(1).strip()
            self.logger.info(f"ReviewAgent: Successfully extracted section: '{section_name}'. Length: {len(extracted_content)}")
            if not extracted_content:
                self.logger.warning(f"ReviewAgent: Extracted section '{section_name}' is EMPTY. Text (500): {text[:500]}")
            return extracted_content
        else:
            self.logger.warning(f"ReviewAgent: Section '{section_name}' NOT FOUND. Text (500): {text[:500]}")
            # Fallback from MAI.py
            fallback_pattern_str = (
                r"^[ \t]*" + escaped_section_name + r"\s*\n" +
                r"(.*?)" + r"(?=(\n\s*\n|[#]{2}))"
            )
            fallback_pattern = re.compile(fallback_pattern_str, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            fallback_match = fallback_pattern.search(text)
            if fallback_match:
                extracted_content = fallback_match.group(1).strip()
                self.logger.info(f"ReviewAgent: Extracted section (FALLBACK): '{section_name}'. Length: {len(extracted_content)}")
                if not extracted_content:
                     self.logger.warning(f"ReviewAgent: Extracted section (fallback) '{section_name}' is empty.")
                return extracted_content
            self.logger.error(f"ReviewAgent: Section '{section_name}' NOT FOUND even with fallback.")
            return f"Section '{section_name}' not found or parsing error."

# ... (Paste ALL other agent classes: EnhancementAgent, ValidationAgent, FinalReportAgent,
#      DocumentReviewAgent, StandardAnalysisAgent, EnhancementAgentNew, ShariahComplianceAgent,
#      ValidationAgentNew, ReportGenerationAgent, VisualizationAgent, FeedbackAgent
#      from the MAI.py / FastAPI structure, adapting them like ReviewAgent to use `aicfg`
#      and ensuring their `execute` methods match the inputs they'll receive from the orchestrator)
#
# For brevity, I will assume these are correctly pasted and adapted.
# Key changes:
#   - `Config` becomes `aicfg` from `.ai_config`.
#   - Logger names are updated.
#   - Input to `DocumentReviewAgent.execute` should be `StandardDocument`.
#   - Ensure all `_extract_section` calls in agents use the correct method from their base class.

# Example for DocumentReviewAgent stub using the above ReviewAgent
class DocumentReviewAgent(NewBaseAgent):
    def __init__(self):
        super().__init__("Document Review Agent", "Reviews standard documents using original ReviewAgent logic", "review_stub")
        self._original_review_agent = ReviewAgent() # Uses the ReviewAgent defined above

    def execute(self, standard_doc: StandardDocument) -> Dict[str, Any]:
        self.logger.info(f"Executing DocumentReviewAgent (stub using original ReviewAgent) for {standard_doc.name}")
        return self._original_review_agent.execute(standard_doc) # Pass StandardDocument object

# StandardAnalysisAgent from MAI.py/FastAPI (adapted)
class StandardAnalysisAgent(NewBaseAgent):
    def __init__(self):
        super().__init__("Standard Analysis Agent", "Analyzes standards for challenges and improvements", "analysis", model_name=aicfg.GPT35_MODEL)
        self.system_prompt = """You are an AI analyst. Given a review of an AAOIFI standard, identify potential challenges in its current form and areas for improvement.
        Respond using the following Markdown headings for each section. Ensure substantial content under each heading:
        ## Challenges
        [List challenges here]
        ## Improvement Areas
        [List improvement areas here]
        """
    def execute(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = review_result.get("standard_name", "Unknown Standard")
        review_summary = review_result.get('review_result', 'N/A')[:1000]

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Standard Name: {standard_name}\nReview Summary (first 1000 chars): {review_summary}")
        ]
        analysis_text = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "full_analysis_text": analysis_text,
            "challenges": self._extract_section(analysis_text, "Challenges", min_hashes=2),
            "improvement_areas": self._extract_section(analysis_text, "Improvement Areas", min_hashes=2)
        }
        self.log_execution(f"Review for {standard_name}", analysis_text[:100], start_time)
        return result

# EnhancementAgentNew from MAI.py/FastAPI (adapted)
class EnhancementAgentNew(NewBaseAgent): 
    def __init__(self):
        super().__init__("Enhancement Agent (New)", "Proposes enhancements based on review and analysis", "enhancement", model_name=aicfg.GPT4_MODEL)
        self.system_prompt = """You are an AI expert for AAOIFI standards. Based on the standard review and identified challenges/improvement areas, propose specific enhancements.
        Organize proposals into the following categories using clear Markdown subheadings (e.g., ### clarity_improvements). Ensure each category heading is EXACTLY as written below (using underscores where shown AND three hashes ###) and on its own line, followed by substantial content on the next lines:
        ### clarity_improvements
        [Suggestions...]
        ### modern_adaptations
        [Suggestions...]
        ### tech_integration
        [Suggestions...]
        ### cross_references
        [Suggestions...]
        ### implementation_guidance
        [Suggestions...]
        For each proposal under these categories: specify the section, current concept, proposed modification, and justification."""

    def execute(self, review_result: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = review_result.get("standard_name", "Unknown Standard")
        review_summary = review_result.get('review_result', 'N/A')[:1000]
        challenges = analysis_result.get('challenges', 'N/A')
        improvement_areas = analysis_result.get('improvement_areas', 'N/A')
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
            Standard Name: {standard_name}
            Review Summary (first 1000 chars): {review_summary}... 
            Identified Challenges: {challenges}
            Identified Improvement Areas: {improvement_areas}
            Please generate enhancement proposals ensuring to use the exact specified ### subheadings for each category and provide substantial content for each.
            """)
        ]
        enhancement_text = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "enhancement_proposals": enhancement_text, 
            "clarity_improvements": self._extract_section(enhancement_text, "clarity_improvements", min_hashes=3),
            "modern_adaptations": self._extract_section(enhancement_text, "modern_adaptations", min_hashes=3),
            "tech_integration": self._extract_section(enhancement_text, "tech_integration", min_hashes=3),
            "cross_references": self._extract_section(enhancement_text, "cross_references", min_hashes=3),
            "implementation_guidance": self._extract_section(enhancement_text, "implementation_guidance", min_hashes=3)
        }
        self.log_execution(f"Analysis for {standard_name}", enhancement_text[:100], start_time)
        return result

# ShariahComplianceAgent from MAI.py/FastAPI (adapted)
class ShariahComplianceAgent(NewBaseAgent):
    def __init__(self):
        super().__init__("Shariah Compliance Agent", "Assesses Shariah compliance of proposals", "shariah_compliance", model_name=aicfg.GPT4_MODEL)
        self.system_prompt = """You are a Shariah scholar. Assess the Shariah compliance of the proposed enhancements to the AAOIFI standard.
        Provide a general shariah_assessment summary under a heading '## Shariah Assessment Summary'.
        Then, for each specific category of enhancement listed below, provide an overall_ruling (Approved, Conditionally Approved, Requires Modification, Rejected) and a brief justification.
        Format this as a Markdown list, with each item clearly starting with the category name (using underscores) followed by a colon and the ruling, then a hyphen and justification. Example:
        - clarity_improvements: Approved - The proposed changes enhance understanding without violating Shariah principles.
        Ensure you provide a ruling for all five categories: clarity_improvements, modern_adaptations, tech_integration, cross_references, implementation_guidance.
        """
    def execute(self, enhancement_result: Dict[str, Any], review_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = enhancement_result.get("standard_name", "Unknown Standard")
        enhancement_categories_keys = ["clarity_improvements", "modern_adaptations", "tech_integration", "cross_references", "implementation_guidance"]
        prompt_human_content = f"Standard Name: {standard_name}\nOriginal Review Summary (excerpt): {review_result.get('review_result', 'N/A')[:500]}...\n\nProposed Enhancements Summaries:\n"
        for key in enhancement_categories_keys:
            content = enhancement_result.get(key, "Category content not available.")
            prompt_human_content += f"\n{key.replace('_',' ').title()}:\n{(str(content)[:300] + '...') if len(str(content)) > 300 else str(content)}\n"
        full_proposals_text = enhancement_result.get('enhancement_proposals', 'N/A')
        prompt_human_content += f"\nFull Text of All Enhancement Proposals (for context):\n{full_proposals_text[:2000]}...\n"
        prompt_human_content += "\nPlease provide Shariah assessment as per the specified format."
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=prompt_human_content)]
        shariah_text = self._run_chain(messages)
        overall_rulings = {}
        for key in enhancement_categories_keys:
            pattern = re.compile(rf"^\s*[-*]?\s*{key}\s*:\s*([A-Za-z\s]+?)\s*-\s*(.*)", re.IGNORECASE | re.MULTILINE)
            match = pattern.search(shariah_text)
            overall_rulings[key] = match.group(1).strip() if match else "Not specifically assessed"
            if match: self.logger.info(f"Shariah ruling parsed for '{key}': {overall_rulings[key]}")
            else: self.logger.warning(f"Could not parse ruling for category '{key}'. Text: {shariah_text[:500]}")
        result = {
            "standard_name": standard_name,
            "shariah_assessment_full_text": shariah_text,
            "shariah_assessment_summary": self._extract_section(shariah_text, "Shariah Assessment Summary", min_hashes=2) or shariah_text, 
            "overall_ruling": overall_rulings
        }
        self.log_execution(f"Enhancements for {standard_name}", shariah_text[:100], start_time)
        return result

# ValidationAgentNew from MAI.py/FastAPI (adapted)
class ValidationAgentNew(NewBaseAgent): 
    def __init__(self):
        super().__init__("Validation Agent (New)", "Validates practical aspects of proposals", "validation", model_name=aicfg.GPT4_MODEL)
        self.system_prompt = """You are an AAOIFI standards expert. Validate the proposed enhancements considering their Shariah assessment.
        Focus on practical applicability, consistency, and value addition.
        Provide an overall validation_result summary under a heading '## Overall Validation Summary'.
        Then, for each category of enhancement, provide an implementation_assessment under subheadings like '### Clarity Improvements Assessment'.
        Use the exact category names for the subheadings. Ensure substantial content for each.
        """
    def execute(self, enhancement_result: Dict[str, Any], shariah_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = enhancement_result.get("standard_name", "Unknown Standard")
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
            Standard Name: {standard_name}
            Proposed Enhancements (Full text): {enhancement_result.get('enhancement_proposals', 'N/A')[:2000]}...
            Shariah Assessment Summary: {shariah_result.get('shariah_assessment_summary', 'N/A')}
            Shariah Rulings per Category: {json.dumps(shariah_result.get('overall_ruling',{}), indent=2)}
            Please provide practical validation.
            """)
        ]
        validation_text = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "validation_full_text": validation_text,
            "validation_summary": self._extract_section(validation_text, "Overall Validation Summary", min_hashes=2) or validation_text, 
            "implementation_assessments": { 
                "clarity_improvements": self._extract_section(validation_text, "Clarity Improvements Assessment", min_hashes=3),
                "modern_adaptations": self._extract_section(validation_text, "Modern Adaptations Assessment", min_hashes=3),
                "tech_integration": self._extract_section(validation_text, "Tech Integration Assessment", min_hashes=3),
                "cross_references": self._extract_section(validation_text, "Cross References Assessment", min_hashes=3),
                "implementation_guidance": self._extract_section(validation_text, "Implementation Guidance Assessment", min_hashes=3),
            }
        }
        self.log_execution(f"Shariah assessment for {standard_name}", validation_text[:100], start_time)
        return result

# ReportGenerationAgent from MAI.py/FastAPI (adapted)
class ReportGenerationAgent(NewBaseAgent): 
    def __init__(self):
        super().__init__("Report Generation Agent", "Synthesizes findings into reports", "report", model_name=aicfg.GPT4_MODEL)
        self.system_prompt = """
        You are an expert report writer for Islamic finance standards. Synthesize findings into a comprehensive report.
        Use these Markdown headings: ## Executive Summary, ## Standard Analysis, ## Enhancement Recommendations, ## Validation Results, ## Implementation Roadmap, ## Appendices.
        Ensure substantial content under each.
        """
    def execute(self, review_result: Dict[str, Any], analysis_result: Dict[str, Any], enhancement_result: Dict[str, Any], shariah_result: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = review_result.get("standard_name", "Unknown Standard")
        # Construct detailed_input similar to MAI.py
        detailed_input = f"Standard Name: {standard_name}\n"
        detailed_input += f"Review Summary: {review_result.get('review_result', 'N/A')[:500]}...\n"
        detailed_input += f"Analysis Challenges: {analysis_result.get('challenges', 'N/A')}\n"
        detailed_input += f"Enhancement Proposals (Clarity): {enhancement_result.get('clarity_improvements', 'N/A')[:300]}...\n"
        detailed_input += f"Shariah Assessment: {shariah_result.get('shariah_assessment_summary', 'N/A')}\n"
        detailed_input += f"Validation Summary: {validation_result.get('validation_summary', 'N/A')}\n"
        # ... add more context as needed by the prompt
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=detailed_input + "\nPlease generate the report.")]
        report_text = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "full_report": report_text,
            "executive_summary": self._extract_section(report_text, "Executive Summary", min_hashes=2),
            "standard_analysis_section": self._extract_section(report_text, "Standard Analysis", min_hashes=2),
            "enhancement_recommendations_section": self._extract_section(report_text, "Enhancement Recommendations", min_hashes=2),
            "validation_results_section": self._extract_section(report_text, "Validation Results", min_hashes=2),
            "implementation_roadmap_section": self._extract_section(report_text, "Implementation Roadmap", min_hashes=2)
        }
        self.log_execution(f"Report generation for {standard_name}", report_text[:100], start_time)
        return result

# VisualizationAgent from MAI.py/FastAPI (adapted - generates SPECS)
class VisualizationAgent(NewBaseAgent): 
    def __init__(self):
        super().__init__("Visualization Agent", "Creates visual representations specifications", "visualization", model_name=aicfg.GPT35_MODEL) # Can be 3.5 for specs
        self.system_prompt = """
        You are an expert in data visualization. Design specifications for visualizations.
        Use these Markdown headings: ## Enhancement Impact Matrix, ## Shariah Compliance Visualization, ## Implementation Roadmap Timeline, ## Stakeholder Impact Analysis.
        For each: title, description, visualization type, key elements, data structure example, interpretation.
        """
    def execute(self, enhancement_result: Dict[str, Any], shariah_result: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        standard_name = enhancement_result.get("standard_name", "Unknown Standard")
        # Construct input_summary similar to MAI.py
        input_summary = f"Standard Name: {standard_name}\n"
        input_summary += f"Enhancements (clarity): {str(enhancement_result.get('clarity_improvements', 'N/A'))[:100]}...\n"
        input_summary += f"Shariah Rulings: {json.dumps(shariah_result.get('overall_ruling', {}))}\n"
        input_summary += f"Implementation Assessments (clarity): {str(validation_result.get('implementation_assessments', {}).get('clarity_improvements','N/A'))[:100]}...\n"
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=input_summary + "\nPlease generate visualization specifications.")]
        visualization_text = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "visualization_specifications_full_text": visualization_text,
            "enhancement_impact_matrix_spec": self._extract_section(visualization_text, "Enhancement Impact Matrix", min_hashes=2),
            "shariah_compliance_visualization_spec": self._extract_section(visualization_text, "Shariah Compliance Visualization", min_hashes=2),
            # ... other specs
        }
        self.log_execution(f"Visualization specs for {standard_name}", visualization_text[:100], start_time)
        return result

# FeedbackAgent from MAI.py/FastAPI (adapted)
class FeedbackAgent(NewBaseAgent): 
    def __init__(self):
        super().__init__("Feedback Agent", "Processes feedback and suggests refinements", "feedback", model_name=aicfg.GPT4_MODEL)
        self.system_prompt = """
        You are an expert facilitator for stakeholder feedback on Islamic finance standards. Process feedback and suggest refinements.
        Use these Markdown headings: ## Stakeholder Categories, ## Feedback Patterns and Themes, ## Feedback Validity Analysis, ## Recommended Refinements, ## Feedback Incorporation Process Suggestions.
        """
    def execute(self, feedback_text: str, enhancement_proposals_text: str, standard_name: str) -> Dict[str, Any]:
        start_time = time.time()
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
            Standard Name: {standard_name}
            Original Enhancement Proposals: {enhancement_proposals_text[:2000]}...
            Stakeholder Feedback: {feedback_text}
            Please analyze and suggest refinements.
            """)
        ]
        feedback_analysis = self._run_chain(messages)
        result = {
            "standard_name": standard_name,
            "feedback_analysis_full_text": feedback_analysis,
            "stakeholder_categories": self._extract_section(feedback_analysis, "Stakeholder Categories", min_hashes=2),
            "feedback_patterns": self._extract_section(feedback_analysis, "Feedback Patterns and Themes", min_hashes=2),
            "recommended_refinements": self._extract_section(feedback_analysis, "Recommended Refinements", min_hashes=2),
            # ... other sections
        }
        self.log_execution(f"Feedback for {standard_name}", feedback_analysis[:100], start_time)
        return result
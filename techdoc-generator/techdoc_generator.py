import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool  # Import BaseTool for custom tools
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import Field  # Import Field for tool parameter definition
import hashlib  # For generating unique filenames
import time  # For timestamps

# Load environment variables
load_dotenv()

# Configure API Keys
# Make sure to set these in your .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")

# Set ChromaDB OpenAI API key (same as OpenAI key)
os.environ["CHROMA_OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key
# Enable telemetry
os.environ["CREWAI_DISABLE_TELEMETRY"] = "false"

# Initialize the model and tools
# Set the model name to use OpenAI with appropriate rate limits
openai_model = "gpt-4o"  # Use a model with higher rate limits
print(f"Using OpenAI's {openai_model} model")

# Initialize LLM using OpenAI with options to reduce token usage
try:
    llm = LLM(
        model=openai_model,
        temperature=0.7,
        max_tokens=3000,  # Increased from 1000 to 3000
    )
    print("Successfully initialized OpenAI LLM with rate-limit friendly settings")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    raise

# Initialize search tool
search = DuckDuckGoSearchRun()

# Create a custom search tool using BaseTool
class SearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Useful for searching the web for current information."
    search_engine: DuckDuckGoSearchRun = Field(default_factory=lambda: DuckDuckGoSearchRun())

    def _run(self, query: str) -> str:
        """Execute the search query and return results"""
        try:
            return self.search_engine.run(query)
        except Exception as e:
            return f"Error performing search: {str(e)}"

search_tool = SearchTool()

# Global variable to store the output directory
output_directory = ""

# Custom Task class that saves output to a file when completed
class DocumentationTask(Task):
    def __init__(self, description, expected_output, agent, context=None, output_file=None):
        # Initialize the base Task class
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context,
            output_file=output_file  # Set CrewAI's native output file
        )

    def execute(self, *args, **kwargs):
        """Override execute to log progress and append to combined document."""
        task_name = self.description.split('for')[0].strip()
        print(f"\n🔄 Starting task: {task_name}")
        
        # Call the original execute method (which handles saving to self.output_file)
        result = super().execute(*args, **kwargs)
        
        # Convert result to string for consistent handling
        result_text = ""
        if hasattr(result, 'raw'):
            result_text = str(result.raw)
        elif hasattr(result, '__str__'):
            result_text = str(result)
        else:
            result_text = str(result)
            
        print(f"\n✅ Task completed: {task_name}")
        print(f"   Result length: {len(result_text)} characters")
        if self.output_file:
            print(f"   Individual output saved to: {self.output_file}")
        
        # Append the confirmed result string to the combined file
        if output_directory and result_text and self.output_file:
            try:
                combined_filepath = os.path.join(output_directory, "complete_documentation.md")
                with open(combined_filepath, "a", encoding="utf-8") as file:
                    # Add a header based on the intended filename (using self.output_file)
                    section_title = os.path.basename(self.output_file).replace('.md', '').replace('_', ' ').title()
                    file.write(f"\n\n## {section_title}\n\n")
                    file.write(result_text)
                print(f"   ✅ Appended output to {combined_filepath}")
            except Exception as e:
                print(f"   ⚠️ Error appending task output to combined file: {e}")
        else:
            print("   ⚠️ No output directory, result text, or output file path, skipping append to combined file")
        
        # Return the original result object or the string representation if needed elsewhere
        return result # Or potentially result_text depending on CrewAI needs

# Define agents with AI-optimized documentation roles
researcher = Agent(
    role="Technical Research Specialist",
    goal="Gather comprehensive, structured information on the technical topic to enable AI-compatible documentation",
    backstory="""You are a senior technical researcher with expertise in creating 
                AI-optimized knowledge bases. You excel at gathering detailed, 
                structured information that AI systems can easily parse and understand.""",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=llm
)

system_designer = Agent(
    role="System Design Architect",
    goal="Create detailed, explicit System Design Documents (SDDs) with consistent terminology and clear structure",
    backstory="""You are an experienced system architect who specializes in 
                creating comprehensive technical specifications optimized for AI systems. 
                You know how to organize information with explicit structure, 
                consistent terminology, and complete context.""",
    verbose=True,
    allow_delegation=False,
    tools=[],  # Empty tools list since this agent doesn't need search
    llm=llm
)

requirements_writer = Agent(
    role="Requirements Engineer",
    goal="Create detailed user stories and functional requirements with explicit criteria and edge cases",
    backstory="""You are a skilled requirements engineer who excels at creating 
                 question-oriented documentation frames around user needs. 
                 You're meticulous about defining explicit acceptance criteria 
                 and documenting edge cases.""",
    verbose=True,
    allow_delegation=False,
    tools=[],  # Empty tools list since this agent doesn't need search
    llm=llm
)

api_documentor = Agent(
    role="API Documentation Specialist",
    goal="Create comprehensive API documentation with examples, error handling, and endpoint specifications",
    backstory="""You are an expert in creating detailed API documentation that
                 includes complete endpoint specifications, authentication methods,
                 request/response examples, and error handling. Your documentation
                 is known for its clarity and completeness.""",
    verbose=True,
    allow_delegation=False,
    tools=[],  # Empty tools list since this agent doesn't need search
    llm=llm
)

diagram_creator = Agent(
    role="Technical Diagram Specialist",
    goal="Create clear, detailed diagrams and visual representations of system components and flows",
    backstory="""You are a visualization expert who can translate complex technical
                 concepts into clear diagrams, flowcharts, and sequence diagrams 
                 that enhance understanding of system architecture and flows.""",
    verbose=True,
    allow_delegation=False,
    tools=[],  # Empty tools list since this agent doesn't need search
    llm=llm
)

def create_technical_documentation(topic):
    print(f"\nInitiating AI-optimized documentation generation for: '{topic}'")
    print("Setting up specialized documentation agents and tasks...\n")
    
    # Define tasks for creating AI-optimized documentation, providing output file paths
    research_task = DocumentationTask(
        description=f"""Research for '{topic}' to create an AI-compatible knowledge base.
                      Focus on: technical details, architectures, best practices, and solutions.
                      Organize with clear headings, consistent terminology, and explicit relationships.""",
        expected_output="""A structured research report with clear sections, terminology,
                         relationships, specifications, and complete context.""",
        agent=researcher,
        output_file=os.path.join(output_directory, "research_findings.md")
    )
    
    system_design_task = DocumentationTask(
        description=f"""System for '{topic}' with:
                      Title, Executive Summary, Problem Statement, Architecture,
                      Components, Data Models, APIs, Integration Points, Requirements,
                      Implementation, and Alternatives.
                      
                      IMPORTANT: Start the document with exactly "# System Design Document".""",
        expected_output="""A System Design Document with all required sections,
                         component descriptions, and consistent terminology.""",
        agent=system_designer,
        context=[research_task],
        output_file=os.path.join(output_directory, "system_design_document.md")
    )
    
    requirements_task = DocumentationTask(
        description=f"""Requirements for '{topic}' with:
                      User Personas, User Stories (As a [user]...), Functional Requirements,
                      Non-Functional Requirements, Acceptance Criteria, and Edge Cases.
                      
                      IMPORTANT: Start the document with exactly "# User Stories and Requirements Document".""",
        expected_output="""A Requirements Document with clear personas, user stories,
                         requirements, acceptance criteria, and edge cases.""",
        agent=requirements_writer,
        context=[research_task],
        output_file=os.path.join(output_directory, "user_stories_and_requirements.md")
    )
    
    # Always create all tasks
    api_documentation_task = DocumentationTask(
        description=f"""API for '{topic}' with:
                      Endpoint Specifications, Authentication Methods, Request/Response Examples,
                      Error Handling, and Rate Limiting Information.
                      
                      IMPORTANT: Start the document with exactly "# API Documentation".""",
        expected_output="""API Documentation with endpoints, authentication,
                         sample requests/responses, and error handling.""",
        agent=api_documentor,
        context=[system_design_task, requirements_task],
        output_file=os.path.join(output_directory, "api_documentation.md")
    )
    
    diagrams_task = DocumentationTask(
        description=f"""Diagrams for '{topic}' including:
                      User Flow Diagrams, System Sequence Diagrams,
                      Decision Trees, and State Diagrams using Mermaid syntax.
                      
                      IMPORTANT: Start the document with exactly "# Technical Diagrams".""",
        expected_output="""A set of markdown/Mermaid diagrams showing user flows,
                         system sequences, decision trees, and state diagrams.""",
        agent=diagram_creator,
        context=[system_design_task, requirements_task],
        output_file=os.path.join(output_directory, "technical_diagrams.md")
    )
    
    # Create the crew with the AI-optimized documentation focused agents
    print("Assembling the AI-optimized documentation crew...\n")
    
    # Always use memory with OpenAI
    use_memory = True
    
    # Determine the process type - using parallel can help with rate limits
    # but sequential ensures more coherent documentation
    use_parallel = input("Would you like to run tasks in parallel to avoid rate limits? (y/n): ").lower() == 'y'
    process_type = Process.parallel if use_parallel else Process.sequential
    process_name = "parallel" if use_parallel else "sequential"
    print(f"\nUsing {process_name} processing mode...")
    
    # Always include all tasks and agents - never filter
    all_tasks = [research_task, system_design_task, requirements_task, api_documentation_task, diagrams_task]
    used_agents = [researcher, system_designer, requirements_writer, api_documentor, diagram_creator]
    
    # Create the crew with the regular Crew class
    print("\n🚀 Starting tasks with real-time output monitoring")
    crew = Crew(
        agents=used_agents,
        tasks=all_tasks,
        verbose=True,
        process=process_type,
        memory=use_memory
    )
    
    # Execute the crew's tasks
    print(f"Starting the AI-optimized documentation process for '{topic}'...\n")
    
    try:
        # Run the crew - individual file saving is handled by DocumentationTask
        result = crew.kickoff(inputs={"topic": topic})
        return result
    except Exception as e:
        if "RateLimitError" in str(e) or "rate limit" in str(e).lower():
            print("\n⚠️ Rate limit exceeded. Suggestions:")
            print("  - Try using parallel processing (answer 'y' to the parallel question)")
            print("  - Simplify your topic or make it more specific")
            print("  - Wait a few minutes before trying again")
            print("  - Consider upgrading your OpenAI API tier for higher rate limits")
        raise

def main():
    print("=" * 80)
    print("AI-OPTIMIZED TECHNICAL DOCUMENTATION GENERATOR".center(80))
    print(f"Powered by CrewAI with OpenAI's {openai_model} model".center(80))
    print("=" * 80)
    
    print("\nThis system creates comprehensive technical documentation optimized for AI coding assistants.")
    print("The documentation follows best practices for AI compatibility:")
    print("  - Comprehensive and detailed content")
    print("  - Consistent terminology")
    print("  - Explicit structure with clear headings")
    print("  - Question-oriented documentation")
    print("  - Clear examples and diagrams")
    
    topic = input("\nEnter the technical topic for your AI-optimized documentation: ")
    if not topic.strip():
        print("Error: Topic cannot be empty.")
        return
    
    # Create a safely named directory for the output files
    # Limit the directory name to a safe length (max 50 chars) to avoid file name too long errors
    safe_name = topic.replace(' ', '_').lower()
    if len(safe_name) > 50:
        # Create a truncated name with a hash for uniqueness
        hash_suffix = hashlib.md5(safe_name.encode()).hexdigest()[:8]
        safe_name = safe_name[:40] + "_" + hash_suffix  # 40 chars + 8 char hash + 1 underscore
    
    # Set the global output directory
    global output_directory
    output_directory = f"{safe_name}_ai_documentation"
    os.makedirs(output_directory, exist_ok=True)
    
    # Create log file to track progress
    log_filepath = os.path.join(output_directory, "generation_log.txt")
    with open(log_filepath, "w", encoding="utf-8") as logfile:
        logfile.write(f"Documentation generation started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        logfile.write(f"Topic: {topic}\n")
        logfile.write(f"Model: {openai_model}\n\n")
    
    print(f"\nOutput files will be saved to: {output_directory}")
    print(f"Progress is being logged to: {log_filepath}")
    print("\nGenerating AI-optimized technical documentation. This may take several minutes...\n")
    print("Each task's output will be saved as it completes.\n")
    
    try:
        # Create a combined file to store all outputs as well
        combined_filepath = os.path.join(output_directory, "complete_documentation.md")
        with open(combined_filepath, "w", encoding="utf-8") as file:
            file.write(f"# Complete Documentation for: {topic}\n\n")
            file.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write("---\n\n")
            file.write(f"## Table of Contents\n\n")
            file.write(f"1. Research findings\n")
            file.write(f"2. System Design Document\n")
            file.write(f"3. User Stories and Requirements\n")
            file.write(f"4. API Documentation\n")
            file.write(f"5. Technical Diagrams\n\n")
            file.write("---\n\n")
        
        # Log the creation of the file
        with open(log_filepath, "a", encoding="utf-8") as logfile:
            logfile.write(f"Created combined documentation file: {combined_filepath}\n")
        
        result = create_technical_documentation(topic)
        
        # Log completion
        with open(log_filepath, "a", encoding="utf-8") as logfile:
            logfile.write(f"\nDocumentation generation completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if result:
                if hasattr(result, 'raw'):
                    logfile.write(f"Final result size: {len(str(result.raw))} characters\n")
                else:
                    logfile.write(f"Final result size: {len(str(result))} characters\n")
        
        # Convert result to string if it's a CrewOutput object
        result_text = ""
        if hasattr(result, 'raw'):
            # New CrewAI versions return a CrewOutput object
            result_text = str(result.raw)
        elif hasattr(result, '__str__'):
            # Try to convert to string
            result_text = str(result)
        else:
            print("Warning: Result format is not as expected. Some features may not work.")
            result_text = "# Documentation\n\nUnable to extract documentation sections."
            
        # Log the file list
        with open(log_filepath, "a", encoding="utf-8") as logfile:
            logfile.write("\nGenerated files:\n")
            for filename in os.listdir(output_directory):
                file_path = os.path.join(output_directory, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    logfile.write(f"- {filename} ({file_size} bytes)\n")
        
        # List all the files that were created
        print("\nGenerated files:")
        for filename in os.listdir(output_directory):
            file_path = os.path.join(output_directory, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                print(f"- {filename} ({file_size} bytes)")
        
        print(f"\nSuccess! Your AI-optimized technical documentation has been saved to the '{output_directory}' directory.")
        print(f"Individual task outputs were saved as they completed.")
        print(f"The combined output is available in: {combined_filepath}")
        
        # Offer to view a summary
        view_choice = input("\nWould you like to see a summary of the documentation? (y/n): ")
        if view_choice.lower() == 'y':
            print("\n" + "=" * 80)
            print("DOCUMENTATION SUMMARY".center(80))
            print("=" * 80 + "\n")
            
            # Extract and display just the executive summary section
            executive_summary_start = result_text.find("## Executive Summary")
            if executive_summary_start != -1:
                next_section = result_text.find("##", executive_summary_start + 1)
                if next_section != -1:
                    executive_summary = result_text[executive_summary_start:next_section].strip()
                    print(executive_summary)
                else:
                    print("Executive summary not found in the generated documentation.")
            else:
                print("Executive summary not found in the generated documentation.")
            
            print("\nOpen the saved files to view the complete documentation.")
            
    except Exception as e:
        # Log the error
        with open(log_filepath, "a", encoding="utf-8") as logfile:
            logfile.write(f"\nError occurred: {e}\n")
            import traceback
            logfile.write(traceback.format_exc())
        
        print(f"\nAn error occurred: {e}")
        print(f"Error details have been logged to: {log_filepath}")
        print("Please check your API keys and internet connection and try again.")

if __name__ == "__main__":
    main()
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import json

class EnhancedFolderRAGChatbot:
    def __init__(self):
        # ... (previous init code remains the same)
        self.conversation_history = []
        self.session_start = datetime.now()
    
    def format_enhanced_response(self, result: Dict[str, Any], question: str) -> str:
        """Format response with enhanced structure and information"""
        
        if isinstance(result, str):
            # Handle error responses
            return f"❌ {result}"
        
        answer = result.get('answer', result.get('result', 'No answer provided'))
        sources = result.get('sources', result.get('source_documents', []))
        confidence = result.get('confidence_score', 0.5)
        metadata = result.get('metadata', {})
        
        # Start building the response
        response_parts = []
        
        # Confidence indicator
        confidence_emoji = self.get_confidence_emoji(confidence)
        response_parts.append(f"{confidence_emoji} **Answer** (Confidence: {confidence:.1%})")
        response_parts.append(answer)
        response_parts.append("")
        
        # Enhanced source information
        if sources:
            response_parts.append("📚 **Sources & Evidence**")
            response_parts.extend(self.format_sources_detailed(sources))
            response_parts.append("")
        
        # Processing insights
        if metadata.get('processing_notes'):
            response_parts.append("💡 **Insights**")
            for note in metadata['processing_notes']:
                response_parts.append(f"   • {note}")
            response_parts.append("")
        
        # Source diversity info
        if 'source_diversity' in result:
            diversity = result['source_diversity']
            response_parts.append(f"📊 **Knowledge Base Coverage**: {diversity['unique_files']} files, {len(diversity['file_types'])} file types")
            response_parts.append("")
        
        # Follow-up suggestions
        suggestions = self.generate_follow_up_suggestions(question, answer, sources)
        if suggestions:
            response_parts.append("🔍 **Suggested Follow-up Questions**")
            for suggestion in suggestions:
                response_parts.append(f"   • {suggestion}")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        if confidence >= 0.8:
            return "🎯"  # High confidence
        elif confidence >= 0.6:
            return "✅"  # Good confidence
        elif confidence >= 0.4:
            return "⚠️"   # Moderate confidence
        else:
            return "❓"  # Low confidence
    
    def format_sources_detailed(self, sources: List) -> List[str]:
        """Format sources with detailed information"""
        formatted_sources = []
        
        # Group sources by file
        sources_by_file = {}
        for i, source in enumerate(sources):
            if hasattr(source, 'metadata'):
                file_name = source.metadata.get('source_file', f'Source {i+1}')
                content = source.page_content
            else:
                file_name = source.get('file', f'Source {i+1}')
                content = source.get('content_preview', '')
            
            if file_name not in sources_by_file:
                sources_by_file[file_name] = []
            sources_by_file[file_name].append(content)
        
        # Format each file's sources
        for file_name, contents in sources_by_file.items():
            formatted_sources.append(f"   📄 **{file_name}**")
            for j, content in enumerate(contents):
                preview = content[:200] + "..." if len(content) > 200 else content
                formatted_sources.append(f"      └─ {preview}")
        
        return formatted_sources
    
    def generate_follow_up_suggestions(self, question: str, answer: str, sources: List) -> List[str]:
        """Generate contextual follow-up questions"""
        suggestions = []
        
        # Analyze the question type
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what', 'define', 'explain']):
            suggestions.append("How does this relate to other concepts in the documents?")
            suggestions.append("Can you provide more specific examples?")
        
        elif any(word in question_lower for word in ['how', 'process', 'steps']):
            suggestions.append("What are the prerequisites for this process?")
            suggestions.append("What could go wrong during this process?")
        
        elif any(word in question_lower for word in ['why', 'reason', 'cause']):
            suggestions.append("What are the implications of this?")
            suggestions.append("Are there alternative explanations?")
        
        # Add source-specific suggestions
        if sources:
            unique_files = set()
            for source in sources:
                if hasattr(source, 'metadata'):
                    file_name = source.metadata.get('source_file', '')
                else:
                    file_name = source.get('file', '')
                if file_name:
                    unique_files.add(file_name)
            
            if len(unique_files) > 1:
                suggestions.append("How do different sources compare on this topic?")
        
        # Limit to 3 most relevant suggestions
        return suggestions[:3]
    
    def get_enhanced_response(self, question: str) -> str:
        """Get enhanced response with comprehensive formatting"""
        if not self.qa_chain:
            return "❌ No knowledge base loaded. Please setup a knowledge base first."
        
        try:
            # Log the question
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'type': 'user'
            })
            
            # Get the raw result
            raw_result = self.qa_chain({"query": question})
            
            # Process with enhanced chain if available
            if hasattr(self.qa_chain, 'post_process_response'):
                processed_result = self.qa_chain.post_process_response(raw_result)
            else:
                # Fallback processing
                processed_result = self.basic_post_processing(raw_result)
            
            # Format the response
            formatted_response = self.format_enhanced_response(processed_result, question)
            
            # Log the response
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'response': formatted_response,
                'type': 'assistant'
            })
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"An error occurred while processing your question: {str(e)}"
            print(f"Debug - Error details: {e}")  # For debugging
            return f"❌ {error_msg}"
    
    def basic_post_processing(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Basic processing for standard RAG results"""
        answer = result.get('result', '')
        sources = result.get('source_documents', [])
        
        # Simple confidence calculation
        confidence = 0.7 if sources else 0.3
        if "don't have enough information" in answer.lower():
            confidence = 0.2
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence_score': confidence,
            'metadata': {
                'total_sources_found': len(sources),
                'processing_notes': []
            }
        }
    
    def enhanced_chat(self):
        """Enhanced chat session with better interaction"""
        if not self.qa_chain:
            print("❌ No knowledge base loaded.")
            return
        
        print(f"\n🚀 Enhanced RAG Chatbot - Knowledge Base: {self.current_kb}")
        print("=" * 70)
        print("💡 Ask questions about your documents")
        print("💡 I'll provide detailed answers with sources and confidence levels")
        print("💡 Type 'quit', 'exit', 'bye', 'help', or 'stats' for special commands")
        print("=" * 70 + "\n")
        
        while True:
            try:
                user_input = input("🧑 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    self.show_session_summary()
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                elif user_input.lower() == 'stats':
                    self.show_session_stats()
                    continue
                
                elif user_input.lower() == 'history':
                    self.show_conversation_history()
                    continue
                
                if not user_input:
                    print("❓ Please enter a question or type 'help' for assistance.")
                    continue
                
                print("\n🔍 Analyzing your question and searching knowledge base...")
                response = self.get_enhanced_response(user_input)
                print(f"\n{response}\n")
                print("═" * 70)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An unexpected error occurred: {str(e)}\n")
    
    def show_help(self):
        """Show help information"""
        help_text = """
🆘 **Help & Commands**

**Questions**: Ask anything about your documents
**Commands**:
   • help     - Show this help message
   • stats    - Show session statistics
   • history  - Show conversation history
   • quit/exit/bye - End session

**Tips for Better Results**:
   • Be specific in your questions
   • Ask follow-up questions for more details
   • Try different phrasings if results aren't satisfactory
   • Check the confidence levels in responses
        """
        print(help_text)
    
    def show_session_stats(self):
        """Show session statistics"""
        session_duration = datetime.now() - self.session_start
        user_questions = [h for h in self.conversation_history if h['type'] == 'user']
        
        print(f"\n📊 **Session Statistics**")
        print(f"   Duration: {str(session_duration).split('.')[0]}")
        print(f"   Questions asked: {len(user_questions)}")
        print(f"   Knowledge base: {self.current_kb}")
        print(f"   Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def show_conversation_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 **Conversation History**")
        print("-" * 50)
        
        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            timestamp = entry['timestamp'].split('T')[1].split('.')[0]  # Just time
            if entry['type'] == 'user':
                print(f"{i}. [{timestamp}] 🧑 {entry['question']}")
            else:
                # Show just first line of response
                first_line = entry['response'].split('\n')[0]
                print(f"   [{timestamp}] 🤖 {first_line}")
        print()
    
    def show_session_summary(self):
        """Show session summary before exit"""
        user_questions = [h for h in self.conversation_history if h['type'] == 'user']
        if user_questions:
            session_duration = datetime.now() - self.session_start
            print(f"\n📋 **Session Summary**")
            print(f"   Questions answered: {len(user_questions)}")
            print(f"   Session duration: {str(session_duration).split('.')[0]}")
            print(f"   Knowledge base used: {self.current_kb}")

# Update the main function to use enhanced chatbot
def main():
    try:
        chatbot = EnhancedFolderRAGChatbot()
        
        # Interactive setup (same as before)
        if chatbot.interactive_setup():
            chatbot.enhanced_chat()  # Use enhanced chat instead
            
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")

if __name__ == "__main__":
    main()